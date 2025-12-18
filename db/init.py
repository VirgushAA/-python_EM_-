from db.sessions import engine
from models.user import Base

def db_init():
    return Base.metadata.create_all(bind=engine)
