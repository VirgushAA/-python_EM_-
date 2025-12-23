# from urllib.request import Request

from fastapi import APIRouter, status, Depends, HTTPException, Request
from schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse, UpdateMeRequest, UserOut
from sqlalchemy.orm import Session
from db.sessions import SessionLocal
from models.user import User, Role, Permission
from core.security import hash_password, verify_password
from core.jwt import create_access_token, decode_access_token

auth_router = APIRouter(prefix='/auth', tags=['auth'])
me_router = APIRouter(prefix='/me', tags=['me'])
users_router = APIRouter(prefix='/users', tags=['users'])
post_router = APIRouter(prefix='/post', tags=['post'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- auth router

@auth_router.post(
    '/register',
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED
)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    exist = db.query(User).filter(User.email == data.email).first()
    if exist:
        raise HTTPException(409, 'Email already registered.')

    role_user = db.query(Role).filter(Role.name == "user").first()

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        is_active=True
    )

    if role_user:
        user.roles.append(role_user)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "email": user.email}

@auth_router.post(
    '/login',
    response_model=TokenResponse
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, 'Invalid credentials.')
    if not user.is_active:
        raise HTTPException(403, 'User account is inactive or deactivated')

    token = create_access_token(user.id)

    return {"access_token": token}

@auth_router.get('/show')
def show(db: Session = Depends(get_db)):
    output = db.query(User).all()
    print(output)
    return {'ok': 1}

@auth_router.post("/logout")
def logout():
    return {'Client should delete token'}

# ----------------------------------------------

def get_bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(401, 'Authorization header missing')

    auth_string = auth.split()
    if len(auth_string) != 2:
        raise HTTPException(401, 'Invalid Authorization header')

    scheme, token = auth_string
    if scheme.lower() != "bearer":
        raise HTTPException(401, 'Invalid auth scheme')

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

def require_permission(code: str):
    def checker(user: User = Depends(get_current_user)):
        for role in user.roles:
            for permission in role.permissions:
                if permission.code == code:
                    return user
        raise HTTPException(403, 'Forbidden')
    return checker

# ---------- user router

@users_router.get(
    '/',
    dependencies=[Depends(require_role('admin'))],
    response_model=list[UserOut]
)
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@users_router.patch(
    '/{user_id}/roles/{role_id}',
    dependencies=[Depends(require_role('admin'))]
)
def assign_role(user_id: int, role_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, 'User not found')

    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(404, 'Role not found')

    if role in user.roles:
        return {'detail': 'Role already assigned'}

    user.roles.append(role)
    db.commit()

    return {'detail': f"Role '{role.name}' assigned to user {user.id}"}

@users_router.delete(
    '/deactivate/{user_id}',
    dependencies=[Depends(require_role('admin'))]
)
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise  HTTPException(404, 'User not found')
    if not user.is_active:
        return {'detail': f"User {user_id} is allready deactivated"}

    user.is_active = False
    db.commit()
    return {'detail': f"User {user_id} has deactivated"}

@users_router.get(
    '/debug/all',
    dependencies=[Depends(require_role('admin'))]
)
def show_all(db: Session = Depends(get_db)):
    return {
        'users': [
            {
                'id': u.id,
                'email': u.email,
                'roles': [r.name for r in u.roles],
                'is_active': u.is_active
            }
            for u in db.query(User).all()
        ],
        'roles': [
            {
                'id': r.id,
                'name': r.name,
                'permissions': [p.code for p in r.permissions],
            }
            for r in db.query(Role).all()
        ],
        'permissions': [
            {
                'id': p.id,
                'code': p.code,
                'resource': p.resource,
                'action': p.action,
            }
            for p in db.query(Permission).all()
        ],
    }

# -------- me router

@me_router.get('/', response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user

@me_router.delete('/')
def delete_me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    user.is_active = False
    db.commit()
    return {'detail': 'User deactivated'}

@me_router.patch('/')
def update_me(
        data: UpdateMeRequest,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    if data.email:
        user.email = data.email
    if data.name:
        user.name = data.name
    if data.password:
        user.password_hash = hash_password(data.password)

    db.commit()
    return {'detail': 'Updated'}

# ======================= post router

@post_router.get(
    '/{post_id}',
    dependencies=[Depends(require_permission('post.read'))]
)
def read_post(post_id: int):
    return {
        'id': post_id,
        'title': 'Mock post',
        'content': 'Lorem Ipsum'
    }

@post_router.patch(
    '/{post_id}',
    dependencies=[Depends(require_permission('post.update'))]
)
def update_post(post_id: int, data: dict):
    return {
        'detail': f"Post {post_id} updated",
        'changes': data
    }

@post_router.post(
    '/',
    dependencies=[Depends(require_permission('post.create'))]
)
def create_post(data: dict):
    return {
        'id': 123,
        'detail': 'Post created',
        'contend': data
    }

@post_router.delete(
    '/{post_id}',
    dependencies=[Depends(require_permission('post.delete'))]
)
def delete_post(post_id: int):
    return {'detail': f"Post {post_id} has been deleted."}
