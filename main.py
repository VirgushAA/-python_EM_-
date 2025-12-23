from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.auth import auth_router, me_router, users_router, post_router
from db.init import db_init
from db.sessions import SessionLocal
from misc.db_seed import seed_roles_permissions_and_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_init()
    db = SessionLocal()
    try:
        seed_roles_permissions_and_users(db)
    finally:
        db.close()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(me_router)
app.include_router(users_router)
app.include_router(post_router)

@app.get('/ping')
def ping():

    return {'ok': True}
