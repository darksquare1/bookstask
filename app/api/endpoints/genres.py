from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import schemas
from app.db import models
from app.db.database import get_db
from utils.security import RoleVerify

genres_router = APIRouter()


@genres_router.get('', response_model=list[schemas.GenreGet])
def get_genres(depends_on=Depends(RoleVerify(['admin'])), db: Session = Depends(get_db)):
    genres = db.query(models.Genre).all()
    if not genres:
        raise HTTPException(status_code=404, detail='Books not found')

    return [
        schemas.GenreGet(
            id=genre.id,
            name=genre.name
        )
        for genre in genres
    ]


@genres_router.post('', response_model=schemas.GenrePost)
def create_genre(genre: schemas.GenrePost, depends_on=Depends(RoleVerify(['admin'])), db: Session = Depends(get_db)):
    if db.query(models.Genre).filter_by(name=genre.name).all():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'{genre.name} already exists')
    new_genre = models.Genre(
        name=genre.name,
    )

    db.add(new_genre)
    db.commit()
    db.refresh(new_genre)
    return schemas.GenreGet(id=new_genre.id, name=new_genre.name)


@genres_router.put('/{genre_id}', response_model=schemas.GenreGet)
def update_genre(genre_id: int, genre: schemas.GenrePost, depends_on=Depends(RoleVerify(['admin'])),
                 db: Session = Depends(get_db)):
    existing_genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not existing_genre:
        raise HTTPException(status_code=404, detail='Genre not found')

    existing_genre.name = genre.name

    db.commit()
    db.refresh(existing_genre)
    return schemas.GenreGet(
        name=existing_genre.name,
        id=existing_genre.id
    )


@genres_router.delete('/{genre_id}', response_model=schemas.GenreGet)
def delete_genre(genre_id: int, depends_on=Depends(RoleVerify(['admin'])), db: Session = Depends(get_db)):
    existing_genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not existing_genre:
        raise HTTPException(status_code=404, detail='Genre not found')
    db.delete(existing_genre)
    db.commit()
    return schemas.GenreGet(
        name=existing_genre.name,
        id=existing_genre.id
    )
