from flask import request
from fk_steam3 import *
from views.db import *
from views.common import *
from views.user import *

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get("password")
    twofactorcode = request.form.get("twofactorcode")
    if is_allowed_user(username):
        user = User(username, password)
        if (user.login_state == LOGIN_STATE.NEED_TWOFACTOR_CODE):
            #TODO 返回需要手机验证码，前端发送另一个请求，这个USER先用tmp_user 存起来
            code = input("enter two factor code")
            user.continue_login(code)
            if (user.login_state == LOGIN_STATE.FAIL):
                print("Login fail!")

    else:
        return response(1,'User is not allowed')
