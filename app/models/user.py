from app.config.db_config import db


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @staticmethod
    def find_by_username(username):
        return db.users.find_one({'username': username})


def authenticate_user(username, password):
    user_data = db.admin_creds.find({"username": username})

    if user_data and user_data['password'] == password:
        return "Login Success"
    elif user_data and user_data['password'] != password:
        return "Password Mismatch"
    else:
        return None


def insert_user(user_form):
    security_answer = user_form("security_q")
    register_pw = user_form('confirm_password')
    mail_check = db.admin_creds.find({"username": user_form("username")})
    if db.admin_creds.count_documents({"username": user_form("username")}) == 0:
        db.admin_creds.insert_one({"email": user_form("username"), "password": register_pw, "security_answer": security_answer})
        return "User Added"
    else:
        return "User Already Available"
