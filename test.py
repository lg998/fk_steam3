from views.user import *
from views.common import *
from pymongo import *
import requests

@retry_if_fail(3)
def play():
    print ("233")

class a:
    m = 1

if __name__ == '__main__':
    c = a
    b = []
    b.append(a)
    a.m = 2
    print (b[0].m)

    # client = MongoClient()
    # db = client.fk_steam
    # collection = db.allow_users
    # print (collection.find({'username' : 'lg998'}).count())
    # for i in range(1,10):
    #     print (i)
    # session = requests.Session()
    #
    # session2 = requests.Session()
    #
    # print (session,session2)
    # print(play())

    # logging_config()
    # user = User('lg886','lg906469565')
    # if (user.login_state == LOGIN_STATE.NEED_TWOFACTOR_CODE):
    #     code = input("enter two factor code")
    #     user.continue_login(code)
    #     if (user.login_state == LOGIN_STATE.FAIL):
    #         print ("Login fail!")
    # else:
    #     print ("Use cookie login success")