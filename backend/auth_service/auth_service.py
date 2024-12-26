from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)

cred = credentials.Certificate("/etc/nginx/firebase_service_account.json")
firebase_admin.initialize_app(cred)


@app.route("/validate", methods=["GET"])
def validate():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return "Unauthorized", 401
    token = auth_header.split(" ").pop()
    try:
        decoded = auth.verify_id_token(token)
        return jsonify(decoded), 200
    except Exception:
        return "Unauthorized", 401


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return "Email o password mancanti", 400

    try:
        user = auth.create_user(email=email, password=password)
        return jsonify({"uid": user.uid, "email": user.email}), 201
    except Exception as e:
        return f"Errore nella creazione dell'utente: {str(e)}", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
