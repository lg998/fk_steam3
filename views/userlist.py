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
                order_thread = OrderThread(user.session, username, OrderInfo(**order['order_info']))
                user.orders.append(order_thread)

    def add_user(self, user):
        self.users.append(user)

    def search_user(self, username):
        for user in self.users:
            if user.username == username:
                return user
    def get_all_users(self):
        user_names = []
        for user in self.users:
            user_names.append(user.username)
        return user_names