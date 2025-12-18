from fastapi import FastAPI, HTTPException, status, requests
from api.auth import router as auth_router, router
from db.init import db_init

app = FastAPI()

@app.on_event('startup')
def startup():
    db_init()

app.include_router(auth_router)
# app.include_router(router)

# raise HTTPException(
#     status_code=status.HTTP_401_UNAUTHORIZED,
#     detail="Invalid credentials"
# )

@app.get('/ping')
def ping():
    return {'ok': True}

