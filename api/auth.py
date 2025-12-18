from os.path import exists

from fastapi import APIRouter, status, Depends, HTTPException
from schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse
from sqlalchemy.orm import Session
from db.sessions import SessionLocal
from models.user import User
from core.security import hash_password, verify_password
from core.jwt import create_access_token

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
