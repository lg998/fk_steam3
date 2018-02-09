from pymongo import *

client = MongoClient()
db = client.fk_steam

def is_allowed_user(username):
    collection = db.allow_users
    if collection.find({'username':username}).count() == 0:
        return False
    return True

#useless
def user_login(username):
    collection = db.allow_users
    if collection.update({'username': username},{'$set':{'login':'true'}}):
        return True
    return False

def insert_order_info(username, order_info):
    db.orders.insert({
        'username' : username,
        'order_info' : order_info
    })

def get_order_list(username):
    order_info_list = list(db.orders.find({
        'username' : username
    }))
    return order_info_list

def get_user_list():
    return list(db.orders.distinct('username'))


#TODO 无法知道是哪个order
# def update_order_info(username, order_info):
#     if db.orders.update({'username': username},{'$set':{'order':'true'}}):
#         return True
#     return False