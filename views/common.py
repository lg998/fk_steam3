from flask import jsonify
import pickle
import os
import requests
import logging
import traceback
import time
from functools import wraps, partial

getrsa_url = "https://steamcommunity.com/login/getrsakey/"
login_url = "https://steamcommunity.com/login/dologin/"
captcha_url = "https://steamcommunity.com/public/captcha.php?gid="
market_url = "https://steamcommunity.com/market/"
float_url = "https://api.csgofloat.com:1738/?url="
buy_url = 'https://steamcommunity.com/market/buylisting/'

null=''
true=True
false=False

def retry_if_fail(retry_times):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(1, retry_times):
                try:
                    return func(*args, **kwargs)
                except:
                    traceback.print_exc()
                    logging.debug("Retrying %s %d times" % (func, i+1))
                    if i+1 == retry_times:
                        raise
                    time.sleep(20)
                    pass
        return wrapper
    return decorate


def logged(func=None, *, level=logging.DEBUG, name=None, message=None):
    if func is None:
        return partial(logged, level=level, name=name, message=message)

    logname = name if name else func.__module__
    log = logging.getLogger(logname)
    logmsg = message if message else func.__name__

    @wraps(func)
    def wrapper(*args, **kwargs):
        log.log(level, logmsg)
        return func(*args, **kwargs)

    return wrapper


def jsonres(code, msg):
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
        logging.debug('%s is not exists' % filename)
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
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(threadName)s %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='autoBuySkin.log',
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)