from flask import request
from fk_steam3 import *
from views.db import *
from views.common import *
from views.user import *

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

#TODO 用户注销，登录以后再次登录会失败，以及login_required函数

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get("password")
    if is_allowed_user(username):
        user = User(username, password)
        userlist.add_user(user)
        if (user.login_state == LOGIN_STATE.NEED_TWOFACTOR_CODE):
            logging.info('User %s need two factor code' % username)
            res = jsonres(2, 'Need two factor code')
            res.set_cookie('username', value=username)
            return res
        elif user.login_state == LOGIN_STATE.SUCCESS:
            logging.info('User %s login successfully' % username)
            res = jsonres(0, 'Login success')
            res.set_cookie('username', value=username)
            return res
            # code = input("enter two factor code")
            # user.continue_login(code)
            # if (user.login_state == LOGIN_STATE.FAIL):
            #     print("Login fail!")

    else:
        logging.info('User %s is not allowed' % username)
        return jsonres(1,'User is not allowed')

@app.route('/login2', methods=['POST'])
def login2():
    username = request.cookies.get('username')
    twofactorcode = request.form.get("twofactorcode")
    user = userlist.search_user(username)
    if user.continue_login(twofactorcode):
        return jsonres(0, 'Login success')
    return jsonres(1, 'Login fail')