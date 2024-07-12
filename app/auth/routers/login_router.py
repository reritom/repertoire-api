from fastapi import APIRouter, Depends

from app.auth.routers.dependencies import unauthenticated_user_required
from app.auth.schemas.login_schema import LoginResponseSchema, LoginSchema
from app.auth.services.auth_service.service import login_user
from app.database import SessionType, get_session

router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponseSchema,
    status_code=201,
    dependencies=[Depends(unauthenticated_user_required)],
)
def login(
    user_credentials: LoginSchema,
    session: SessionType = Depends(get_session),
):
    token, expires = login_user(session=session, user_credentials=user_credentials)
    return LoginResponseSchema(token=token, expires=expires)
