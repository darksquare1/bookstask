from fastapi.testclient import TestClient
from app.db import models
from main import app
from tests.utils import create_test_user
from utils.security import create_access_token

client = TestClient(app)


def test_get_genres_as_reader(db):
    """
    Функция тестирующая маршрут просмотра жанров в роли читателя (доступ запрещен).
    """
    genre = models.Genre(name='Science Fiction')
    db.add(genre)
    db.commit()
    user = create_test_user(db)
    token = create_access_token(data={'sub': user.username, 'role': 'reader'})
    response = client.get('/genres', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 401


def test_create_genre_as_admin(db):
    """
    Функция тестирующая маршрут создания жанра в роли админа
    """
    genre_data = {'name': 'Mystic'}
    user = create_test_user(db)
    token = create_access_token(data={'sub': user.username, 'role': 'admin'})

    response = client.post('/genres', json=genre_data, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json()['name'] == genre_data['name']


def test_create_genre_as_reader_forbidden(db):
    """
    Функция тестирующая маршрут создания жанра в роли читателя (доступ запрещен).
    """
    genre_data = {'name': 'Horror'}
    token = create_access_token(data={'sub': 'testuser', 'role': 'reader'})

    response = client.post('/genres', json=genre_data, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 401
    assert response.json().get('detail') == 'Access denied. Required roles: admin'


def test_update_genre_as_admin(db):
    """
    Функция тестирующая маршрут обновления имени жанра в роли админа.
    """
    genre = models.Genre(name='Mystery')
    db.add(genre)
    db.commit()

    updated_data = {'name': 'Thriller'}
    user = create_test_user(db)
    token = create_access_token(data={'sub': user.username, 'role': 'admin'})

    response = client.put(f'/genres/{genre.id}', json=updated_data, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert response.json()['name'] == updated_data['name']


def test_update_genre_as_reader_forbidden(db):
    """
    Функция тестирующая маршрут обновления имени жанра в роли читателя (доступ запрещен).
    """
    genre = models.Genre(name='Romance')
    db.add(genre)
    db.commit()

    updated_data = {'name': 'Comedy'}
    token = create_access_token(data={'sub': 'testuser', 'role': 'reader'})

    response = client.put(f'/genres/{genre.id}', json=updated_data, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 401
    assert response.json()['detail'] == 'Access denied. Required roles: admin'


def test_delete_genre_as_admin(db):
    """
    Функция тестирующая маршрут удаления жанра в роли админа.
    """
    genre = models.Genre(name='Action')
    db.add(genre)
    db.commit()
    user = create_test_user(db)
    token = create_access_token(data={'sub': user.username, 'role': 'admin'})

    response = client.delete(f'/genres/{genre.id}', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert response.json()['name'] == genre.name
    deleted_genre = db.query(models.Genre).filter(models.Genre.id == genre.id).first()
    assert deleted_genre is None


def test_delete_genre_as_reader_forbidden(db):
    """
    Функция тестирующая маршрут удаления жанра в роли читателя(доступ запрещен).
    """
    genre = models.Genre(name='Adventure')
    db.add(genre)
    db.commit()

    token = create_access_token(data={'sub': 'testuser', 'role': 'reader'})

    response = client.delete(f'/genres/{genre.id}', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 401
    assert response.json()['detail'] == 'Access denied. Required roles: admin'


def test_delete_non_existent_genre(db):
    """
    Функция тестирующая маршрут удаления несуществующего жанра в роли админа.
    """
    user = create_test_user(db)
    token = create_access_token(data={'sub': user.username, 'role': 'admin'})

    response = client.delete('/genres/9999', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 404
    assert response.json()['detail'] == 'Genre not found'
