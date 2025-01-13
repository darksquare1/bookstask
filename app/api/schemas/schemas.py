from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


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

class GenrePost(BaseModel):
    name: str

class GenreGet(GenrePost):
    id: int