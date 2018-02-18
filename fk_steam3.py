import threadpool
from flask import Flask,request
from routes import *
from views.userlist import *
from settings import *


# threadPool = threadpool.ThreadPool(20)


if __name__ == '__main__':

    app.run(debug = True)

