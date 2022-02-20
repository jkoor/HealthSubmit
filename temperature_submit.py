# -*- coding:utf-8 -*-
# Author: JKOR
"""健康系统自动填报"""

import os
import re

import requests
import yaml
from bs4 import BeautifulSoup


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


def post_temperature(session, parms, temperature):
    """体温提交模块"""

    r = session.post(url=parms["temperature_url"], data=temperature)
    soup = BeautifulSoup(r.text, 'lxml')
    a = soup.find(attrs={"type": "text/javascript"})
    try:
        pattern = re.compile(r"content: '(.*)', btn")
        result = temperature["TimeNowHour"] + ':' + temperature["TimeNowMinute"] + '  ' + temperature["Temper1"] + '.' + \
                 temperature["Temper2"] + '℃  '
        result += re.findall(pattern, a.string)[0]
        print(result)
        return result
    except:
        return "体温填报失败(提交失败)"


def submit_temperature(account, password):
    """体温填报

    Args:
        account: 学号
        password: 密码
    Return:
        result_info字典，包含提交结果，提交时间，提交数据
    """

    # 读取config
    f_obj = open('config.yml', 'r', encoding='utf-8')
    config = yaml.safe_load(f_obj.read())
    parms = config["parms"]
    temperature_data = config["temperature_data"]
    parms["login_data"]["txtUid"] = account
    parms["login_data"]["txtPwd"] = password

    # 构造Session
    session = requests.session()

    # 若当前步骤失败，则不在往下进行
    result = login_health_web(session, parms)
    if result is True:
        temperature_result = []
        for temperature in temperature_data:
            result = post_temperature(session, parms, temperature)
            temperature_result.append(result)

    return temperature_result


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    STU_ID = os.environ['STU_ID']  # 学号
    STU_PWD = os.environ['STU_PWD']  # 密码
    STU_EMAIL = os.environ['STU_EMAIL']  # 邮箱

    # 体温填报
    temperature_result = submit_temperature(STU_ID, STU_PWD)
    print(temperature_result)
