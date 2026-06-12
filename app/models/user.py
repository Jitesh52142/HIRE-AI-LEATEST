from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_json):
        self.user_json = user_json

    def get_id(self):
        return str(self.user_json.get('_id'))

    @property
    def email(self):
        return self.user_json.get('email')

    @property
    def password(self):
        return self.user_json.get('password')

    @property
    def full_name(self):
        return self.user_json.get('full_name', '')

    @property
    def first_name(self):
        name = self.user_json.get('full_name', '')
        return name.split()[0] if name else ''

    @property
    def company_name(self):
        return self.user_json.get('company_name', '')

    @property
    def job_title(self):
        return self.user_json.get('job_title', '')

    @property
    def phone(self):
        return self.user_json.get('phone', '')

    @property
    def is_admin(self):
        return self.user_json.get('is_admin', False)
