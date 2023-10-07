import time
import getpass
import configparser
import base64
import os

if bytes is str: input = raw_input

try:
    import requests

    def get_func(url, *args, **kwargs):
        resp = requests.get(url, *args, **kwargs)
        return resp.text

    def post_func(url, data, *args, **kwargs):
        resp = requests.post(url, data=data, *args, **kwargs)
        return resp.text

except ImportError:
    import urllib.request

    def get_func(url, *args, **kwargs):
        req = urllib.request.Request(url, *args, **kwargs)
        resp = urllib.request.urlopen(req)
        return resp.read().decode("utf-8")

    def post_func(url, data, *args, **kwargs):
        data_bytes = bytes(urllib.parse.urlencode(data), encoding='utf-8')
        req = urllib.request.Request(url, data=data_bytes, *args, **kwargs)
        resp = urllib.request.urlopen(req)
        return resp.read().decode("utf-8")


def time2date(timestamp):
    time_arry = time.localtime(int(timestamp))
    return time.strftime('%Y-%m-%d %H:%M:%S', time_arry)


def humanable_bytes(num_byte):
    num_byte = float(num_byte)
    num_GB, num_MB, num_KB = 0, 0, 0
    if num_byte >= 1024**3:
        num_GB = num_byte // (1024**3)
        num_byte -= num_GB * (1024**3)
    if num_byte >= 1024**2:
        num_MB = num_byte // (1024**2)
        num_byte -= num_MB * (1024**2)
    if num_byte >= 1024:
        num_KB = num_byte // 1024
        num_byte -= num_KB * 1024
    return '{} GB {} MB {} KB {} B'.format(num_GB, num_MB, num_KB, num_byte)


def humanable_bytes2(num_byte):
    num_byte = float(num_byte)
    if num_byte >= 1024**3:
        return '{:.2f} GB'.format(num_byte/(1024**3))
    elif num_byte >= 1024**2:
        return '{:.2f} MB'.format(num_byte/(1024**2))
    elif num_byte >= 1024**1:
        return '{:.2f} KB'.format(num_byte/(1024**1))


class SrunClient:

    name = 'UCAS'

    def __init__(self, username=None, passwd=None, print_log=True):
        setting_path = "setting.ini"
        self.username = ""
        self.passwd = ""
        self.srun_ip = ""
        if os.path.exists(setting_path):
            config = configparser.ConfigParser()
            config.read(setting_path)
            self.username = config['DEFAULT']['username']
            self.passwd = str(base64.b64decode(config['DEFAULT']['passwd']), 'utf-8')
            self.srun_ip = config['DEFAULT']['srun_ip']
        self.login_url = 'http://{}/cgi-bin/srun_portal'.format(self.srun_ip)
        #login_url = 'http://{}/srun_portal_pc'.format(srun_ip)
        self.online_url = 'http://{}/cgi-bin/rad_user_info'.format(self.srun_ip)
        # headers = {'User-Agent': 'SrunClient {}'.format(name)}
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.56'}
        self.print_log = print_log
        self.online_info = dict()
        #self.check_online()

    def _encrypt(self, passwd):
        column_key = [0,0,'d','c','j','i','h','g']
        row_key = [
            ['6','7','8','9',':',';','<','=','>','?','@','A','B','C','D','E'],
            ['?','>','A','@','C','B','E','D','7','6','9','8',';',':','=','<'],
            ['>','?','@','A','B','C','D','E','6','7','8','9',':',';','<','='],
            ['=','<',';',':','9','8','7','6','E','D','C','B','A','@','?','>'],
            ['<','=',':',';','8','9','6','7','D','E','B','C','@','A','>','?'],
            [';',':','=','<','7','6','9','8','C','B','E','D','?','>','A','@'],
            [':',';','<','=','6','7','8','9','B','C','D','E','>','?','@','A'],
            ['9','8','7','6','=','<',';',':','A','@','?','>','E','D','B','C'],
            ['8','9','6','7','<','=',':',';','@','A','>','?','D','E','B','C'],
            ['7','6','8','9',';',':','=','<','?','>','A','@','C','B','D','E'],
        ]
        encrypt_passwd = ''
        for idx, c in enumerate(passwd):
            char_c = column_key[ord(c) >> 4]
            char_r = row_key[idx%10][ord(c) & 0xf]
            if idx%2:
                encrypt_passwd += char_c + char_r
            else:
                encrypt_passwd += char_r + char_c
        return encrypt_passwd

    def _log(self, msg):
        if self.print_log:
            print('[SrunClient {}] {}'.format(self.name, msg))

    def check_config(self):
        if os.path.exists("setting.ini"):
            return True
        return False
    '''
    type : 2 - set username and passwd
           5 - set srun_ip
    '''
    def generate_config(self, type='2'):
        config = self.read_config()
        if not self.check_config():
            print('There is not setting file, please enter info below')
            print('If you want to retype info, delete setting file(setting.ini) you created before.')
            self.username = input('username: ')
            self.passwd = getpass.getpass('passwd: ')
            self.srun_ip = input('srun_ip(authentation server ip): ')
        elif type == '2':
            self.username = input('username: ')
            self.passwd = getpass.getpass('passwd: ')
        elif type == '5':
            self.srun_ip = input('srun_ip(authentation server ip): ')
        self.login_url = 'http://{}/cgi-bin/srun_portal'.format(self.srun_ip)
        self.online_url = 'http://{}/cgi-bin/rad_user_info'.format(self.srun_ip)
        config['DEFAULT'] = {'username': self.username,
                            'passwd': str(base64.b64encode(self.passwd.encode('utf-8')), 'utf-8'),
                            'srun_ip': self.srun_ip,
                            }
        with open('setting.ini', 'w') as configfile:
            config.write(configfile)

    def read_config(self):
        config = configparser.ConfigParser()
        if not self.check_config():
            return config
        config.read('setting.ini')
        if 'username' in config['DEFAULT']:
            self.username = config['DEFAULT']['username']
        if 'passwd' in config['DEFAULT']:
            self.passwd = str(base64.b64decode(config['DEFAULT']['passwd']), 'utf-8')
        if 'srun_ip' in config['DEFAULT']:
            self.srun_ip = config['DEFAULT']['srun_ip']
        return config

    def check_config(self):
        if os.path.exists("setting.ini"):
            return True
        return False

    def check_online_url(self):
        config = self.read_config()
        if not self.check_config():
            self.generate_config()
        if 'srun_ip' not in config['DEFAULT']:
            self.srun_ip = input('srun_ip(authentation server ip): ')
            self.login_url = 'http://{}/cgi-bin/srun_portal'.format(self.srun_ip)
            self.online_url = 'http://{}/cgi-bin/rad_user_info'.format(self.srun_ip)

    def check_online(self):
        resp_text = get_func(self.online_url, headers=self.headers)
        if 'not_online' in resp_text:
            self._log('###*** NOT ONLINE! ***###')
            return False
        try:
            items = resp_text.split(',')
            self.online_info = {
                'online':True, 'username':items[0],
                'login_time':items[1], 'now_time':items[2],
                'used_bytes':items[6], 'used_second':items[7],
                'ip':items[8], 'balance':items[11],
                'auth_server_version':items[21]
                }
            return True
        except Exception as e:
            print(resp_text)
            print('Catch `Status Internal Server Error`? The request is frequent!')
            print(e)

    def show_online(self):
        if not self.check_online(): return
        self._log('###*** ONLINE INFORMATION! ***###')
        header = '================== ONLIN INFORMATION =================='
        print(header)
        print('Username: {}'.format(self.online_info['username']))
        print('Login time: {}'.format(time2date(self.online_info['login_time'])))
        print('Now time: {}'.format(time2date(self.online_info['now_time'])))
        print('Used data: {}'.format(humanable_bytes(self.online_info['used_bytes'])))
        print('Ip: {}'.format(self.online_info['ip']))
        print('Balance: {}'.format(self.online_info['balance']))
        print('=' * len(header))

    def login(self):
        curr_try = 1
        MAX_TRY = 2
        while curr_try <= MAX_TRY:
            if not self.check_config():
                self.generate_config()
            if self.check_online():
                self._log('###*** ALREADY ONLINE! ***###')
                return True
            if not self.username or not self.passwd:
                self._log('###*** LOGIN FAILED! (username or passwd is None) ***###')
                self._log('username and passwd are required! (check username and passwd)')
            encrypt_passwd = self._encrypt(self.passwd)
            payload = {
                'action': 'login',
                'username': self.username,
                'password': encrypt_passwd,
                'type': 2, 'n': 117,
                'drop': 0, 'pop': 0,
                'mbytes': 0, 'minutes': 0,
                'ac_id': 1
                }
            resp_text = post_func(self.login_url, data=payload, headers=self.headers)
            if 'login_ok' in resp_text:
                self._log('###*** LOGIN SUCCESS! ***###')
                self._log(resp_text)
                self.show_online()
            elif 'login_error' in resp_text:
                self._log('###*** LOGIN FAILED! (login error)***###')
                self._log(resp_text)
            else:
                self._log('###*** LOGIN FAILED! (unknown error) ***###')
                self._log(resp_text)
            curr_try += 1
            self.login_url = 'https://{}/cgi-bin/srun_portal'.format(self.srun_ip)
            self.online_url = 'https://{}/cgi-bin/rad_user_info'.format(self.srun_ip)
            self._log('###***HTTP LOGIN FAILED! (try to login by HTTPS)***###')

    def logout(self):
        if not self.check_online(): return True
        payload = {
            'action': 'logout',
            'ac_id': 1,
            'username': self.online_info['username'],
            'type': 2
            }
        resp_text = post_func(self.login_url, data=payload, headers=self.headers)
        if 'logout_ok' in resp_text:
            self._log('###*** LOGOUT SUCCESS! ***###')
            return True
        elif 'login_error' in resp_text:
            self._log('###*** LOGOUT FAILED! (login error) ***###')
            self._log(resp_text)
            return False
        else:
            self._log('###*** LOGOUT FAILED! (unknown error) ***###')
            self._log(resp_text)
            return False


    def show_commands(self):
        wellcome = '############### Wellcome to Srun Client ###############'
        print(wellcome)
        print('Username: {}'.format(self.username))
        print('Ip: {}'.format(self.srun_ip))
        print('[1]: show online information')
        print('[2]: set username and passwd')
        print('[3]: login')
        print('[4]: logout')
        print('[5]: set srun_ip')
        print('[h]: show this messages')
        print('[q]: quit')
        print('#' * len(wellcome))


if __name__ == "__main__":
    srun_client = SrunClient()
    srun_client.show_commands()
    #srun_client.show_online()
    command = '_'
    while command != 'q':
        command = input('>')
        if command == '1':
            srun_client.show_online()
        elif command == '2':
            #srun_client.username = input('username: ')
            #srun_client.passwd = getpass.getpass('passwd: ')
            srun_client.generate_config(command)
        elif command == '3':
            srun_client.login()
        elif command == '4':
            srun_client.logout()
        elif command == '5':
            srun_client.generate_config(command)
        elif command == 'h':
            srun_client.show_commands()
        elif command == 'q':
            print('bye!')
        else:
            print('unknown command!')
