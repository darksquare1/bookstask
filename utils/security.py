import datetime
import jwt
from fastapi.security import OAuth2PasswordBearer
from typing import List
from fastapi import Depends, HTTPException
from starlette import status
from app.core.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, token_life_time: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=token_life_time)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Expired token')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    username = payload.get('sub')
    return username


class RoleVerify:
    def __init__(self, roles: List[str]):
        self.roles = roles

    def __call__(self, token: str = Depends(oauth2_scheme)):
        payload = verify_token(token)
        role = payload.get('role')
        if role not in self.roles:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Access denied. Required roles: {', '.join(self.roles)}"
            )
        return payload
