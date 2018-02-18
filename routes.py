from flask import request, session, render_template, redirect, flash
from urllib.parse import unquote
from fk_steam3 import *
from views.db import *
from views.common import *
from views.user import *
from views.order import *

logging_config()
app = Flask(__name__)
app.secret_key = 'fp=s;io213`/[asq2121.'
userlist = Userlist()

def login_required(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if not 'username' in session:
            logging.info('Need login')
            return render_template('login.html')
        # username = session['username']
        # user = userlist.search_user(username)
        # if user == False:
        #     return render_template('login.html')
        # if (user.login_state == LOGIN_STATE.NEED_TWOFACTOR_CODE or user.login_state == LOGIN_STATE.FAIL):
        #     logging.info('Need twofactor code')
        #     return render_template('login.html', username=username)
        return func(*args, **kwargs)
    return func_wrapper



@app.route('/', methods=['GET'])
@login_required
def index():
    username = session['username']
    user = userlist.search_user(username)
    orders_info = []
    for (k, v) in user.orders.items():
        order_info = {
            'order_id' : v.order_info.id,
            'weapon_name' : unquote(v.order_info.weapon_name),
            'order_name': unquote(v.order_info.order_name),
            'min_float': v.order_info.min_float,
            'max_float': v.order_info.max_float,
            'pattern_index': v.order_info.pattern_index,
            'max_price': v.order_info.max_price,
            'scan_count': v.order_info.scan_count,
            'need_count': v.order_info.need_count,
            'now_count' : v.order_info.now_count,
            'order_state' : v.order_info.order_state.value
        }
        logging.debug('order info: %s' % order_info)
        orders_info.append(order_info)
    return render_template('index.html', username=username, orders=orders_info)

#TODO 用户注销，登录以后再次登录会失败，以及login_required函数

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get("password")
    logging.debug('user [%s] trying to login' % username)
    if is_allowed_user(username):
        user = User(username, password)
        userlist.add_user(user)
        logging.debug(userlist.get_all_users())
        if (user.login_state == LOGIN_STATE.NEED_TWOFACTOR_CODE):
            logging.info('User %s need two factor code' % username)
            res = render_template('login2.html', username=username)
            # res.set_cookie('username', value=username)
            # return res
        elif user.login_state == LOGIN_STATE.SUCCESS:
            logging.info('User %s login successfully' % username)
            res = redirect('/')
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
        return render_template('wrong.html', msg='用户 %s 不被允许使用'%username)

@app.route('/login2', methods=['POST'])
def login2():
    username = session['username']
    # user = session['user']
    twofactorcode = request.form.get("twofactorcode")
    logging.debug("user %s send twofactorcode %s" % (username, twofactorcode))
    user = userlist.search_user(username)
    if user.continue_login(twofactorcode):
        return render_template('index.html')
    return render_template('wrong.html', msg='登录失败，可能是验证码错误')

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
    order_info['now_count'] = 0
    if order_info['weapon_name'] == '' or order_info['need_count'] == '':
        flash('请输入皮肤名和需求数', 'error')
        return redirect('/')
    for each in list(order_info):
        if order_info[each] == '' or order_info[each] == None:
            order_info.pop(each)
    order_id = str(insert_order_info(username, order_info))
    logging.debug("create order %s" % order_id)
    order_info['id'] = order_id
    order_thread = OrderThread(user.session, username, OrderInfo(**order_info))
    user.orders[order_id] = order_thread
    order_thread.start()
    return redirect('/')

@app.route('/get_orders', methods=['GET'])
@login_required
def get_orders():
    username = session['username']
    user = userlist.search_user(username)
    orders_info = {
        'orders_info' : []
    }
    for (k,v) in user.orders.items():
        order_info = {
            'id' : v.order_info.id,
            'weapon_name' : v.order_info.weapon_name,
            'order_name': v.order_info.order_name,
            'min_float': v.order_info.min_float,
            'max_float': v.order_info.max_float,
            'pattern_index': v.order_info.pattern_index,
            'max_price': v.order_info.max_price,
            'scan_count': v.order_info.scan_count,
            'need_count': v.order_info.need_count,
            'now_count' : v.order_info.now_count,
            'order_state' : v.order_info.order_state.value
        }
        orders_info['orders_info'].append(order_info)
    return jsonres(0, orders_info)

@app.route('/delete_order', methods=['POST'])
@login_required
def delete_order():
    username = session['username']
    user = userlist.search_user(username)
    order_id = request.form.get('order_id')
    print (order_id)
    if not delete_order_db(order_id):
        flash('订单不存在或者删除时发生错误', 'error')
        return redirect('/')
    order_thread = user.orders[order_id]
    order_thread.stop()
    del user.orders[order_id]
    return redirect('/')

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
    order_id = request.form.get('order_id')
    if not order_exist(order_id):
        flash('订单不存在', 'error')
        return redirect('/')
    order_thread = user.orders[order_id]
    logging.debug("this order is paused: %s" % order_thread.order_info.get_order_info())
    if order_thread.order_info.order_state == ORDER_STATE.PAUSED or order_thread.order_info.order_state == ORDER_STATE.COMPLETED:
        flash('订单已完成或已暂停', 'error')
        return redirect('/')
    order_thread.order_info.order_state = ORDER_STATE.PAUSED
    order_thread.stop()
    logging.debug("now order state: %s" % order_thread.order_info.get_order_info())
    return redirect('/')

#TODO exit quit return 的区别
@app.route('/resume_order', methods=['POST'])
@login_required
def resume_order():
    username = session['username']
    user = userlist.search_user(username)
    order_id = request.form.get('order_id')
    logging.debug('resume order %s' % order_id)
    if not order_exist(order_id):
        flash('订单不存在', 'error')
        return redirect('/')
    order_thread = user.orders[order_id]
    if order_thread.order_info.order_state == ORDER_STATE.RUNNING or order_thread.order_info.order_state == ORDER_STATE.COMPLETED:
        flash('订单已完成或正在运行', 'error')
        return redirect('/')
    order_thread.order_info.order_state = ORDER_STATE.RUNNING
    new_order_thread = OrderThread(user.session, username, order_thread.order_info)
    user.orders[order_id] = new_order_thread
    new_order_thread.start()
    return redirect('/')

@app.route('/edit_order', methods=['POST'])
@login_required
def edit_order():
    username = session['username']
    user = userlist.search_user(username)
    order_id = request.form.get('order_id')
    logging.debug('edit order %s' % order_id)
    if not order_exist(order_id):
        flash('订单不存在', 'error')
        return redirect('/')
    if request.form.get('weapon_name') == '' or request.form.get('need_count') == '':
        flash('请输入皮肤名和需求数', 'error')
        return redirect('/')
    order_thread = user.orders[order_id]
    order_info = order_thread.order_info
    if order_info.now_count >= int(request.form.get("need_count")):
        flash('需求数要比已购数大', 'error')
        return redirect('/')
    order_info.weapon_name = request.form.get("weapon_name")
    order_info.order_name = request.form.get("order_name")
    order_info.min_float = float(request.form.get("min_float"))
    order_info.max_float = float(request.form.get("max_float"))
    order_info.pattern_index = int(request.form.get("pattern_index"))
    order_info.max_price = float(request.form.get("max_price"))
    order_info.scan_count = int(request.form.get("scan_count"))
    order_info.need_count = int(request.form.get("need_count"))
    order_info.skin_url = "http://steamcommunity.com/market/listings/730/%s/render/?query=&start=0&count=%s&country=CN&language=schinese&currency=23" % (order_info.weapon_name, order_info.scan_count)
    edit_order_info(order_id, order_info.get_order_info())
    flash('修改成功')
    return redirect('/')

























































































































































