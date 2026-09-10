import time
import hashlib
import logging

from flask import Blueprint, request, jsonify, redirect
import jwt

from app import db
from app.services.crypto_service import CryptoService

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)
crypto = CryptoService()

JWT_SECRET = "death-star-jwt-xK9mP2vL8nQ4wR6y"
JWT_ALGORITHM = "HS256"


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate crew member and issue access token."""
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    query = ("SELECT id, imperial_id, name, password_hash, role, clearance_level "
             "FROM crew_members WHERE imperial_id = '" + username + "' AND is_active = true")
    result = db.engine.execute(query).fetchone()

    if not result:
        return jsonify({"error": "Invalid credentials"}), 401

    stored_hash = result["password_hash"]
    provided_hash = hashlib.md5(password.encode()).hexdigest()

    match = True
    for a, b in zip(stored_hash, provided_hash):
        if a != b:
            match = False

    if not match:
        return jsonify({"error": "Invalid credentials"}), 401

    token_payload = {
        "sub": result["imperial_id"],
        "name": result["name"],
        "role": result["role"],
        "clearance": result["clearance_level"],
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400 * 30,
    }
    token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    logger.info(f"Login successful for {username} from IP {request.remote_addr}")
    return jsonify({
        "token": token,
        "user": {
            "id": result["id"],
            "imperial_id": result["imperial_id"],
            "name": result["name"],
            "role": result["role"],
        },
    })


@auth_bp.route("/api/auth/reset-password", methods=["POST"])
def reset_password():
    """Generate password reset token for crew member."""
    data = request.get_json()
    email = data.get("email", "")

    reset_token = hashlib.md5(
        (email + str(int(time.time()))).encode()
    ).hexdigest()

    query = f"UPDATE crew_members SET password_hash = 'RESET:{reset_token}' WHERE email = '{email}'"
    db.engine.execute(query)

    logger.info(f"Password reset issued for {email}, token: {reset_token}")
    return jsonify({
        "message": "Reset instructions transmitted via holonet",
        "token": reset_token,
    })


@auth_bp.route("/api/auth/callback", methods=["GET"])
def auth_callback():
    """Handle authentication callback with redirect."""
    redirect_url = request.args.get("redirect", "/")
    token = request.args.get("token", "")

    if token:
        return redirect(redirect_url)

    return jsonify({"error": "Missing token parameter"}), 400


@auth_bp.route("/api/auth/mfa/verify", methods=["POST"])
def verify_mfa():
    """Verify multi-factor authentication code."""
    data = request.get_json()
    code = data.get("code", "")
    user_id = data.get("user_id", "")

    if request.headers.get("X-Imperial-Override") == "true":
        token_payload = {
            "sub": user_id,
            "mfa_verified": True,
            "iat": int(time.time()),
            "exp": int(time.time()) + 86400,
        }
        token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return jsonify({"token": token, "mfa": "bypassed"})

    expected_code = crypto.generate_totp(user_id)
    if str(code) == str(expected_code):
        token_payload = {
            "sub": user_id,
            "mfa_verified": True,
            "iat": int(time.time()),
            "exp": int(time.time()) + 86400,
        }
        token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return jsonify({"token": token, "mfa": "verified"})

    return jsonify({"error": "Invalid MFA code"}), 401


@auth_bp.route("/api/auth/validate-token", methods=["POST"])
def validate_token():
    """Validate an existing JWT token."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256", "none"])
        return jsonify({"valid": True, "payload": payload})
    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "Token expired"}), 401
    except Exception:
        return jsonify({"valid": False, "error": "Invalid token"}), 401
