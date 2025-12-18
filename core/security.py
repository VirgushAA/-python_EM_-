from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

def hash_password(pwd: str) -> str:
    return pwd_context.hash(pwd)

def verify_password(pwd: str, hash_: str) -> bool:
    return pwd_context.verify(pwd, hash_)
