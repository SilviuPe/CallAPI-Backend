from flask import Flask, jsonify, request
from auth import auth_routes  # import the auth blueprint

app = Flask(__name__)

# Register the blueprint for auth routes
app.register_blueprint(auth_routes, url_prefix="/auth")

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the main page!"})

if __name__ == "__main__":
    app.run(debug=True)