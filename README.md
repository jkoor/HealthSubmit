# 健康系统自动填报

[![健康系统自动填报](https://github.com/jkoor/HealthSubmit/actions/workflows/auto_submit.yml/badge.svg?branch=main)](https://github.com/jkoor/HealthSubmit/actions/workflows/auto_submit.yml)

利用GitHub Action实现沈阳理工大学学生健康情况自动填报

---

## 1. 特点

- 支持最近更新的验证码
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
├─ main.py  # 填报主程序
├─ requirements.txt  # 所需Python运行环境
└─ send_email.py  # 邮件发送程序
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

- ### main.py
  
  ```python
  result_info = submit_health_condition(STU_ID, STU_PWD)
  # STU_ID: 学号  STU_PWD: 密码
  # 返回值为填报结果
  # 每调用一次该函数会进行一次填报，可用该函数完成批量填报
  ```

- ### send_email.py
  
  ```python
  send_result(result_info, account, email)
  # result_info: 填报结果返回值  account: 学号  email: 接收邮箱
  # 返回值为发送邮件结果  True/False
  ```

- ### 示范
  
  ```python
  # 进行一次健康填报并发送邮件告知结果
  import main
  import send_email
  result_info = main.submit_health_condition('1805000000', '123456')
  print(result_info)
  send_result(result_info, '1805000000', 'abc@qq.com')
  ```

---

## 6. 欢迎交流

`邮箱` kiritor@qq.com

`Q  Q` 1737612906
