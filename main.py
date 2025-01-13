import uvicorn
from fastapi import FastAPI

from app.api.endpoints.book import books_router
from app.api.endpoints.user import auth_router

app = FastAPI()
app.include_router(auth_router, tags=["auth"])
app.include_router(books_router, prefix='/books', tags=['books'])

if __name__ == '__main__':
    uvicorn.run(app='main:app')
