# -*- coding:utf-8 -*-
# Author: JKOR
"""健康系统自动填报"""

import json

from utils import HealthCondition

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':

    # 读取当前目录data.txt, 添加账号
    f_obj = open('stus_info_1.json', 'r')
    stus = json.loads(f_obj.read())

    for stu in stus:
        student = HealthCondition(stu["xh"], stu["pwd"], stu["email"])
        student.temperature_flag = False
        student.submit_health_condition()  # 健康系统及体温填报
        print(student.account, student.result)
        if student.temperature_flag:
            for t_data in student.temperature_data:
                print("体温填报：", t_data["result"])

        student.send_email()  # 发送邮件告知填报结果
