import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from main import app
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.TEST_DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope='function')
def db():
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
        Base.metadata.drop_all(bind=engine)


def override_get_db():
    with TestingSessionLocal() as db:
        yield db


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_register_and_login(db):
    user_data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword',
    }
    response = client.post('/register', json=user_data)
    assert response.status_code == 200
    assert response.json() == {'details': 'Successfully registered!'}

    login_data = {'username': 'testuser', 'password': 'testpassword'}
    response = client.post('/login', json=login_data)
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'bearer'

    login_data_invalid = {'username': 'testuser', 'password': 'wrongpassword'}
    response = client.post('/login', json=login_data_invalid)
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid username or password'
