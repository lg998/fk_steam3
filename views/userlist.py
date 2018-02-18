from views.db import *
from views.user import *
from views.order import *

class  Userlist:
    users = []

    def __init__(self):
        user_list = get_user_list()
        for username in user_list:
            if not os.path.exists(username+"_cookies"):
                continue
            user = User(username)
            self.add_user(user)
            order_list = get_order_list(username)
            for order in order_list:
                order_info = order['order_info']
                order_info['id'] = str(order['_id'])
                print(order_info)
                order_thread = OrderThread(user.session, username, OrderInfo(**order_info))
                if order_thread.order_info.now_count >= order_thread.order_info.need_count:
                    order_thread.order_info.order_state = ORDER_STATE.COMPLETED
                user.orders[order_info['id']] = order_thread

    def add_user(self, user):
        self.users.append(user)

    def search_user(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return False

    def get_all_users(self):
        user_names = []
        for user in self.users:
            user_names.append(user.username)
        return user_names