from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app.crud.user import create_user
from app.api import schemas
from app.db import models
from app.db.database import get_db
from utils.security import verify_password, create_access_token, RoleVerify

auth_router = APIRouter()


@auth_router.post('/register', response_model=schemas.UserCreate)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db=db, user=user)
    if not db_user:
        raise HTTPException(status_code=400, detail="Username or email already taken")
    return JSONResponse(content={'details': 'Successfully registered!'})


@auth_router.post('/login')
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail='Invalid username or password')
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid username or password')
    access_token = create_access_token(data={'sub': db_user.username, 'role': db_user.role.value})
    return {'access_token': access_token, 'token_type': 'bearer'}


@auth_router.put('/me', response_model=schemas.UserUpdate)
def change_user_info(user: schemas.UserUpdate, db: Session = Depends(get_db),
                     payload: dict = Depends(RoleVerify(['reader', 'admin']))):
    username = payload.get('sub')
    users = db.query(models.User).filter(models.User.email == user.email).first()
    if users:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Such email already exists')
    current_user = db.query(models.User).filter(models.User.username == username).first()
    current_user.email = user.email
    db.commit()
    return schemas.UserUpdate(email=current_user.email)
