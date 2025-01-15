from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from app.api import schemas
from app.db import models
from app.db.database import get_db
from utils.security import RoleVerify

books_router = APIRouter()


@books_router.get('', response_model=Page[schemas.BookOut])
def get_books(depends_on=Depends(RoleVerify(['admin', 'reader'])), db: Session = Depends(get_db), size: int = 10):
    books = db.query(models.Book).all()
    if not books:
        raise HTTPException(status_code=404, detail='Books not found')

    return paginate([
        schemas.BookOut(
            id=book.id,
            title=book.title,
            description=book.description,
            publication_date=book.publication_date,
            available_copies=book.available_copies,
            genres=[genre.name for genre in book.genres],
            authors=[author.name for author in book.authors]
        )
        for book in books
    ])


@books_router.post('', response_model=schemas.BookOut)
def create_book(book: schemas.BookCreate, depends_on=Depends(RoleVerify(['admin'])), db: Session = Depends(get_db)):
    authors = db.query(models.Author).filter(models.Author.name.in_(book.authors)).all()
    genres = db.query(models.Genre).filter(models.Genre.name.in_(book.genres)).all()

    if len(authors) != len(book.authors):
        raise HTTPException(status_code=400, detail="Some authors do not exist")
    if len(genres) != len(book.genres):
        raise HTTPException(status_code=400, detail="Some genres do not exist")
    new_book = models.Book(
        title=book.title,
        description=book.description,
        publication_date=book.publication_date,
        available_copies=book.available_copies,
        authors=authors,
        genres=genres
    )
    db.add(new_book)
    db.commit()
    return schemas.BookOut(
        id=new_book.id,
        title=new_book.title,
        description=new_book.description,
        publication_date=new_book.publication_date,
        available_copies=new_book.available_copies,
        genres=[genre.name for genre in new_book.genres],
        authors=[author.name for author in new_book.authors]
    )


@books_router.put('/{book_id}', response_model=schemas.BookOut)
def update_book(book_id: int, book: schemas.BookUpdate, depends_on=Depends(RoleVerify(['admin'])),
                db: Session = Depends(get_db)):
    existing_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not existing_book:
        raise HTTPException(status_code=404, detail='Book not found')

    fields_to_update = ["title", "description", "publication_date", "available_copies"]
    for field in fields_to_update:
        value = getattr(book, field, None)
        if value is not None:
            setattr(existing_book, field, value)
    if book.genres:
        genres = db.query(models.Genre).filter(models.Genre.name.in_(book.genres)).all()
        if len(genres) != len(book.genres):
            raise HTTPException(status_code=400, detail="Some genres do not exist")
        existing_book.genres = genres
    if book.authors:
        authors = db.query(models.Author).filter(models.Author.name.in_(book.authors)).all()
        if len(authors) != len(book.authors):
            raise HTTPException(status_code=400, detail="Some authors do not exist")
        existing_book.authors = authors

    db.commit()
    return schemas.BookOut(
        id=existing_book.id,
        title=existing_book.title,
        description=existing_book.description,
        publication_date=existing_book.publication_date,
        available_copies=existing_book.available_copies,
        genres=[genre.name for genre in existing_book.genres],
        authors=[author.name for author in existing_book.authors]
    )


@books_router.delete('/{book_id}', response_model=schemas.BookOut)
def delete_book(book_id: int, depends_on=Depends(RoleVerify(['admin'])), db: Session = Depends(get_db)):
    existing_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not existing_book:
        raise HTTPException(status_code=404, detail='Book not found')
    db.delete(existing_book)
    db.commit()
    return schemas.BookOut(
        id=existing_book.id,
        title=existing_book.title,
        description=existing_book.description,
        publication_date=existing_book.publication_date,
        available_copies=existing_book.available_copies,
        genres=[genre.name for genre in existing_book.genres],
        authors=[author.name for author in existing_book.authors]
    )
