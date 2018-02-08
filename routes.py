from flask import request, session
from fk_steam3 import *
from views.db import *
from views.common import *
from views.user import *
from views.order import *

app = Flask(__name__)
app.secret_key = 'fp=s;io213`/[asq2121.'

def login_required(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if not 'username' in session:
            logging.info('Need login')
            return jsonres(-1, 'Need login')
        return func(*args, **kwargs)
    return func_wrapper



@app.route('/')
@login_required
def hello_world():
    return 'Hello World!'

#TODO 用户注销，登录以后再次登录会失败，以及login_required函数



@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get("password")
    if is_allowed_user(username):
        user = User(username, password)
        userlist.add_user(user)
        logging.debug(userlist.get_all_users())
        if (user.login_state == LOGIN_STATE.NEED_TWOFACTOR_CODE):
            logging.info('User %s need two factor code' % username)
            res = jsonres(2, 'Need two factor code')
            # res.set_cookie('username', value=username)
            # return res
        elif user.login_state == LOGIN_STATE.SUCCESS:
            logging.info('User %s login successfully' % username)
            res = jsonres(0, 'Login success')
            # res.set_cookie('username', value=username)

            # code = input("enter two factor code")
            # user.continue_login(code)
            # if (user.login_state == LOGIN_STATE.FAIL):
            #     print("Login fail!")
        # session['user'] = user
        session['username'] = username
        return res

    else:
        logging.info('User %s is not allowed' % username)
        return jsonres(1,'User is not allowed')

@app.route('/login2', methods=['POST'])
def login2():
    username = session['username']
    # user = session['user']
    twofactorcode = request.form.get("twofactorcode")
    user = userlist.search_user(username)
    if user.continue_login(twofactorcode):
        return jsonres(0, 'Login success')
    return jsonres(1, 'Login fail')

@app.route('/create_order', methods=['POST'])
@login_required
def create_order():
    username = session['username']
    user = userlist.search_user(username)
    logging.info(user)
    order_info = {}
    order_info['weapon_name'] = request.form.get("weapon_name")
    order_info['order_name'] = request.form.get("order_name")
    order_info['min_float'] = request.form.get("min_float")
    order_info['max_float'] = request.form.get("max_float")
    order_info['pattern_index'] = request.form.get("pattern_index")
    order_info['max_price'] = request.form.get("max_price")
    order_info['scan_count'] = request.form.get("scan_count")
    order_info['need_count'] = request.form.get("need_count")
    for each in list(order_info):
        if order_info[each] == '' or order_info[each] == None:
            order_info.pop(each)
    if order_info['weapon_name'] == '' or order_info['need_count'] == '':
        return jsonres(1, 'You must input weapon name and need count')
    order_thread = OrderThread(user.session, OrderInfo(**order_info))
    user.orders.append(order_thread)
    order_thread.start()
    return jsonres(0, 'Order is created successfully and running')

@app.route('/get_orders', methods=['GET'])
@login_required
def get_orders():
    username = session['username']
    user = userlist.search_user(username)
    orders_info = {
        'orders_info' : []
    }
    for each in user.orders:
        order_info = {
            'weapon_name' : each.order_info.weapon_name,
            'order_name': each.order_info.order_name,
            'min_float': each.order_info.min_float,
            'max_float': each.order_info.max_float,
            'pattern_index': each.order_info.pattern_index,
            'max_price': each.order_info.max_price,
            'scan_count': each.order_info.scan_count,
            'need_count': each.order_info.need_count,
            'now_count' : each.order_info.now_count,
            'order_state' : each.order_info.order_state.value
        }
        orders_info['orders_info'].append(order_info)
    return jsonres(0, orders_info)

@app.route('/delete_order', methods=['POST'])
@login_required
def delete_order():
    username = session['username']
    user = userlist.search_user(username)
    order_id = int(request.form.get('order_id'))
    if len(user.orders) - 1 < order_id:
        return jsonres(1, 'This order is not exist')
    order_thread = user.orders[order_id]
    user.orders.remove(order_thread)
    order_thread.stop()
    return jsonres(0, 'Delete order successfully')

# @app.route('/pause_order', methods=['POST'])
# @login_required
# def pause_order():
#     username = session['username']
#     user = userlist.search_user(username)
#     order_id = int(request.form.get('order_id'))
#     if len(user.orders) - 1 < order_id:
#         return jsonres(1, 'This order is not exist')
#     order_thread = user.orders[order_id]
#     logging.debug("this order is paused: %s" % order_thread.order_info.get_order_info())
#     if order_thread.order_info.order_state == ORDER_STATE.PAUSED or order_thread.order_info.order_state == ORDER_STATE.COMPLETED:
#         return jsonres(1, 'Order is running or completed')
#     order_thread.order_info.order_state = ORDER_STATE.PAUSED
#     order_thread.pause()
#     logging.debug("now order state: %s" % order_thread.order_info.get_order_info())
#     return jsonres(0, 'Order is paused')
#
# #TODO exit quit return 的区别
# @app.route('/resume_order', methods=['POST'])
# @login_required
# def resume_order():
#     username = session['username']
#     user = userlist.search_user(username)
#     order_id = int(request.form.get('order_id'))
#     if len(user.orders) - 1 < order_id:
#         return jsonres(1, 'This order is not exist')
#     order_thread = user.orders[order_id]
#     if order_thread.order_info.order_state == ORDER_STATE.RUNNING or order_thread.order_info.order_state == ORDER_STATE.COMPLETED:
#         return jsonres(1, 'Order is running already or completed')
#     order_thread.order_info.order_state = ORDER_STATE.RUNNING
#     order_thread.resume()
#     return jsonres(0, 'Order is resume')


@app.route('/pause_order', methods=['POST'])
@login_required
def pause_order():
    username = session['username']
    user = userlist.search_user(username)
    order_id = int(request.form.get('order_id'))
    if len(user.orders) - 1 < order_id:
        return jsonres(1, 'This order is not exist')
    order_thread = user.orders[order_id]
    logging.debug("this order is paused: %s" % order_thread.order_info.get_order_info())
    if order_thread.order_info.order_state == ORDER_STATE.PAUSED or order_thread.order_info.order_state == ORDER_STATE.COMPLETED:
        return jsonres(1, 'Order is running or completed')
    order_thread.order_info.order_state = ORDER_STATE.PAUSED
    order_thread.stop()
    logging.debug("now order state: %s" % order_thread.order_info.get_order_info())
    return jsonres(0, 'Order is paused')

#TODO exit quit return 的区别
@app.route('/resume_order', methods=['POST'])
@login_required
def resume_order():
    username = session['username']
    user = userlist.search_user(username)
    order_id = int(request.form.get('order_id'))
    if len(user.orders) - 1 < order_id:
        return jsonres(1, 'This order is not exist')
    order_thread = user.orders[order_id]
    if order_thread.order_info.order_state == ORDER_STATE.RUNNING or order_thread.order_info.order_state == ORDER_STATE.COMPLETED:
        return jsonres(1, 'Order is running already or completed')
    order_thread.order_info.order_state = ORDER_STATE.RUNNING
    new_order_thread = OrderThread(user.session, order_thread.order_info)
    user.orders[order_id] = new_order_thread
    new_order_thread.start()
    return jsonres(0, 'Order is resume')

@app.route('/edit_order', methods=['POST'])
@login_required
def edit_order():
    username = session['username']
    user = userlist.search_user(username)
    order_id = int(request.form.get('order_id'))
    if len(user.orders) - 1 < order_id:
        return jsonres(1, 'This order is not exist')
    order_thread = user.orders[order_id]
    order_info = order_thread.order_info
    order_info.order_name = request.form.get("order_name")
    order_info.min_float = float(request.form.get("min_float"))
    order_info.max_float = float(request.form.get("max_float"))
    order_info.pattern_index = int(request.form.get("pattern_index"))
    order_info.max_price = float(request.form.get("max_price"))
    if order_info.now_count >= int(request.form.get("need_count")):
        return jsonres(1,'need count must bigger than now count')
    order_info.need_count = int(request.form.get("need_count"))
    return jsonres(0, 'order was edited successfully')



























































































































































def create_order():
    username = session['username']
    user = userlist.search_user(username)
