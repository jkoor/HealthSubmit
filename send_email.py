import yagmail


def send_result(result, submit_data, email, s_time, reg_flag):
    """发送填报结果至邮箱
    
    Args:
        result: 填报结果
        submit_data: 提交信息表单
        email: 收件人
        s_time: 健康系统填报时间
        reg_flag: 0为初次提交信息邮件, 1为每日填报邮件, 2为取消填报邮件
    Return:
        邮件发送结果，发送成功为True,失败为False
    """

    # 链接邮箱服务器
    yag = yagmail.SMTP(user="jkoor@qq.com",
                       password="nuycoijvbrknbfgc",
                       host='smtp.qq.com')
    # 邮件主题
    subject = "健康系统填报: " + result

    submit_info = [
        "您今天体温是否正常? : 是", "您今日是否处于中高风险地区? : 否",
        "和您共同居住的家庭成员是否有新冠肺炎确诊或疑似病例? : 否", "您是否正在进行集中隔离? : 否",
        "您是否今日解除集中隔离? : 否", "您是否正在进行居家隔离? : 否", "您今日是否进行了核酸检测? : 否",
        "您今日是否发生了所在地（跨地级市）异动变化? : 否", "您今日是否是确诊病例密切接触者? : 否",
        "您今日是否确诊为新冠肺炎病例? : 否", "您今日是否处于重点管控地区? : 否", "您今日是否处于重点关注地区? : 否"
    ]
    ending = [
        "------------------------------", "提交时间 : " + s_time,
        "若需取消自动填报可在网页重新填写学号密码，邮箱处填写[学号@密码.com]，提交即可",
        "如学号为1800010101, 密码为000000, 邮箱填写1800010101@000000.com即可取消填报",
        "以上信息为系统自动发送，请勿回复", "若有问题可发邮件至kiritor@qq.com", "---by jkor---"
    ]

    if reg_flag == 1:  # 每日填报推送
        datas = {
            "StudentId": "学号",
            "Name": "姓名",
            "ClassName": "班级",
            "MoveTel": "手机号",
            "ProvinceName": "所在省",
            "CityName": "所在市",
            "CountyName": "所在区/县",
            "ComeWhere": "所在地址",
            "FaProvinceName": "家庭所在省",
            "FaCityName": "家庭所在市",
            "FaCountyName": "家庭所在区/县",
            "FaComeWhere": "家庭所在地址",
        }
        beginning = [
            submit_data['StudentId'] + "今日所填报信息如下: (若已填报或登陆失败请忽略)",
            "------------------------------"
        ]
        for data, value in datas.items():
            beginning.append("%s : %s" % (value, submit_data[data]))

        contents = beginning + submit_info + ending

    elif reg_flag == 0:  # 初次注册提交
        beginning = [
            "提交成功，若信息无误，将于每日9点-10点填报", "届时填报结果将以邮件告知，若未收到邮件，请检查垃圾箱，是否被拦截。",
            "------------------------------", "当前所在地会按照家庭所在地填写, 其余信息将按如下填写: "
        ]
        contents = beginning + submit_info + ending
    elif reg_flag == 2:  # 取消自动填报
        subject = "健康系统填报: %s已取消自动填报" % result[:10]
        beginning = [result[:10] + "已取消自动填报！", "若需重新自动填报, 重新提交正常学号密码邮箱即可。"]
        contents = beginning + ending

    # 发送邮件
    try:
        yag.send(email, subject, contents)
        print("邮件发送成功")
        return True
    except:
        print("邮件发送失败")
        return False
