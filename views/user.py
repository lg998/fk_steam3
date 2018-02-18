import requests
import json
import rsa
import base64
import time
from enum import Enum
from views.common import *
from settings import *
from requests.adapters import HTTPAdapter
from views.db import *



LOGIN_STATE = Enum('LOGIN_STATE', ('INIT', 'NEED_TWOFACTOR_CODE', 'SUCCESS', 'FAIL'))

class User:
    login_state = LOGIN_STATE.INIT
    username = ""
    password = ""
    encrypted_password  = ""
    timestamp = ""
    cookie_file_name = ""
    session = requests.Session()
    orders = {}
    #TODO 对于有cookie保存的用户是没有密码验证的，不安全
    def __init__(self, username, password = 'not exist'):
        self.username = username
        self.password = password
        self.cookie_file_name = self.username+"_cookies"
        request_retry = HTTPAdapter(max_retries = REQUEST_RETRY_TIMES)
        self.session.mount('https://', request_retry)
        self.session.mount('http://', request_retry)
        self.login_to_steam()



    def login_to_steam(self):
        if load_cookies(self.session, self.cookie_file_name):
            logging.debug("Use cookie to login")
            self.login_state = LOGIN_STATE.SUCCESS
            # user_login(self.username)
        else:
            logging.debug ("Use username and password to login")
            logging.debug ("getting rsa key")
            key_mod, key_exp, self.timestamp = self.get_rsa_key()
            logging.debug ("encrypting password")
            self.encrypted_password = self.encrypt_password(key_mod, key_exp, self.password)
            self.login_state = LOGIN_STATE.NEED_TWOFACTOR_CODE


    def continue_login(self, twofactorcode):
        print("sending login post")
        if not self.send_login_post(self.encrypted_password, twofactorcode, self.timestamp):
            return False
        # user_login(self.username)
        save_cookies(self.session, self.cookie_file_name)
        return True

    def get_rsa_key(self):
        rsa_res = json.loads(self.session.post(getrsa_url, {'username': self.username}).content)
        token_gid = rsa_res["token_gid"]
        timestamp = rsa_res["timestamp"]
        key_mod = rsa_res["publickey_mod"]
        key_exp = rsa_res["publickey_exp"]
        logging.info("rsa key info: ")
        for each in rsa_res:
            logging.info("%s %s" % (each, rsa_res[each]))
        return key_mod, key_exp, timestamp

    def encrypt_password(self, key_mod, key_exp, password):
        rsa_mod = int(key_mod, 16)
        rsa_exp = int(key_exp, 16)
        return base64.b64encode(rsa.encrypt(password.encode('utf-8'), rsa.PublicKey(rsa_mod, rsa_exp)))

    def send_login_post(self, encrypted_password, twofactorcode, timestamp):
        request_data = {
            'password': encrypted_password,
            'username': self.username,
            'twofactorcode': twofactorcode,
            'emailauth': '',
            'loginfriendlyname': '',
            'captchagid': '-1',
            'captcha_text': '',
            'emailsteamid': '',
            'rsatimestamp': timestamp,
            'remember_login': 'true',
            'donotcache': str(int(time.time() * 1000))
        }
        logging.info(request_data)
        login_res = json.loads(self.session.post(login_url, request_data).content)
        logging.info("login result: ")
        for each in login_res:
            logging.info("%s %s" % (each, login_res[each]))
        if login_res['success'] == False:
            self.login_state = LOGIN_STATE.FAIL
            return False
        #transfer_urls
        parameters = login_res.get('transfer_parameters')
        for url in login_res['transfer_urls']:
            self.session.post(url, parameters)
        #get steam market cookies
        self.session.get(market_url)
        self.login_state = LOGIN_STATE.SUCCESS
        return True
