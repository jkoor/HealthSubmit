import yagmail


def send_result(result_info, account, email, reg_flag=0):
    """发送填报结果至邮箱

    Args:
        result_info: 填报信息
        account: 学号
        email: 收件人
        reg_flag: 1为初次提交信息邮件, 0为每日填报邮件, -1为取消填报邮件
    Return:
        邮件发送结果，发送成功为True,失败为False
    """

    # 链接邮箱服务器
    yag = yagmail.SMTP(user="example@qq.com",
                       password="*******",
                       host='smtp.qq.com')

    # 邮件主题
    subject = "健康系统填报: " + account + result_info["result"]

    # 邮件正文
    submit_info = [
        "------------------------------",
        "您今天体温是否正常? : 是",
        "您今日是否处于中高风险地区? : 否",
        "和您共同居住的家庭成员是否有新冠肺炎确诊或疑似病例? : 否",
        "您是否正在进行集中隔离? : 否",
        "您是否今日解除集中隔离? : 否",
        "您是否正在进行居家隔离? : 否",
        "您今日是否进行了核酸检测? : 否",
        "您今日是否发生了所在地（跨地级市）异动变化? : 否",
        "您今日是否是确诊病例密切接触者? : 否",
        "您今日是否确诊为新冠肺炎病例? : 否",
        "您今日是否处于重点管控地区? : 否",
        "您今日是否处于重点关注地区? : 否"
    ]
    if reg_flag == 0:  # 每日填报推送
        submit_data = result_info["submit_data"]
        beginning = [
            account + "今日所填报信息如下: (若已填报或填报失败请忽略)",
            "------------------------------",
            "姓名: " + submit_data["Name"],
            "班级: " + submit_data["ClassName"],
            "手机号: " + submit_data["MoveTel"],
            "当前所在地: " + submit_data["ProvinceName"] + submit_data["CityName"] + submit_data["CountyName"] + submit_data["ComeWhere"],
            "家庭所在地: " + submit_data["FaProvinceName"] + submit_data["FaCityName"] + submit_data["FaCountyName"] + submit_data["FaComeWhere"]
        ]
        beginning += submit_info
    elif reg_flag == 1:  # 初次注册提交
        beginning = [
            "若信息无误, 将于每日9点-10点填报, 届时填报结果将以邮件告知",
            "------------------------------",
            "当前所在地会按照家庭所在地填写, 其余信息将按如下填写: "
        ]
        try:
            beginning += ["------------------------------", "每日体温填报: "]
            beginning += result_info["temperature_result"]
        except:
            pass
        beginning += submit_info
    elif reg_flag == -1:  # 取消自动填报
        subject = "健康系统填报: %s已取消自动填报" % account
        beginning = ["若需重新填报, 重新提交学号密码邮箱即可。"]

    ending = [
        "------------------------------",
        "提交时间 : " + result_info["post_time"],
        "重填学号密码，邮箱填写[cancel@cancel.com]可取消填报",
        "网址: http://101.43.133.188:5000",
        "反馈邮箱: kiritor@qq.com",
        "---by jkor---"
    ]
    contents = beginning + ending

    # 发送邮件
    try:
        yag.send(email, subject, contents)
        return True
    except:
        return False
