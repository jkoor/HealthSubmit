# -*- coding:utf-8 -*-
# Author: JKOR
"""健康系统自动填报"""

import json
import re
import time

import requests
import yaml
from bs4 import BeautifulSoup
from paddleocr import PaddleOCR

import send_email


def login_health_web(session, parms):
    """登录健康填报模块"""

    r = session.post(url=parms["login_url"], headers=parms["login_header"], data=parms["login_data"])

    # 返回登录结果
    soup = BeautifulSoup(r.text, 'lxml')
    a = soup.find(attrs={"type": "text/javascript"})
    # print(a.text)
    try:
        if a.text[:10] == "layer.open":  # 登录失败
            pattern = re.compile(r"content: '(.*)', btn")
            return re.findall(pattern, a.string)[0]
        else:  # 登录成功
            return True
    except:
        return "登录失败，请重试!"


def get_vccode(session, parms):
    # 获取验证码
    r = session.get(parms["vccode_url"])
    with open(parms["vccode_save_path"], "wb") as f:
        f.write(r.content)

    # PalldeOCR识别
    ocr = PaddleOCR()
    result = ocr.ocr(parms["vccode_save_path"], det=False)

    # 验证识别结果
    try:
        result = result[0][0].replace(' ', '')
    except:
        return get_vccode(session, parms)
    pattern = re.compile(r'[A-Za-z]{4}$')
    if pattern.match(result):
        return result
    else:
        return get_vccode(session, parms)


def get_submit_data(session, parms, submit_data):
    """获取所需填报信息模块"""

    r = session.get(url=parms["submit_data_url"])
    soup = BeautifulSoup(r.text, 'lxml')

    # 将获取到的信息添加到submit_data表单
    try:
        datas = ["StudentId", "Name", "Sex", "SpeType", "CollegeNo", "SpeGrade", "SpecialtyName", "ClassName",
                 "MoveTel", "IdCard",
                 "FaProvinceName", "FaCityName", "FaCountyName"]
        for data in datas:
            a = soup.find(id=data)
            submit_data[data] = a["value"]
        # 设置当前所在地址与其家庭住址相同
        submit_data["ProvinceName"] = submit_data["FaProvinceName"]
        submit_data["CityName"] = submit_data["FaCityName"]
        submit_data["CountyName"] = submit_data["FaCountyName"]
        a = soup.find(class_="select-style required validate", attrs={"name": "FaCounty"})
        submit_data["FaProvince"] = a["data-defaultvalue"][:2] + "0000"
        submit_data["FaCity"] = a["data-defaultvalue"][:4] + "00"
        submit_data["FaCounty"] = a["data-defaultvalue"]
        submit_data["Province"] = submit_data["FaProvince"]
        submit_data["City"] = submit_data["FaCity"]
        submit_data["County"] = submit_data["FaCounty"]
        a = soup.find(class_="required validate input-style", attrs={"name": "FaComeWhere"})
        submit_data["FaComeWhere"] = a["value"]
        submit_data["ComeWhere"] = a["value"]
        a = soup.find(attrs={"name": "ReSubmiteFlag"})
        submit_data["ReSubmiteFlag"] = a["value"]
        return True  # 获取成功
    except:
        a = soup.find(attrs={"type": "text/javascript"})
        if a.text[:10] == "layer.open":
            pattern = re.compile(r"content: '(.*)', btn")
            return re.findall(pattern, a.string)[0]  # 获取失败原因
        else:
            return "填报失败"


def post_submit_data(session, parms, submit_data):
    """提交信息表单模块"""

    # 提交表单，填报健康系统
    submit_data["VCcode"] = get_vccode(session, parms)
    print(submit_data["VCcode"])
    r = session.post(url=parms["post_url"], data=submit_data)
    soup = BeautifulSoup(r.text, 'lxml')
    a = soup.find(attrs={"type": "text/javascript"})
    # a = """layer.open({content: '验证码已经过期，请重新输入！', btn: '确定', yes: function(index){history.back()}});"""
    try:
        pattern = re.compile(r"content: '(.*)', btn")
        result = re.findall(pattern, a.string)[0]
        if "验证码" in result:
            return post_submit_data(session, parms, submit_data)
        else:
            return result
    except:
        return "填报失败，请重试"


def submit_health_condition(account, password):
    """登录并填报健康系统"""

    # 读取config
    f_obj = open('config.yml', 'r', encoding='utf-8')
    config = yaml.safe_load(f_obj.read())
    parms = config["parms"]
    submit_data = config["submit_data"]
    parms["login_data"]["txtUid"] = account
    parms["login_data"]["txtPwd"] = password

    # 构造Session
    session = requests.session()

    retry_times = 0  # 提交失败重试次数
    # 若当前步骤失败，则不在往下进行
    result = login_health_web(session, parms)
    if result is True:
        result = get_submit_data(session, parms, submit_data)
        if result is True:
            result = post_submit_data(session, parms, submit_data)
            if "重复提交" in result and retry_times <= config["max_retry_times"]:  # 尝试次数过多则取消填报，返回填报失败
                retry_times += 1
                submit_health_condition(account, password)

    post_time = time.asctime(time.localtime(time.time()))  # 填报时间
    print(account, password, result, post_time)
    result_info = {"result": result, "post_time": post_time, "submit_data": submit_data}
    return result_info


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    # submit_health_condition("1805030317", "182216")

    # with open('data.txt', 'r') as f_obj:
    #     for line in f_obj:
    #         account = line[:10]
    #         password = line[-7:-1]
    #         submit_health_condition(account, password)

    # 读取当前目录data.txt, 添加账号
    f_obj = open('stus_info.json', 'r')
    stus = json.loads(f_obj.read())
    # 批量填报
    for stu in stus:
        result_info = submit_health_condition(stu["xh"], stu["pwd"])
        # 邮件告知填报结果
        send_email.send_result(result_info, stu["xh"], stu["email"])
        time.sleep(3)
