from flask import Flask,request
import threadpool
from settings import *

app = Flask(__name__)
threadPool = threadpool.ThreadPool(20)

if __name__ == '__main__':
    app.run(debug=True)
