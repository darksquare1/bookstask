from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from app.api import schemas
from app.db import models
from app.db.database import get_db
from utils.security import RoleVerify

authors_router = APIRouter()


@authors_router.get('', response_model=Page[schemas.AuthorGet])
def get_authors(depends_on=Depends(RoleVerify(['admin', 'reader'])), db: Session = Depends(get_db)):
    authors = db.query(models.Author).all()
    if not authors:
        raise HTTPException(status_code=404, detail='Authors not found')

    return paginate([
        schemas.AuthorGet(
            id=author.id,
            name=author.name,
            biography=author.biography,
            birth_date=author.birth_date
        )
        for author in authors
    ])


@authors_router.post('', response_model=schemas.AuthorGet)
def create_author(author: schemas.AuthorPost, depends_on=Depends(RoleVerify(['admin'])), db: Session = Depends(get_db)):
    new_author = models.Author(
        name=author.name,
        biography=author.biography,
        birth_date=author.birth_date
    )
    db.add(new_author)
    db.commit()
    return schemas.AuthorGet(
        id=new_author.id,
        name=new_author.name,
        biography=new_author.biography,
        birth_date=new_author.birth_date
    )


@authors_router.put('/{author_id}', response_model=schemas.AuthorGet)
def update_author(author_id: int, author: schemas.AuthorPost, depends_on=Depends(RoleVerify(['admin'])),
                  db: Session = Depends(get_db)):
    existing_author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not existing_author:
        raise HTTPException(status_code=404, detail='Author not found')

    fields_to_update = ["name", "biography", "birth_date"]
    for field in fields_to_update:
        value = getattr(author, field, None)
        if value is not None:
            setattr(existing_author, field, value)

    db.commit()
    return schemas.AuthorGet(
        id=existing_author.id,
        name=existing_author.name,
        biography=existing_author.biography,
        birth_date=existing_author.birth_date
    )


@authors_router.delete('/{author_id}', response_model=schemas.AuthorGet)
def delete_author(author_id: int, depends_on=Depends(RoleVerify(['admin'])), db: Session = Depends(get_db)):
    existing_author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not existing_author:
        raise HTTPException(status_code=404, detail='Author not found')
    db.delete(existing_author)
    db.commit()
    return schemas.AuthorGet(
        id=existing_author.id,
        name=existing_author.name,
        biography=existing_author.biography,
        birth_date=existing_author.birth_date
    )
