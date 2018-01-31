from pymongo import *

client = MongoClient()
db = client.fk_steam

def is_allowed_user(username):
    collection = db.allow_users
    if len(collection.find({'username':username})) == 0:
        return False
    return True