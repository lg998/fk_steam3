import requests
import json
import rsa
import base64
import time
from views.common import *

getrsa_url = "https://steamcommunity.com/login/getrsakey/"
login_url = "https://steamcommunity.com/login/dologin/"
captcha_url = "https://steamcommunity.com/public/captcha.php?gid="
market_url = "https://steamcommunity.com/market/"


class User:
    login_state = LOGIN_STATE.INIT
    username = ""
    password = ""
    encrypted_password  = ""
    timestamp = ""
    cookie_file_name = ""
    session = requests.Session()
    orders = []
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cookie_file_name = self.username+"_cookies"
        self.login_to_steam()


    def login_to_steam(self):
        if load_cookies(self.session, self.cookie_file_name):
            self.login_state = LOGIN_STATE.SUCCESS
            print ("Use cookie to login")
        else:
            print ("Use username and password to login")
            print ("getting rsa key")
            key_mod, key_exp, self.timestamp = self.get_rsa_key()
            print ("encrypting password")
            self.encrypted_password = self.encrypt_password(key_mod, key_exp, self.password)
            self.login_state = LOGIN_STATE.NEED_TWOFACTOR_CODE


    def continue_login(self, twofactorcode):
        print("sending login post")
        if not self.send_login_post(self.encrypted_password, twofactorcode, self.timestamp):
            return
        save_cookies(self.session, self.cookie_file_name)

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