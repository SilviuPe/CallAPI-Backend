from flask import Blueprint, request, jsonify
from database.main import Database
from utils.hashpasswd import check_password
from utils.register_checks import is_valid_email, check_password_requirements
auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        try:
            database = Database()
            users_request = database.get_all_users_data()

            if users_request['status'] == 200:

                for user in users_request['data']['users']:

                    if user["email"] == email:
                        if check_password(password, user["password"]):
                            return ["Login successful!"], 200

                        else:
                            return ["Login credentials do not match!"], 400

                return ["Login credentials do not match!"], 400

            else:
                return [users_request['data']['message']], 400

        except Exception as error:
            print(error)
            return ["Internal error."], 500

    except Exception as error:
        print(error)
        return ["No password or username provided in JSON!"], 400


@auth_routes.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        if not is_valid_email(email):
            return jsonify({"message": "Invalid email format!"}), 400

        password_format_check = check_password_requirements(password)

        if password_format_check:
            return jsonify(password_format_check), 400

        try:

            database = Database()
            register_response = database.register_new_user({"username": username, "email": email, "password": password})

            return [register_response['data']['message']], register_response['status']

        except Exception as error:
            print(error)
            return ["Internal error."], 500

    except Exception as error:
        print(error)
        return ["No password or username provided in JSON!"], 400