from fastapi.testclient import TestClient
from app.db import models
from main import app
from utils.security import create_access_token

client = TestClient(app)


def test_get_books_as_reader(db):
    """
    Функция, тестирующая маршрут получения книг в роли читателя.
    """
    genre = models.Genre(name='Fiction')
    author = models.Author(name='Author One', biography='Bio', birth_date='1990-01-01')
    book = models.Book(
        title='Test Book',
        description='A test book description',
        publication_date='2023-01-01',
        available_copies=10,
        genres=[genre],
        authors=[author],
    )
    db.add(genre)
    db.add(author)
    db.add(book)
    db.commit()

    token = create_access_token(data={'sub': 'testuser', 'role': 'reader'})
    response = client.get('/books', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    books = response.json()
    assert len(books['items']) == 1
    assert books['items'][0]['title'] == 'Test Book'


def test_create_book_as_admin(db):
    """
    Функция, тестирующая маршрут создания книги в роли админа.
    """
    author = models.Author(name='Author Two', biography='Bio', birth_date='1985-01-01')
    db.add(author)
    db.commit()

    book_data = {
        'title': 'New Book',
        'description': 'A new book description',
        'publication_date': '2024-01-01',
        'available_copies': 5,
        'genres': ['Fiction'],
        'authors': ['Author Two'],
    }

    token = create_access_token(data={'sub': 'adminuser', 'role': 'admin'})
    response = client.post('/books', json=book_data, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    book = response.json()
    assert book['title'] == 'New Book'
    assert book['genres'] == ['Fiction']
    assert book['authors'] == ['Author Two']


def test_create_book_as_reader_forbidden(db):
    """
    Функция тестирующая маршрут создания книги в роли читателя (запрет на создание).
    """
    book_data = {
        'title': 'New Book',
        'description': 'A new book description',
        'publication_date': '2024-01-01',
        'available_copies': 5,
        'genres': ['Fiction'],
        'authors': ['Author Two'],
    }

    token = create_access_token(data={'sub': 'testuser', 'role': 'reader'})
    response = client.post('/books', json=book_data, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 401
    assert response.json()['detail'] == 'Access denied. Required roles: admin'


def test_delete_book_as_admin(db):
    """
    Функция тестирующая маршрут удаления книги в роли админа.
    """
    genre = models.Genre(name='Horror')
    author = models.Author(name='Author Four', biography='Bio', birth_date='1975-01-01')
    book = models.Book(
        title='Book to Delete',
        description='This book will be deleted',
        publication_date='2018-01-01',
        available_copies=1,
        genres=[genre],
        authors=[author],
    )
    db.add(genre)
    db.add(author)
    db.add(book)
    db.commit()

    token = create_access_token(data={'sub': 'adminuser', 'role': 'admin'})
    response = client.delete(f'/books/{book.id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    deleted_book = response.json()
    assert deleted_book['title'] == 'Book to Delete'
    assert db.query(models.Book).filter(models.Book.id == book.id).first() is None
