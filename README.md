# 健康系统自动填报

[![健康系统自动填报](https://github.com/jkoor/HealthSubmit/actions/workflows/auto_submit.yml/badge.svg?branch=main)](https://github.com/jkoor/HealthSubmit/actions/workflows/auto_submit.yml)

利用GitHub Action实现沈阳理工大学学生健康情况自动填报

---

## 1. 特点

- 支持最近更新的验证码
- 支持每日三次体温填报
- 利用GitHub Action，无需搭建服务器
- 可自定义提交表单, 如当前所在地等
- 无第三方介入，无需担心隐私问题
  
```txt
文件目录
HealthSubmit
├─ .github
│    └─ workflows
│           └─ auto_submit.yml  # GitHub Action配置文件
├─ config.yml  # 项目配置文件
├─ main.py  # 主程序
├─ requirements.txt  # 所需Python运行环境
├─ template.html  # 邮件发送模板
└─ uilts.py  # 登录填报函数
```

---

## 2. 开始使用

1. `Fork` 项目
2. 打开 Fork 项目，进入项目设置 Settings - Security - Secrets - Actions
3. 添加如下五个键值

   ```yaml
   STU_ID: 1805000000  # 学号
   STU_PWD: 000000  # 密码
   STU_EMAIL: abc@qq.com  # 填报结果接收方邮箱
   EMAIL_USER: abc@qq.com  # 填报结果发送方邮箱，仅支持QQ邮箱，可与接收方相同
   EMAIL_PWD: 123456789  # 填报结果发送方邮箱密码，并开启POP3协议
   ```

   ![Serects](https://s3.bmp.ovh/imgs/2022/01/b772dd26b98ee7b7.png)

4. 请先点击项目右上角 `☆Star`进行填报测试，运行时间约 **3min**，将以邮件告知填报结果
5. 将于每日 9 点自动进行健康填报

---

## 3. 注意事项

- 五个键值必须填写，邮箱密码错误不会发送邮件，但填报正常
- 若不需要体温填报功能，请在config.yml更改

```ymal
  temperature_flag: False  # 取消体温填报
```

- 程序运行情况可进 `Action` 查看
  ![运行结果](https://s3.bmp.ovh/imgs/2022/01/16d8c7bdebf6ffdc.png)
- 每点击一次项目右上角 `☆Star`便会运行一次
- 如若更改每日填报时间，可更改 `auto_submit.yml`

```ymal
...
on:
  schedule:
  # UTC标准时间，为北京时间减8h，如北京时间上午9:00为UTC 1:00
   - cron: 58 1 * * *  # 北京时间每日9:58填报
  watch:
    types: [started]
...
```

- 需要自定义表单，请在config.yml中添加

```ymal
...
user_data: # 用户自定义提交表单，变量需与submit_data中变量相同
  blackCount: '4'
...
```

---

## 4. 其他

不想折腾？ 那就试试这个吧

填写学号、密码、邮箱即可，每日自动填报

不过，这就与前面所说的没有第三方介入背道而驰了🤭

`Demo` [http://101.43.133.188:5000/](http://101.43.133.188:5000/)

---

## 5. 说明文档

- ### 安装运行环境
  
  ```powershell
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
  ```

- ### uilts.py
  
  ```python
  student = HealthCondition(account, password, email)  # 调用主类
  student.submit_health_condition()  # 每调用一次该函数会进行一次填报，可用该函数完成批量填报
  student.send_email()  # 邮件告知填报结果
  student.result  # 健康系统填报结果
  student.submit_data  # 健康系统提交表单
  student.temperature_data  # 体温提交表单
  student.post_time  # 提交时间
  # 其余函数及参数请查看uilts.py
  ```

- ### 示范
  
  ```python
  # 进行一次健康填报并发送邮件告知结果
  from uilts import HealthCondition
  student = HealthCondition("1805000000", "000000", "abc@qq.com")  # 创建类
  student.submit_health_condition()  # 健康系统填报
  student.send_email()  # 邮件告知填报结果
  print(student.account)
  print(student.result)
  print(student.submit_data)
  print(student.temperature_data)
  print(student.post_time)
  ```

---

## 6. 欢迎交流

`邮箱` kiritor@qq.com

`Q  Q` 1737612906
