import os
from datetime import datetime, timedelta, timezone
from typing import Any, cast
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

JWT_ALG = "HS256"
ACCESS_TTL_MIN = int(os.getenv("ACCESS_TTL_MIN", "15"))
REFRESH_TTL_DAYS = int(os.getenv("REFRESH_TTL_DAYS", "21"))
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME_SUPER_SECRET")


def get_password_hash(password: str) -> str:
    hashed = pwd_context.hash(password)
    return cast(str, hashed)


def verify_password(plain: str, hashed: str) -> bool:
    ok = pwd_context.verify(plain, hashed)
    return cast(bool, ok)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(
    sub: str, *, extra: dict[str, Any] | None = None
) -> tuple[str, int]:
    exp = now_utc() + timedelta(minutes=ACCESS_TTL_MIN)
    payload: dict[str, Any] = {
        "sub": sub,
        "exp": exp,
        "jti": str(uuid4()),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    token: str = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return token, ACCESS_TTL_MIN * 60


def create_refresh_token(sub: str) -> tuple[str, str, datetime]:
    exp = now_utc() + timedelta(days=REFRESH_TTL_DAYS)
    jti = str(uuid4())
    payload: dict[str, Any] = {"sub": sub, "exp": exp, "jti": jti, "type": "refresh"}
    token: str = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return token, jti, exp


def decode_token(token: str) -> dict[str, Any]:
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return cast(dict[str, Any], decoded)
    except JWTError as e:
        raise ValueError("Invalid token") from e
