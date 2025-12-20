from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.auth import auth_router, me_router, users_router, roles_router
from db.init import db_init

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_init()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(me_router)
app.include_router(users_router)
app.include_router(roles_router)

# raise HTTPException(
#     status_code=status.HTTP_401_UNAUTHORIZED,
#     detail="Invalid credentials"
# )

@app.get('/ping')
def ping():

    return {'ok': True}
