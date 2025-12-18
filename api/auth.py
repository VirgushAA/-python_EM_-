from urllib.request import Request

from fastapi import APIRouter, status, Depends, HTTPException
from schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse
from sqlalchemy.orm import Session
from db.sessions import SessionLocal
from models.user import User
from core.security import hash_password, verify_password
from core.jwt import create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED
)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    exist = db.query(User).filter(User.email == data.email).first()
    if exist:
        raise HTTPException(409, 'Email already registered.')

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "email": user.email}

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, 'Invalid credentials.')

    token = create_access_token(user.id)

    return {"access_token": token}

@router.get("/show")
def show(db: Session = Depends(get_db)):
    output = db.query(User).all()
    print(output)
    return {"ok": 1}


def get_bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(401, "Authorization header missing")

    scheme, token = auth.split()
    if scheme.lower() != "bearer":
        raise HTTPException(401, "Invalid auth scheme")

    return token

def get_current_user(
        token: str = Depends(get_bearer_token),
        db: Session = Depends(get_db)
):

    payload = decode_access_token(token)
    user_id = payload.get('sub')

    if user_id is None:
        raise HTTPException(401, 'invalid token')

    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None or not user.is_active:
        raise HTTPException(401, 'User not found or inactive.')

    return user


def require_role(role_name: str):
    def checker(user: User = Depends(get_current_user)):
        if role_name not in [r.name for r in user.roles]:
            raise HTTPException(403, 'Forbidden')
        return user
    return checker


