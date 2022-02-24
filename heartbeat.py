from srun import SrunClient
import socket
import logging
import base64
import getpass
import configparser
import os

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d [%(filename)s:%(lineno)d] %(message)s',
    datefmt='## %Y-%m-%d %H:%M:%S'
)
logging.getLogger("heartbeat").setLevel(logging.INFO)
logger = logging.getLogger("heartbeat")
class HeartBeat:
    USERNAME = ''
    PASSWD = ''

    CHECK_SERVER = 'www.baidu.com'

    def check_config(self):
        if os.path.exists("setting.ini"):
            return True
        return False

    def generate_config(self):
        config = configparser.ConfigParser()
        print('There is not setting file, please enter info below')
        print('If you want to retype info, delete setting file(setting.ini) you created before.')
        self.USERNAME = input('username: ')
        self.PASSWD = getpass.getpass('passwd: ')
        config['DEFAULT'] = {'username': self.USERNAME,
                            'passwd': str(base64.b64encode(self.PASSWD.encode('utf-8')), 'utf-8')}
        with open('setting.ini', 'w') as configfile:
            config.write(configfile)

    def read_config(self):
        config = configparser.ConfigParser()
        config.read('setting.ini')
        self.USERNAME = config['DEFAULT']['username']
        #PASSWD = config['DEFAULT']['passwd']
        self.PASSWD = str(base64.b64decode(config['DEFAULT']['passwd']), 'utf-8')


    def check_connect(self):
        with socket.socket() as s:
            s.settimeout(3)
            try:
                status = s.connect_ex((self.CHECK_SERVER, 443))
                return status == 0
            except Exception as e:
                print(e)
                return False

    def login(self):
        srun_client = SrunClient(print_log=False)
        # Use this method frequently to check online is not suggested!
        # if srun_client.check_online(): return
        logger.info('NOT ONLINE, TRY TO LOGIN!')
        srun_client.username = self.USERNAME
        srun_client.passwd = self.PASSWD
        srun_client.login()

    def check_online(self):
        if not self.check_config():
            self.generate_config()
        else:
            self.read_config()
        while not self.check_connect():
            self.login()



if __name__ == "__main__":
    HeartBeat().check_online()

#     import time
#     while 1:
#         check_online()
#         time.sleep(10)
