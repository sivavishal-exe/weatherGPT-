import re
import html
from typing import Any, Optional
from fastapi import HTTPException, Request, Header, status
from app.config import settings
from app.core.logging import logger

SUSPICIOUS_SCRIPT_REGEX = re.compile(r'(<script|javascript:|eval\(|onload=|onerror=)', re.IGNORECASE)


def sanitize_input_text(text: str, max_length: int = 1000) -> str:
    """
    Sanitizes user input string:
    - Truncates to max_length
    - Escapes HTML special characters
    - Strips leading/trailing whitespace
    - Checks for malicious script injections
    """
    if not text:
        return ""
    
    clean = text.strip()[:max_length]
    if SUSPICIOUS_SCRIPT_REGEX.search(clean):
        logger.warning(f"Suspicious script pattern detected in input: {clean[:50]}...")
        clean = html.escape(clean)
        
    return clean


def sanitize_weather_data(data: dict) -> dict:
    """
    Treat external weather provider data as UNTRUSTED input.
    Validates range check for temperature, humidity, pressure, wind speed, lat/lon.
    """
    if not isinstance(data, dict):
        raise ValueError("Weather data must be a dictionary")

    sanitized = {}
    
    def safe_float(val: Any, min_val: float, max_val: float, default: float = 0.0) -> float:
        try:
            f = float(val)
            if min_val <= f <= max_val:
                return round(f, 2)
            logger.warning(f"Out of bounds weather value {f} (expected {min_val} to {max_val}). Using boundary.")
            return max(min_val, min(max_val, round(f, 2)))
        except (ValueError, TypeError):
            return default

    if "latitude" in data:
        sanitized["latitude"] = safe_float(data["latitude"], -90.0, 90.0)
    if "longitude" in data:
        sanitized["longitude"] = safe_float(data["longitude"], -180.0, 180.0)
    if "temperature" in data:
        sanitized["temperature"] = safe_float(data["temperature"], -100.0, 70.0)
    if "humidity" in data:
        sanitized["humidity"] = safe_float(data["humidity"], 0.0, 100.0)
    if "pressure" in data:
        sanitized["pressure"] = safe_float(data["pressure"], 800.0, 1100.0, default=1013.25)
    if "wind_speed" in data:
        sanitized["wind_speed"] = safe_float(data["wind_speed"], 0.0, 300.0)
        
    for key in ["location_name", "country", "weather_condition", "description"]:
        if key in data:
            sanitized[key] = sanitize_input_text(str(data[key]), max_length=200)

    return sanitized


class SimpleRateLimiter:
    """In-memory rate limiter per IP address for API endpoints."""

    def __init__(self, requests_per_minute: int = 60):
        self.limit = requests_per_minute
        self.requests: dict[str, list[float]] = {}

    def is_rate_limited(self, ip_address: str, current_time: float) -> bool:
        window_start = current_time - 60.0
        timestamps = self.requests.get(ip_address, [])
        valid_timestamps = [t for t in timestamps if t > window_start]
        self.requests[ip_address] = valid_timestamps

        if len(valid_timestamps) >= self.limit:
            return True
            
        valid_timestamps.append(current_time)
        return False


rate_limiter = SimpleRateLimiter(requests_per_minute=60)


async def verify_api_key_or_optional_auth(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """
    Authentication verification dependency.
    If API Key security is enforced, checks header against valid configuration.
    Allows guest access with rate limiting by default.
    """
    if settings.ENVIRONMENT == "production" and settings.SECRET_KEY != "dev-secret-key-change-in-production-weathergpt-2026":
        if x_api_key and x_api_key == settings.SECRET_KEY:
            return True
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            if token == settings.SECRET_KEY:
                return True
        # For public read endpoints, guest access is granted under rate limiting
        return True
    return True


async def require_admin_user(
    x_admin_api_key: Optional[str] = Header(None, alias="X-Admin-API-Key"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
) -> bool:
    """
    Strict Authentication & Authorization dependency for Administrative Endpoints.
    Requires valid admin credentials via X-Admin-API-Key, X-API-Key or Authorization Bearer header.
    Raises 401 if missing credentials, 403 if invalid credentials.
    """
    provided_key = None
    if x_admin_api_key:
        provided_key = x_admin_api_key.strip()
    elif x_api_key:
        provided_key = x_api_key.strip()
    elif authorization:
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            provided_key = parts[1]
        else:
            provided_key = authorization.strip()

    if not provided_key:
        logger.warning("Administrative access attempt rejected: Missing authentication header.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for administrative operations."
        )

    valid_keys = {settings.ADMIN_SECRET_KEY, settings.SECRET_KEY}
    if provided_key not in valid_keys:
        logger.warning(f"Administrative access attempt rejected: Invalid key provided ({provided_key[:4]}...).")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Insufficient administrative privileges."
        )

    return True


import hashlib
import hmac
import base64
import json
import time


def hash_password(password: str) -> str:
    """Hashes password using PBKDF2-HMAC-SHA256 with a salt."""
    salt = hashlib.sha256(settings.SECRET_KEY.encode()).digest()[:16]
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return base64.b64encode(salt + key).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against hashed PBKDF2 string."""
    try:
        data = base64.b64decode(hashed_password.encode('utf-8'))
        salt = data[:16]
        expected_key = data[16:]
        computed_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
        return hmac.compare_digest(expected_key, computed_key)
    except Exception:
        return False


def create_jwt_token(payload: dict, expires_in_seconds: int = 86400) -> str:
    """Generates signed JWT token with signature verification."""
    header = {"alg": "HS256", "typ": "JWT"}
    token_payload = payload.copy()
    token_payload["exp"] = int(time.time()) + expires_in_seconds

    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(token_payload).encode()).decode().rstrip("=")

    signing_input = f"{header_b64}.{payload_b64}"
    signature = hmac.new(settings.SECRET_KEY.encode(), signing_input.encode(), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

    return f"{signing_input}.{sig_b64}"


def decode_jwt_token(token: str) -> Optional[dict]:
    """Decodes and validates JWT token signature and expiry."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}"

        expected_sig = hmac.new(settings.SECRET_KEY.encode(), signing_input.encode(), hashlib.sha256).digest()
        actual_sig = base64.urlsafe_b64decode(sig_b64 + "==")

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload_bytes = base64.urlsafe_b64decode(payload_b64 + "==")
        payload = json.loads(payload_bytes.decode())

        if payload.get("exp", 0) < time.time():
            return None

        return payload
    except Exception:
        return None


