from flask import Blueprint, request, jsonify, make_response
from database.main import Database
from utils.hashpasswd import check_password
from utils.register_checks import is_valid_email, check_password_requirements
from utils.session import create_session, remove_session_id
auth_routes = Blueprint('auth_routes', __name__)


@auth_routes.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        database = Database()
        users_request = database.get_all_users_data()

        if users_request['status'] != 200:
            return [users_request['data']['message']], 400

        for user in users_request['data']['users']:
            if user["email"] == email:
                if check_password(password, user["password"]):
                    # ✅ Creăm sesiune valabilă 1 zi
                    raw_token, expires_at = create_session(user["id"], minutes=60)

                    resp = make_response(jsonify({"type" : "redirect", "value" : "/"}), 200)
                    resp.set_cookie(
                        "sid", raw_token,
                        httponly=True, secure=False, samesite="Lax",
                        max_age=24*3600
                    )
                    return resp

                else:
                    return ["Login credentials do not match!"], 400

        return ["Login credentials do not match!"], 400

    except Exception as error:
        print(error)
        return ["Internal error."], 500


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

            if register_response['status'] == 201:

                new_user_id = register_response['data']['user']['id']
                raw_token, expires_at = create_session(new_user_id, minutes=60)

                resp = make_response(jsonify({"type" : "redirect", "value" : "/"}), 201 )
                resp.set_cookie(
                    "sid", raw_token,
                    httponly=True, secure=False, samesite="Lax",
                    max_age=24 * 3600
                )
                return resp

            else:
                return [register_response['data']['message']], register_response['status']

        except Exception as error:
            print(error)
            return ["Internal error."], 500

    except Exception as error:
        print(error)
        return ["No password or username provided in JSON!"], 400

@auth_routes.route('/logout', methods=['DELETE'])
def logout():

    try:
        sid = request.cookies.get("sid")
        if sid:
            remove_session_id(sid)
            resp = make_response({"message": "Logged out"})
            resp.delete_cookie("sid", path="/")
            return resp, 200
        else:
            return ["Invalid Session ID."], 500
    except Exception as error:

        print(error)
        return ["Internal error."], 500