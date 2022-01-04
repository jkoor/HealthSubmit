# -*- coding:utf-8 -*-
# Author: JKOR
"""健康系统自动填报"""

import json
import time
import lxml
import send_email
import requests
from bs4 import BeautifulSoup

web_url = "http://xg.sylu.edu.cn/SPCP/Web/"  # 登录地址
accounts = {}   # 待填报账号字典

# 读取当前目录data.txt, 添加账号
with open('/opt/HealthSubmit/data.json', 'r') as f_obj:
    accounts = json.loads(f_obj.read())

# 待提交表单
submit_data = {
    "StudentId": "",
    "Name": "",
    "Sex": "",
    "SpeType": "",
    "CollegeNo": "",
    "SpeGrade": "",
    "SpecialtyName": "",
    "ClassName": "",
    "MoveTel": "",
    "Province": "",
    "City": "",
    "County": "2",
    "ComeWhere": "",
    "FaProvince": "",
    "FaCity": "",
    "FaCounty": "",
    "FaComeWhere": "",
    "radio_1": "e2f169d0-0778-4e3e-8ebf-64ce5a44f307",
    "radio_2": "c8ecb725-9788-4ed0-b9d2-4be23444ce3e",
    "text_1": "",
    "radio_3": "a884f81e-f401-451d-9f3d-0526aa886feb",
    "radio_4": "62ad9bed-3201-4607-b845-5e279a0311d0",
    "radio_5": "57722ddd-3093-4978-86da-1213420f36c4",
    "radio_6": "c6bcc8ce-86f1-404c-b7f8-ac583d899c75",
    "radio_7": "12727e9b-cd2f-413e-ae30-36adafd5203f",
    "radio_8": "e0559a52-d3d1-4203-ac9a-d221506a507f",
    "text_2": "",
    "radio_9": "c16d5a27-5923-43d8-b6a6-d5733803490b",
    "radio_10": "3a5fbe75-7bf4-4b6d-93f1-f561dbbf0ead",
    "radio_11": "3a36a22f-5af7-4b48-a472-7df55a8ba374",
    "radio_12": "8f1dddba-8bfc-4b06-8f9c-44a50d7c5ceb",
    "text_3": "",
    "radio_13": "51fac408-9d07-4a7a-9375-b1872c4ab0bd",
    "text_4": "",
    "Other": "",
    "GetAreaUrl": "/SPCP/Web/Report/GetArea",
    "IdCard": "",
    "ProvinceName": "",
    "CityName": "",
    "CountyName": "",
    "FaProvinceName": "",
    "FaCityName": "",
    "FaCountyName": "",
    "radioCount": "13",
    "checkboxCount": "0",
    "blackCount": "4",
    "PZData": """[{"OptionName": "是", "SelectId": "e2f169d0-0778-4e3e-8ebf-64ce5a44f307",
                "TitleId": "926853bd-6292-48ef-b554-0ea0cb99b808", "OptionType": "0"},
               {"OptionName": "否", "SelectId": "c8ecb725-9788-4ed0-b9d2-4be23444ce3e",
                "TitleId": "5c2ddaef-1cf4-4995-921c-de1585e71fe1", "OptionType": "0"},
               {"OptionName": "否", "SelectId": "a884f81e-f401-451d-9f3d-0526aa886feb",
                "TitleId": "6f95a926-c6d6-4fa7-9d74-fbcfcd79ec7b", "OptionType": "0"},
               {"OptionName": "否", "SelectId": "62ad9bed-3201-4607-b845-5e279a0311d0",
                "TitleId": "6cd479f3-dd6a-4bab-809a-3abdf28e5a46", "OptionType": "0"},
               {"OptionName": "否", "SelectId": "57722ddd-3093-4978-86da-1213420f36c4",
                "TitleId": "e6f578a6-6a0d-4b17-a18f-f1de3cb81d29", "OptionType": "0"},
               {"OptionName": "否", "SelectId": "c6bcc8ce-86f1-404c-b7f8-ac583d899c75",
                "TitleId": "23dfd17a-84b0-462c-a27d-fbafbe670278", "OptionType": "0"},
               {"OptionName": "否", "SelectId": "12727e9b-cd2f-413e-ae30-36adafd5203f",
                "TitleId": "0428ad6d-0c14-4c38-81fb-dc6928ae6608", "OptionType": "0"},
               {"OptionName": "否", "SelectId": "e0559a52-d3d1-4203-ac9a-d221506a507f",
                "TitleId": "85e00a79-176f-4fcf-8d14-8bb14075d51f", "OptionType": "0"},
               {"OptionName": "否", "SelectId": "c16d5a27-5923-43d8-b6a6-d5733803490b",
                "TitleId": "bd5a0708-79a3-4c92-a978-03aba2dac8a8", "OptionType": "0"},
               {"OptionName": "否", "SelectId": "3a5fbe75-7bf4-4b6d-93f1-f561dbbf0ead",
                "TitleId": "91d7f9a5-aed8-462f-81f5-9d339c3f2d3a", "OptionType": "0"},
               {"OptionName": "否", "SelectId": "3a36a22f-5af7-4b48-a472-7df55a8ba374",
                "TitleId": "025d0800-de7d-45e3-b2b4-c240bec5aa51", "OptionType": "0"},
               {"OptionName": "否", "SelectId": "8f1dddba-8bfc-4b06-8f9c-44a50d7c5ceb",
                "TitleId": "0827f0a0-60eb-4c62-9741-d742bf569ece", "OptionType": "0"},
               {"OptionName": "否", "SelectId": "51fac408-9d07-4a7a-9375-b1872c4ab0bd",
                "TitleId": "7d852786-1eca-4beb-82f2-9b52fd46ad6e", "OptionType": "0"}]""",
    "ReSubmiteFlag": ""
}


def login_web(account, password, url):
    """登录健康填报系统"""
    login_header = {
        "Host": "xg.sylu.edu.cn",
        "Origin": "http://xg.sylu.edu.cn",
        "Referer": "http://xg.sylu.edu.cn/SPCP/Web/",
    }
    data = {
        "StuLoginMode": "1",
        "txtUid": account,
        "txtPwd": password,
        "codeInput": "0000"
    }
    # 登录填报系统
    r = session.post(url=url, headers=login_header, data=data)
    soup = BeautifulSoup(r.text, 'lxml')
    a = soup.find(attrs={"type": "text/javascript"})
    # global result
    try:
        if a.text[:10] == "layer.open":
            result = account + (a.text[22:][:-54])
            return result
        else:
            # print(xh + "登录成功")
            return True
    except:
        result = account + "用户名或者密码错误，请重新输入!"
        return result


def get_private_data():
    """获取填报信息"""
    data_url = "http://xg.sylu.edu.cn/SPCP/Web/Report/Index"
    r = session.get(url=data_url)
    soup = BeautifulSoup(r.text, 'lxml')
    # global result
    try:
        # 将信息添加到submit_data表单
        datas = ["StudentId", "Name", "Sex", "SpeType", "CollegeNo", "SpeGrade", "SpecialtyName", "ClassName", "MoveTel", "IdCard",
                 "FaProvinceName", "FaCityName", "FaCountyName"]
        for data in datas:
            a = soup.find(id=data)
            submit_data[data] = a["value"]

        # 设置当前所在其与家庭住址相同
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
        # print(submit_data)
        return True
    except:
        a = soup.find(attrs={"type": "text/javascript"})
        if a.text[:10] == "layer.open":
            result = str(acc["xh"]) + (a.text[22:][:-92])
        else:
            result = str(acc["xh"]) + "填报失败"
        return result


def submit_healthcondition():
    """提交信息表单"""
    post_url = 'http://xg.sylu.edu.cn/SPCP/Web/Report/Index'
    post_header = {
        "Host": "xg.sylu.edu.cn",
        "Origin": "http://xg.sylu.edu.cn",
        "Referer": "http://xg.sylu.edu.cn/SPCP/Web/Report/Index",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/86.0.4240.198 Safari/537.36 "
    }
    # 提交表单，填报健康系统
    # global result
    try:
        r = session.post(url=post_url, headers=post_header, data=submit_data)
        soup = BeautifulSoup(r.text, 'lxml')
        a = soup.find(attrs={"type": "text/javascript"})
        if a.text[:10] == "layer.open":
            result = str(acc["xh"]) + (a.text[22:][:-92])
        else:
            result = str(acc["xh"]) + "填报失败，请重试"
        return result
    except:
        result = str(acc["xh"]) + "填报失败，请重试"
        return result


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    for acc in accounts:
        # 构造Session
        session = requests.session()

        # 若当前步骤失败，则不在往下进行
        result = login_web(str(acc["xh"]), str(acc["pwd"]), web_url)
        if result is True:
            result = get_private_data()
            if result is True:
                result = submit_healthcondition()
        submit_time = time.asctime(time.localtime(time.time()))
        print(submit_time)
        print(result)
        send_email.email_result(result, submit_data, acc["email"], submit_time)
        time.sleep(5)
