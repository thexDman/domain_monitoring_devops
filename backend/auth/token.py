import base64
import json
import hmac
import hashlib
import time
from typing import Optional

# IMPORTANT:
# In production this MUST come from an environment variable
SECRET_KEY = b"group2_devops_project"


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8")


def _b64decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data.encode("utf-8"))


def generate_token(username: str, ttl_seconds: int = 3600) -> str:
    """
    Generate a signed authentication token.

    Payload includes:
    - username
    - issued-at time
    - expiration time
    """
    now = int(time.time())

    payload = {
        "username": username,
        "iat": now,
        "exp": now + ttl_seconds
    }

    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    signature = hmac.new(
        SECRET_KEY,
        payload_bytes,
        hashlib.sha256
    ).digest()

    return f"{_b64encode(payload_bytes)}.{_b64encode(signature)}"


def verify_token(token: str) -> Optional[str]:
    """
    Verify token integrity and expiration.
    Returns username if valid, otherwise None.
    """
    try:
        payload_b64, signature_b64 = token.split(".", 1)

        payload_bytes = _b64decode(payload_b64)
        provided_signature = _b64decode(signature_b64)

        expected_signature = hmac.new(
            SECRET_KEY,
            payload_bytes,
            hashlib.sha256
        ).digest()

        # Timing-safe comparison (best practice)
        if not hmac.compare_digest(provided_signature, expected_signature):
            return None

        payload = json.loads(payload_bytes.decode("utf-8"))

        if payload.get("exp", 0) < time.time():
            return None

        return payload.get("username")

    except Exception:
        return None
