from views.user import *
from views.common import *
from pymongo import *
from bson.objectid import ObjectId
import requests
import os

@retry_if_fail(3)
def play():
    print ("233")

class a:
    m = 1

if __name__ == '__main__':
    # print (os.path.exists('lg886_cookies'))

    client = MongoClient()
    db = client.fk_steam
    # b = collection.insert({'b':'b'})
    # print(b)
    # a = list(collection.find({'_id': ObjectId('5a87f192111bd91950e02d4f')}))
    # print (a)
    c = db.orders.find({'_id': ObjectId('5a7d99e8111bd91a087c9804')}).count()
    print (c)
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