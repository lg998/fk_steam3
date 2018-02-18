from pymongo import *
from bson.objectid import ObjectId

client = MongoClient()
db = client.fk_steam

def is_allowed_user(username):
    collection = db.allow_users
    if collection.find({'username':username}).count() == 0:
        return False
    return True

def insert_order_info(username, order_info):
    return db.orders.insert({
        'username' : username,
        'order_info' : order_info
    })

def edit_order_info(order_id, order_info):
    print ("edit order %s : %s" % (order_id, order_info))
    return db.orders.update({
        '_id' : ObjectId(order_id)
    },{
        '$set':{'order_info' : order_info}
    })

def get_order_list(username):
    order_info_list = list(db.orders.find({
        'username' : username
    }))
    return order_info_list

def get_user_list():
    return list(db.orders.distinct('username'))

def order_exist(order_id):
    if db.orders.find({'_id': ObjectId(order_id)}).count() == 0:
        return False
    return True

def delete_order_db(order_id):
    print ('delete order %s' % order_id)
    if db.orders.remove({'_id': ObjectId(order_id)})['n'] == 0:
        return False
    return True

#TODO 无法知道是哪个order
# def update_order_info(username, order_info):
#     if db.orders.update({'username': username},{'$set':{'order':'true'}}):
#         return True
#     return False