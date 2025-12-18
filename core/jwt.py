from datetime import datetime, timedelta
# from jose import jwt

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(user_id: int):
    payload = {
        'sub': str(user_id),
        'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    # return jwt.encode(payload, SECRET_KEY, ALGORITHM)
    return 'placeholder_string'
