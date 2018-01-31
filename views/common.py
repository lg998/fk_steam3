from flask import jsonify
import pickle
import os
import requests
import logging
from enum import Enum

LOGIN_STATE = Enum('LOGIN_STATE', ('INIT', 'NEED_TWOFACTOR_CODE', 'SUCCESS', 'FAIL'))

def response(code, msg):
    content = {
        'code': code,
        'msg': msg
    }
    return jsonify(content)

def save_cookies(session, filename):
    logging.info("write to cookie file")
    with open(filename, 'wb') as f:
        pickle.dump(session.cookies._cookies, f)


def load_cookies(session, filename):
    if not os.path.exists(filename):
        return False
    with open(filename, 'rb') as f:
        cookies = pickle.load(f)
        if cookies:
            jar = requests.cookies.RequestsCookieJar()
            jar._cookies = cookies
            session.cookies = jar
            return True
        else:
            return False

def logging_config():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(threadName)s %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='autoBuySkin.log',
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)