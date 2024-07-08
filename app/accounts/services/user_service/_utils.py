from werkzeug.security import check_password_hash as _check_password_hash
from werkzeug.security import generate_password_hash as _generate_password_hash


def hash_password(password: str) -> str:
    return _generate_password_hash(password)


def check_password(password: str, hashed_password: str) -> bool:
    return _check_password_hash(pwhash=hashed_password, password=password)
