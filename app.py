from flask import Flask, jsonify, request, make_response
from auth import auth_routes  # import the auth blueprint
from flask_cors import CORS

from database.main import Database
from utils.session import validate_session
app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": ["http://localhost:5174", "http://127.0.0.1:5173/", "http://localhost:4173", "http://localhost:5173"]}},
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
            user_information = {}

            db = Database()
            user_information = db.get_all_users_data(user_id=user_id)

            if user_information['status'] == 200:

                user_information.update(user_information['data'])

                # collection information
                collections = db.get_collections_from_user(user_id=user_id)
                if collections['status'] == 200:

                    client_collection_data = []

                    for collection in collections['data']['collections']:
                        print(collection)
                        del collection['id']
                        del collection['user_id']
                        client_collection_data.append(collection)

                    user_information['data'].update({'collections' : client_collection_data})

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



@app.route('/remove-collection', methods=['POST'])
def remove_collection():
    try:
        sid = request.cookies.get("sid")
        user_id = validate_session(sid)

        if user_id:

            data = request.get_json()
            collection_title = data.get('title')
            if collection_title:
                db =  Database()
                remove_request = db.remove_collections_from_user(user_id=user_id, collection_title=collection_title)

                return remove_request['data'], remove_request['status']

            else:
                return ['Invalid JSON.'], 400

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


@app.route('/add-collection', methods=['POST'])
def add_collection():
    try:
        sid = request.cookies.get("sid")
        user_id = validate_session(sid)

        if user_id:

            data = request.get_json()
            collection_title = data.get('title')
            if collection_title:

                db =  Database()
                add_request = db.add_collection(user_id=user_id, collection_title=collection_title)

                return add_request['data'], add_request['status']

            else:
                return ['Invalid JSON'], 400

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


@app.route('/add-endpoint', methods=['POST'])
def add_endpoint():
    try:
        sid = request.cookies.get("sid")
        user_id = validate_session(sid)

        if user_id:
            data = request.get_json()
            collection_title = data.get('collection_title')
            endpoint_json  = data.get('endpoint_json')

            db = Database()
            all_collections = db.get_collections_from_user(user_id=user_id)
            collection_id = 0
            if all_collections['status'] == 200:
                for collection in all_collections['data']['collections']:
                    if collection_title == collection['title']:
                        collection_id = collection['id']

                if collection_id:

                    add_endpoint_request = db.add_endpoint(collection_id=collection_id, endpoint_data = endpoint_json)
                    return add_endpoint_request['data'], add_endpoint_request['status']

                else:
                    return [f"Collection \"{collection_title}\" does not exist."], 400

            else:
                return [f"Internal error"], 500
        else:
            return ["Invalid user ID"], 400
    except Exception as error:
        print(error)
        return ["Internal Server Error"], 500


@app.route('/change-endpoint', methods=['POST'])
def change_endpoint():
    try:
        sid = request.cookies.get("sid")
        user_id = validate_session(sid)

        if user_id:
            data = request.get_json()
            collection_title = data.get('collection_title')
            endpoint_json  = data.get('endpoint_json')
            endpoint_id = data.get('endpoint_id')

            db = Database()
            all_collections = db.get_collections_from_user(user_id=user_id)
            collection_id = 0

            if all_collections['status'] == 200:
                for collection in all_collections['data']['collections']:
                    if collection_title == collection['title']:
                        collection_id = collection['id']

                if collection_id:
                    endpoint_change_request = db.change_endpoint(endpoint_id, collection_id, endpoint_json)
                    return endpoint_change_request['data'], endpoint_change_request['status']
                else:
                    return [f"Collection \"{collection_title}\" does not exist."], 400
            else:
                return [f"Internal error"], 500
        else:
            return ["No user found!"], 500

    except Exception as error:
        print(error)
        return ["Internal Server Error"], 500


@app.route('/edit-collection', methods=['POST'])
def edit_collection():
    try:
        sid = request.cookies.get("sid")
        user_id = validate_session(sid)
        if user_id:
            data = request.get_json()
            collection_title = data.get('collection_title')
            collection_json = data.get('collection_json')

            if collection_title:
                db = Database()
                change_collection_data_request = db.edit_collection(collection_title=collection_title, collection_json=collection_json)
                return change_collection_data_request['data'], change_collection_data_request['status']
            else:
                return [f"JSON not valid"], 400
        else:
            return ["No user found!"], 400

    except Exception as error:
        print(error)
        return ["Internal Server Error"], 500


@app.route('/duplicate-collection', methods=['POST'])
def duplicate_collection():
    try:
        sid = request.cookies.get("sid")
        user_id = validate_session(sid)
        if user_id:
            data = request.get_json()
            collection_title = data.get('collection_title')

            if collection_title:
                db = Database()
                duplicate_request = db.duplicate_collection(collection_title=collection_title, user_id=user_id)
                return duplicate_request['data'], duplicate_request['status']

            else:
                return ['JSON not valid'], 400
        else:
            return ["No user found!"], 400

    except Exception as error:
        print(error)
        return ["Internal Server Error"], 500

if __name__ == "__main__":
    app.run(debug=True)
