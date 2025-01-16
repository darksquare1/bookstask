from fastapi.testclient import TestClient
from app.db import models
from main import app
from tests.utils import create_test_user
from utils.security import create_access_token

client = TestClient(app)


def test_get_authors_as_reader(db):
    """
    Тест для получения списка авторов в роли читателя.
    """
    author = models.Author(name='J.K. Rowling', biography='Famous author', birth_date='1965-07-31')
    db.add(author)
    db.commit()
    user = create_test_user(db)
    token = create_access_token(data={'sub': user.username, 'role': 'reader'})
    response = client.get('/authors', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    authors = response.json()
    assert len(authors['items']) == 1
    assert authors['items'][0]['name'] == 'J.K. Rowling'


def test_create_author_as_admin(db):
    """
    Тест для создания нового автора в роли администратора.
    """
    author_data = {
        'name': 'George R.R. Martin',
        'biography': 'Author of A Song of Ice and Fire',
        'birth_date': '1948-09-20'
    }
    user = create_test_user(db)
    token = create_access_token(data={'sub': user.username, 'role': 'admin'})
    response = client.post('/authors', json=author_data, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    author = response.json()
    assert author['name'] == 'George R.R. Martin'
    assert author['biography'] == 'Author of A Song of Ice and Fire'


def test_create_author_as_reader_forbidden(db):
    """
    Тест для попытки создания автора в роли читателя (доступ запрещен).
    """
    author_data = {
        'name': 'New Author',
        'biography': 'New biography',
        'birth_date': '1980-01-01'
    }

    token = create_access_token(data={'sub': 'readeruser', 'role': 'reader'})
    response = client.post('/authors', json=author_data, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 401
    assert response.json()['detail'] == 'Access denied. Required roles: admin'


def test_update_author_as_admin(db):
    """
    Тест для обновления информации об авторе в роли администратора.
    """
    author = models.Author(name='J.K. Rowling', biography='Famous author', birth_date='1965-07-31')
    db.add(author)
    db.commit()

    updated_data = {
        'name': 'Joanne Rowling',
        'biography': 'Updated biography',
        'birth_date': '1965-07-31'
    }
    user = create_test_user(db)
    token = create_access_token(data={'sub': user.username, 'role': 'admin'})
    response = client.put(f'/authors/{author.id}', json=updated_data, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    updated_author = response.json()
    assert updated_author['name'] == 'Joanne Rowling'
    assert updated_author['biography'] == 'Updated biography'


def test_update_author_as_reader_forbidden(db):
    """
    Тест для попытки обновить информацию об авторе в роли читателя (доступ запрещен).
    """
    author = models.Author(name='J.K. Rowling', biography='Famous author', birth_date='1965-07-31')
    db.add(author)
    db.commit()

    updated_data = {
        'name': 'Joanne Rowling',
        'biography': 'Updated biography',
        'birth_date': '1965-07-31'
    }

    token = create_access_token(data={'sub': 'readeruser', 'role': 'reader'})
    response = client.put(f'/authors/{author.id}', json=updated_data, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 401  # Неавторизован
    assert response.json()['detail'] == 'Access denied. Required roles: admin'


def test_delete_author_as_admin(db):
    """
    Тест для удаления автора в роли администратора.
    """
    author = models.Author(name='J.K. Rowling', biography='Famous author', birth_date='1965-07-31')
    db.add(author)
    db.commit()
    user = create_test_user(db)
    token = create_access_token(data={'sub': user.username, 'role': 'admin'})
    response = client.delete(f'/authors/{author.id}', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    deleted_author = response.json()
    assert deleted_author['name'] == 'J.K. Rowling'
    assert db.query(models.Author).filter(models.Author.id == author.id).first() is None


def test_delete_author_as_reader_forbidden(db):
    """
    Тест для попытки удалить автора в роли читателя (доступ запрещен).
    """
    author = models.Author(name='J.K. Rowling', biography='Famous author', birth_date='1965-07-31')
    db.add(author)
    db.commit()

    token = create_access_token(data={'sub': 'readeruser', 'role': 'reader'})
    response = client.delete(f'/authors/{author.id}', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 401  # Неавторизован
    assert response.json()['detail'] == 'Access denied. Required roles: admin'
