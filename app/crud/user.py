from sqlalchemy.orm import Session
from app.db.models import User
from utils.security import hash_password
from app.api.schemas import UserCreate

def create_user(db: Session, user: UserCreate):
    db_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if db_user:
        return None
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user