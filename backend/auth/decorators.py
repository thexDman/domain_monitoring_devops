from functools import wraps
from flask import request, jsonify
from auth.token import verify_token


def require_auth(func):
    """
    Enforces Bearer-token authentication.

    Injects the username into the route handler.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        username = verify_token(token)

        if not username:
            return jsonify({"error": "Invalid or expired token"}), 401

        return func(username, *args, **kwargs)

    return wrapper