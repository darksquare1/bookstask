from datetime import date
from typing import Optional
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class BookBase(BaseModel):
    title: str
    description: Optional[str] = None
    publication_date: Optional[date] = None
    available_copies: int

    @field_validator('available_copies', mode='before')
    @classmethod
    def validate_available_copies(cls, value: int) -> int:
        if value < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Field available copies must be a non negative integer')
        return value


class BookCreate(BookBase):
    genres: list[str]
    authors: list[str]


class BookOut(BookBase):
    id: int
    genres: list[str]
    authors: list[str]


class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    publication_date: Optional[date] = None
    available_copies: Optional[int] = None
    genres: Optional[list[str]] = None
    authors: Optional[list[str]] = None


class GenrePost(BaseModel):
    name: str


class GenreGet(GenrePost):
    id: int


class BookLoanOut(BaseModel):
    loan_id: int
    user_id: int
    book_id: int
    issue_date: date
    estimated_return_date: date
    actual_return_date: Optional[date]


class AuthorPost(BaseModel):
    name: str
    biography: Optional[str] = None
    birth_date: Optional[date] = None


class AuthorGet(AuthorPost):
    id: int
