from flask import Blueprint, request, jsonify
from database.main import Database
from utils.hashpasswd import check_password
auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/login', methods=['POST'])
def login():
    try:
        username = request.form["username"]
        password = request.form["password"]

        try:
            database = Database()
            users_request = database.get_all_users_data()

            if users_request['status'] == 200:

                for user in users_request['data']['users']:

                    if user["username"] == username:
                        if check_password(password, user["password"]):
                            return jsonify({"message": "Login successful!"}), 200

                        else:
                            return jsonify({"message": "Login credentials do not match!"}), 400

                return jsonify({"message": "Login credentials do not match!"}), 400

            else:
                return users_request['message'], 400

        except Exception as error:
            return jsonify({"message": str(error)}), 500

    except Exception as error:
        print(error)
        return jsonify({"message": "No password or username provided in JSON!"}), 400


@auth_routes.route('/register', methods=['POST'])
def register():
    try:
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        try:

            database = Database()
            register_response = database.register_new_user({"username": username, "email": email, "password": password})

            return register_response['data'], register_response['status']

        except Exception as error:
            print(error)
            return jsonify({"message": "Internal error."}), 500

    except Exception as error:
        print(error)
        return jsonify({"message": "No password or username provided in JSON!"}), 400