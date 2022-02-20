# -*- coding:utf-8 -*-
# Author: JKOR
"""健康系统自动填报"""

import os

from utils import HealthCondition

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    STU_ID = os.environ['STU_ID']  # 学号
    STU_PWD = os.environ['STU_PWD']  # 密码
    STU_EMAIL = os.environ['STU_EMAIL']  # 邮箱

    student = HealthCondition(STU_ID, STU_PWD, STU_EMAIL)
    student.submit_health_condition()  # 健康系统及体温填报

    print(student.account, student.result, student.post_time)
    if student.temperature_flag:
        for t_data in student.temperature_data:
            print("体温填报：", t_data["result"])

    student.send_email()  # 发送邮件告知填报结果
