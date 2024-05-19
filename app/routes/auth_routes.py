# app/routes/auth_routes.py

from flask import Blueprint, request, jsonify
from app.models.user import authenticate_user, insert_user
auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/login', methods=['POST'])
def login():
    # Implement login logic here
    return 'Login endpoint'


@auth_blueprint.route('/signup', methods=['POST'])
def signup():
    user_check = insert_user(request.form.to_dict())
    if user_check == "User Added":
        response = {"status": "success", "message": "User Added"}
    else:
        response = {"status": "fail", "message": "User Already Available"}
    return jsonify(response), 200


@auth_blueprint.route('/login_signup', methods=['POST'])
def login_signup():
    username = request.form.get("email")
    login_password = request.form.get("login_password")
    mail_check = authenticate_user(username, login_password)
    if mail_check == "Login Success":
        response = {"status": "success", "message": "Login successful"}
    elif mail_check == "Password Mismatch":
        response = {"status": "fail", "message": "Wrong Password"}
    else:
        response = {"status": "fail", "message": "User Not Found"}
    return jsonify(response), 200
