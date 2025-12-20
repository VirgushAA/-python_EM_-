from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    name: str | None = None
    email: EmailStr
    password: str

class RegisterResponse(BaseModel):
    id: int
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UpdateMeRequest(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    name: str | None = None

class RoleOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    is_active: bool
    roles: list[RoleOut]

    class Config:
        from_attributes = True
