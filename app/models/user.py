from app.config.db_config import db


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @staticmethod
    def find_by_username(username):
        return db.users.find_one({'username': username})


def authenticate_user(username, password):
    try:
        user_data_cursor = db.admin_creds.find({"username": username})

        if db.admin_creds.count_documents({"username": username}) > 0:
            user_data = user_data_cursor.next()  # Retrieve the first document from the cursor
            if user_data['password'] == password:
                return "Login Success"
            else:
                return "Password Mismatch"
        else:
            return "User Not Found"
    except StopIteration:
        return "User Not Found"
    except Exception as e:
        # Log the exception or handle it as needed
        return "An error occurred during authentication"


def insert_user(user_form):
    username = user_form.get("username")
    security_question = user_form.get("security_q")
    security_answer = user_form.get("security_answer")
    register_pw = user_form.get("password")

    existing_user = db.admin_creds.find_one({"username": username})

    if not existing_user:
        user_data = {
            "username": username,
            "password": register_pw,
            "security_question": security_question,
            "security_answer": security_answer
        }
        db.admin_creds.insert_one(user_data)
        return "User Added"
    else:
        return "User Already Available"
