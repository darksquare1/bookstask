import uvicorn
from fastapi import FastAPI

from app.api.endpoints.book import books_router
from app.api.endpoints.bookloans import loan_router
from app.api.endpoints.genres import genres_router
from app.api.endpoints.user import auth_router

app = FastAPI()
app.include_router(auth_router, tags=["auth"])
app.include_router(genres_router, prefix='/genres', tags=['genres'])
app.include_router(books_router, prefix='/books', tags=['books'])
app.include_router(loan_router, prefix='/loans', tags=['loans'])

if __name__ == '__main__':
    uvicorn.run(app='main:app')
