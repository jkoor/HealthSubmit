# -*- coding:utf-8 -*-
# Author: JKOR
"""健康系统自动填报"""

import os
import re
import time

import requests
import yagmail
import yaml
from bs4 import BeautifulSoup
from jinja2 import FileSystemLoader, Environment
from paddleocr import PaddleOCR


class HealthCondition:
    """登录并操作健康系统"""

    def __init__(self, account, password, email):
        """初始化参数"""
        # 读取config
        f_obj = open('config.yml', 'r', encoding='utf-8')
        config = yaml.safe_load(f_obj.read())
        config["parms"]["login_data"]["txtUid"] = account
        config["parms"]["login_data"]["txtPwd"] = password

        self.account = account  # 学号
        self.password = password  # 密码
        self.email = email  # 邮箱
        self.parms = config["parms"]  # 登录参数
        self.user_data = config["user_data"]  # 自定义提交表单
        self.temperature_data = config["temperature_data"]  # 体温提交表单
        self.submit_data = config["submit_data"]  # 健康系统提交表单
        self.temperature_flag = config["temperature_flag"]  # 是否进行体温填报
        self.max_retry_times = config["max_retry_times"]  # 填报失败重试次数
        self.session = requests.session()  # 创建session会话
        self.result = ''  # 填报结果
        self.email_result = None  # 邮件发送结果
        self.post_time = time.asctime(time.localtime(time.time()))  # 填报时间

    def submit_health_condition(self):
        """填报体温及健康系统"""
        self.login_health_web()  # 登录健康系统
        if self.result is True:
            if self.temperature_flag:  # 体温填报
                self.post_temperature_data()
            if self.result is True:
                self.get_submit_data()  # 获取待提交表单
                if self.result is True:
                    self.post_submit_data()  # 提交表单
                    if "重复" in self.result and self.max_retry_times > 0:  # 尝试次数过多则取消填报，返回填报失败
                        self.max_retry_times -= 1
                        self.submit_health_condition()

    def login_health_web(self):
        """登录健康填报模块"""

        r = self.session.post(url=self.parms["login_url"], headers=self.parms["login_header"],
                              data=self.parms["login_data"])
        # 返回登录结果
        soup = BeautifulSoup(r.text, 'lxml')
        a = soup.find(attrs={"type": "text/javascript"})
        try:
            if a.text[:10] == "layer.open":  # 登录失败
                pattern = re.compile(r"content: '(.*)', btn")
                self.result = re.findall(pattern, a.string)[0]
            else:  # 登录成功
                self.result = True
        except:
            self.result = "登录失败，请重试!"
        return self.result

    def post_temperature_data(self):
        """体温提交模块"""

        for t_data in self.temperature_data:
            r = self.session.post(url=self.parms["temperature_url"], data=t_data)
            soup = BeautifulSoup(r.text, 'lxml')
            a = soup.find(attrs={"type": "text/javascript"})
            try:
                pattern = re.compile(r"content: '(.*)', btn")
                t_data["result"] = re.findall(pattern, a.string)[0]
            except:
                t_data["result"] = "体温填报失败(提交失败)"
        return True

    def get_vccode(self):
        # 获取验证码
        r = self.session.get(self.parms["vccode_url"])
        with open(self.parms["vccode_save_path"], "wb") as f:
            f.write(r.content)

        # PalldeOCR识别
        ocr = PaddleOCR()
        result = ocr.ocr(self.parms["vccode_save_path"], det=False)

        # 验证识别结果
        try:
            result = result[0][0].replace(' ', '')
        except:
            return self.get_vccode()
        pattern = re.compile(r'[A-Za-z]{4}$')
        if pattern.match(result):
            return result
        else:
            return self.get_vccode()

    def get_submit_data(self):
        """获取所需填报信息模块"""

        r = self.session.get(url=self.parms["submit_data_url"])
        soup = BeautifulSoup(r.text, 'lxml')

        # 将获取到的信息添加到submit_data表单
        try:
            datas = [
                "StudentId", "Name", "Sex", "SpeType", "CollegeNo", "SpeGrade",
                "SpecialtyName", "ClassName", "MoveTel", "IdCard",
                "FaProvinceName", "FaCityName", "FaCountyName"
            ]
            for data in datas:
                a = soup.find(id=data)
                self.submit_data[data] = a["value"]
            # 设置当前所在地址与其家庭住址相同
            self.submit_data["ProvinceName"] = self.submit_data["FaProvinceName"]
            self.submit_data["CityName"] = self.submit_data["FaCityName"]
            self.submit_data["CountyName"] = self.submit_data["FaCountyName"]
            a = soup.find(class_="select-style required validate",
                          attrs={"name": "FaCounty"})
            self.submit_data["FaProvince"] = a["data-defaultvalue"][:2] + "0000"
            self.submit_data["FaCity"] = a["data-defaultvalue"][:4] + "00"
            self.submit_data["FaCounty"] = a["data-defaultvalue"]
            self.submit_data["Province"] = self.submit_data["FaProvince"]
            self.submit_data["City"] = self.submit_data["FaCity"]
            self.submit_data["County"] = self.submit_data["FaCounty"]
            a = soup.find(class_="required validate input-style",
                          attrs={"name": "FaComeWhere"})
            self.submit_data["FaComeWhere"] = a["value"]
            self.submit_data["ComeWhere"] = a["value"]
            a = soup.find(attrs={"name": "ReSubmiteFlag"})
            self.submit_data["ReSubmiteFlag"] = a["value"]

            for k, v in self.user_data.items():
                self.submit_data[k] = v
            self.result = True
        except:
            a = soup.find(attrs={"type": "text/javascript"})
            if a.text[:10] == "layer.open":
                pattern = re.compile(r"content: '(.*)', btn")
                self.result = re.findall(pattern, a.string)[0]  # 获取失败原因
            else:
                self.result = "填报失败(获取表单失败)"
        return self.result

    def post_submit_data(self):
        """提交信息表单模块"""

        self.submit_data["VCcode"] = self.get_vccode()
        # print(submit_data["VCcode"])
        r = self.session.post(url=self.parms["post_url"], data=self.submit_data)
        soup = BeautifulSoup(r.text, 'lxml')
        a = soup.find(attrs={"type": "text/javascript"})
        # a = """layer.open({content: '验证码已经过期，请重新输入！', btn: '确定', yes: function(index){history.back()}});"""
        try:
            pattern = re.compile(r"content: '(.*)', btn")
            result = re.findall(pattern, a.string)[0]
            if "验证码" in result:
                return self.post_submit_data()
            else:
                self.result = result
        except:
            self.result = "健康系统填报失败(提交失败)"
        return self.result

    def send_email(self):
        EMAIL_USER = 'abc@qq.com'
        EMAIL_PWD = '123456'
        # 链接邮箱服务器
        yag = yagmail.SMTP(user=EMAIL_USER,
                           password=EMAIL_PWD,
                           host='smtp.qq.com')

        subject = "健康系统填报: " + self.account + self.result

        env = Environment(loader=FileSystemLoader(os.path.abspath('.')))  # 创建一个包加载器对象
        template = env.get_template('template.html')  # 获取一个模板文件
        contents = template.render(account=self.account, temperature_data=self.temperature_data,
                                   submit_data=self.submit_data, post_time=self.post_time,
                                   temperature_flag=self.temperature_flag)  # 渲染

        try:
            yag.send(self.email, subject, contents)
            self.email_result = True
            return True
        except:
            self.email_result = False
            return False


