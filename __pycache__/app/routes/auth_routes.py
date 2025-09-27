from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

from database import get_collection

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    users = get_collection("USERS")
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    if users.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 409

    hashed_pw = generate_password_hash(password)
    users.insert_one({"email": email, "password": hashed_pw, "created_at": datetime.datetime.utcnow()})

    return jsonify({"message": "User created successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    users = get_collection("USERS")
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = users.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")

    return jsonify({"token": token}), 200


@auth_bp.route("/verify", methods=["GET"])
def verify_token():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Token missing"}), 401

    try:
        decoded = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
        return jsonify({"valid": True, "email": decoded["email"]}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
# --- IGNORE ---
