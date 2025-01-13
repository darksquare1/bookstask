from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register_and_login(db):
    """
    Функция, которая тестирует регистрацию и авторизацию пользователя по jwt
    """
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
