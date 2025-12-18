from fastapi import APIRouter, status
from schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED
)
def register(data: RegisterRequest):
    # TODO првоерить email
    # TODO хешировать пароль
    # TODO добавить польщователя в бд
    return {"id": 1, "email": data.email}

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(data: LoginRequest):
    # TODO проверить польщователя
    # TODO проверить пароль
    # TODO создать токен
    return {"access_token": "jwt_token"}
