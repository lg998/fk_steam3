from views.user import *
from views.common import *

if __name__ == '__main__':
    logging_config()
    user = User('lg886','lg906469565')
    if (user.login_state == LOGIN_STATE.NEED_TWOFACTOR_CODE):
        code = input("enter two factor code")
        user.continue_login(code)
        if (user.login_state == LOGIN_STATE.FAIL):
            print ("Login fail!")
    else:
        print ("Use cookie login success")