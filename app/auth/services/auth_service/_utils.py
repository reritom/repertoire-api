from datetime import datetime
from typing import Optional

import jwt


def create_access_token(
    expires: datetime,
    secret_key: str,
    user_id: int,
) -> str:
    payload = {
        "exp": expires,
        "iat": datetime.utcnow(),
        "sub": user_id,
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")


def decode_access_token(
    token: str, secret_key: str, raise_exc: bool = False
) -> Optional[dict]:
    try:
        return jwt.decode(token, secret_key, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        if raise_exc:
            raise
