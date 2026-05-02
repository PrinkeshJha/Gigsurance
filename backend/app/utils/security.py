from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional, Dict, Any

from app.schemas.auth import TokenData
from app.config import settings

# -------------------------------

# PASSWORD HASHING CONFIG

# -------------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# -------------------------------

# PASSWORD HELPERS

# -------------------------------

def _truncate_password(password: str) -> str:
    """
    bcrypt supports max 72 bytes.
    """
    return password[:72]

def hash_password(password: str) -> str:
    if not password or not password.strip():
        raise ValueError("Password cannot be empty")

    password = _truncate_password(password)
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    if not password or not hashed_password:
        return False


    try:
        password = _truncate_password(password)
        return pwd_context.verify(password, hashed_password)
    except Exception:
        return False


# -------------------------------

# JWT HELPERS

# -------------------------------

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT token
    """
    if not isinstance(data, dict):
        raise ValueError("Token payload must be a dictionary")


    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=settings.jwt_exp_minutes)
    )

    # ✅ Add standard claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })

    token = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )

    return token


def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate JWT token
    """
    if not token:
        raise JWTError("Token is missing")


    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )

        pan: Optional[str] = payload.get("pan")
        role: Optional[str] = payload.get("role")

        if not pan:
            raise JWTError("Invalid token: missing PAN")

        return TokenData(pan=pan, role=role)

    except JWTError as e:
        raise JWTError(f"Invalid or expired token: {str(e)}")

