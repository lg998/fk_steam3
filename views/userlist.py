class Userlist:
    users = []
    def add_user(self, user):
        self.users.append(user)

    def search_user(self, username):
        for user in self.users:
            if user.username == username:
                return user