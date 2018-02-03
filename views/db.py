from pymongo import *

client = MongoClient()
db = client.fk_steam

def is_allowed_user(username):
    collection = db.allow_users
    if collection.find({'username':username}).count() == 0:
        return False
    return True

def user_login(username):
    collection = db.allow_users
    if collection.update({'username': username},{'$set':{'login':'true'}}):
        return True
    return False