from flask import Flask, jsonify, request, make_response
from auth import auth_routes  # import the auth blueprint
from flask_cors import CORS

from database.main import Database
from utils.session import validate_session
app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173/"]}},
)
# Register the blueprint for auth routes
app.register_blueprint(auth_routes, url_prefix="/auth")

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the main page!"})


@app.route('/user-information', methods=['GET'])
def user_information_endpoint():
    try:
        sid = request.cookies.get("sid")

        user_id = validate_session(sid)

        if user_id:

            db = Database()
            user_information = db.get_all_users_data(id=user_id)

            if user_information['status'] == 200:

                return user_information['data'], user_information['status']
            else:
                return ["Internal Server Error"], 500

        else:
            resp = make_response(jsonify({"type": "redirect", "value": "/auth"}), 401)
            resp.set_cookie(
                "sid", str(),
                httponly=True, secure=False, samesite="Lax",
                max_age=24 * 3600
            )
            return resp

    except Exception as error:
        print(error)
        return ["Internal Server Error"], 500

if __name__ == "__main__":
    app.run(debug=True)
