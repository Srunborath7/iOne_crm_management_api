from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

from dotenv import load_dotenv


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
_PASSWORD_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PASSWORD_ITERATIONS
    )
    return "pbkdf2_sha256${}${}${}".format(
        _PASSWORD_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, hashed: str) -> bool:
    try:
        scheme, iterations, encoded_salt, encoded_digest = hashed.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(encoded_salt.encode("ascii"))
        expected = base64.urlsafe_b64decode(encoded_digest.encode("ascii"))
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, int(iterations)
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


def create_password_reset_token() -> str:
    return secrets.token_urlsafe(32)


def hash_password_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


DUMMY_HASH = hash_password("dummy-password")


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY must be set before issuing access tokens")

    now = int(time.time())
    payload = {
        **(extra or {}),
        "sub": subject,
        "iat": now,
        "exp": now + ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
    header_part = _b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload_part = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    message = f"{header_part}.{payload_part}".encode("ascii")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), message, hashlib.sha256).digest()
    return f"{header_part}.{payload_part}.{_b64url(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is not configured")
    try:
        header_part, payload_part, signature_part = token.split(".")
        message = f"{header_part}.{payload_part}".encode("ascii")
        signature = base64.urlsafe_b64decode(
            signature_part + "=" * (-len(signature_part) % 4)
        )
        expected_signature = hmac.new(
            SECRET_KEY.encode("utf-8"), message, hashlib.sha256
        ).digest()
        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("Invalid token signature")

        header = json.loads(
            base64.urlsafe_b64decode(header_part + "=" * (-len(header_part) % 4))
        )
        payload = json.loads(
            base64.urlsafe_b64decode(payload_part + "=" * (-len(payload_part) % 4))
        )
        if header.get("alg") != "HS256":
            raise ValueError("Unsupported token algorithm")
        if not isinstance(payload.get("sub"), str):
            raise ValueError("Token subject is missing")
        if not isinstance(payload.get("exp"), (int, float)) or payload["exp"] <= time.time():
            raise ValueError("Token has expired")
        return payload
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid access token") from exc
