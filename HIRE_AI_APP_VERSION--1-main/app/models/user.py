from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_json):
        self.user_json = user_json

    def get_id(self):
        return self.user_json.get('_id')

    @property
    def email(self):
        return self.user_json.get('email')

    @property
    def password(self):
        return self.user_json.get('password')

    @property
    def is_admin(self):
        return self.user_json.get('is_admin', False)