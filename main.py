import uvicorn
from fastapi import FastAPI

from app.api.endpoints.user import auth_router

app = FastAPI()
app.include_router(auth_router, tags=["auth"])

if __name__ == '__main__':
    uvicorn.run(app='main:app')
