from srun import SrunClient
import socket
import logging

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d [%(filename)s:%(lineno)d] %(message)s',
    datefmt='## %Y-%m-%d %H:%M:%S'
)
logging.getLogger("heartbeat").setLevel(logging.INFO)
logger = logging.getLogger("heartbeat")
class HeartBeat:

    CHECK_SERVER = 'www.baidu.com'

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
        #srun_client = SrunClient(print_log=False)
        srun_client = SrunClient()
        # Use this method frequently to check online is not suggested!
        # if srun_client.check_online(): return
        logger.info('NOT ONLINE, TRY TO LOGIN!')
        srun_client.login()

    def check_online(self):
        while not self.check_connect():
            self.login()



if __name__ == "__main__":
    HeartBeat().check_online()

#     import time
#     while 1:
#         check_online()
#         time.sleep(10)
