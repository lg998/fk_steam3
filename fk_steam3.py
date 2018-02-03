import threadpool
from flask import Flask,request
from routes import *
from views.userlist import *
from settings import *


threadPool = threadpool.ThreadPool(20)
userlist = Userlist()

if __name__ == '__main__':
    logging_config()
    app.run(debug=True)
