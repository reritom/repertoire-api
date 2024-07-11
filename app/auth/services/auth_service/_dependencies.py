from app.settings import settings


def get_authentication_secret_key() -> str:
    return settings.AUTH_SECRET_KEY


def get_access_token_lifespan_minutes() -> int:
    return settings.ACCESS_TOKEN_LIFESPAN_MINUTES
