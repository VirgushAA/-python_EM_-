from fastapi import FastAPI, HTTPException, status, requests
from api.auth import router as auth_router, router

app = FastAPI()

app.include_router(auth_router)
# app.include_router(router)

# raise HTTPException(
#     status_code=status.HTTP_401_UNAUTHORIZED,
#     detail="Invalid credentials"
# )

@app.get('/ping')
def ping():
    return {'ok': True}

