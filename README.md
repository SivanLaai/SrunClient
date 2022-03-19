# SrunClient
简易版深澜命令行客户端，包含登录登出和查询在线信息功能。支持 windows/Linux/?MacOS，python2/3 。 包含校园内网服务器反向代理教程。
# 增加内容：
- based on [SrunClient](https://github.com/ice-tong/SrunClient)
- 🍬1. 帐号、密码和ip保存于配置当中
- 🍬2. 密码在配置中做了加密处理，防止密码泄露
- 🍬3. 不再需要每次繁琐的设置密码，从配置中自动读取信息
- 🍬4. 把HearBeat抽象成类来管理，更加方便维护
- 🍬5. 可以设置深澜的ip地址了
# how to use
1. 生成setting.ini，不用在手动输入密码
    - 运行srun.py脚本
        ```shell
        [user@host SrunClient]$ python srun.py
        ############### Wellcome to Srun Client ###############
        Username:
        Ip:
        [1]: show online information
        [2]: set username and passwd
        [3]: login
        [4]: logout
        [5]: set srun_ip
        [h]: show this messages
        [q]: quit
        #######################################################
        >3
        There is not setting file, please enter info below
        If you want to retype info, delete setting file(setting.ini) you created before.
        username: test （输入帐号）
        passwd: ***（输入密码）
        srun_ip(authentation server ip): 124.16.1.1 （输入学校认证的网关ip）
        ```
        会生成setting.ini,并登录服务器，以后只需要```python heartbeat.py```就可以认证服务器，当然也可以设置成自动重连，详细看第2步

2. 掉线自动重连
    - 🍬**推荐**🍬 定时任务，定时执行heartbeat.py。
        使用crontba添加定时任务
        ```shell
        [user@host SrunClient]$ crontab -e
        ```
        将下列命令添加，按`esc`，输入`:wq`退出保存（每分钟执行一次命令）。
        ```
        * * * * * python /path/to/heartbeat.py
        ```
    - 或配合`nohup`使用，每隔10秒钟检测一次在线情况，不在线则重新登录。运行：
        ```shell
        nohup python heartbeat.py &
        ```
        `nohup` 进程有被杀死的风险

# addition

- [SSH反向代理 内网穿透](./sshr_readme.md)

# to do

- [ ] 定时下线
- [x] 更换ip
