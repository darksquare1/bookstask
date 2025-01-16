from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.db import models
from main import app
from tests.utils import create_test_user
from utils.security import create_access_token

client = TestClient(app)


def test_borrow_book_as_reader(db):
    """
    Тест на возможность взять книгу в аренду как читателю.
    Проверяет, что пользователь может взять книгу, если у него нет
    ограничений по количеству арендованных книг.
    """
    genre = models.Genre(name='Science Fiction2')
    author = models.Author(name='Author One', biography='Bio', birth_date='1990-01-01')
    book = models.Book(
        title='Test Book',
        description='A test book description',
        publication_date='2023-01-01',
        available_copies=5,
        genres=[genre],
        authors=[author],
    )
    db.add(genre)
    db.add(author)
    db.add(book)
    db.commit()

    user = create_test_user(db)

    token = create_access_token(data={'sub': user.username, 'role': 'reader'})
    response = client.post(f'loans/borrow/{book.id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json()['book_id'] == book.id


def test_borrow_book_max_books(db):
    """
    Тест на попытку взять книгу, если пользователь уже взял 5 книг.
    Проверяет, что система не позволяет взять больше 5 книг одновременно.
    """
    genre = models.Genre(name='Fiction 2')
    author = models.Author(name='Author Two', biography='Bio', birth_date='1985-01-01')
    book = models.Book(
        title='Another Book',
        description='Another test book description',
        publication_date='2023-02-01',
        available_copies=5,
        genres=[genre],
        authors=[author],
    )
    db.add(genre)
    db.add(author)
    db.add(book)
    db.commit()

    user = create_test_user(db)

    for i in range(5):
        loan = models.BookLoan(
            user_id=user.id, book_id=book.id,
            issue_date=date.today(), estimated_return_date=date.today() + timedelta(days=14)
        )
        db.add(loan)
    db.commit()

    token = create_access_token(data={'sub': user.username, 'role': 'reader'})
    response = client.post(f'loans/borrow/{book.id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 400
    assert response.json()['detail'] == "You can't borrow more than 5 books at the same time."


def test_return_book_as_reader(db):
    """
    Тест на возврат книги как читателем.
    Проверяет, что пользователь может вернуть книгу, если она была арендована.
    """
    genre = models.Genre(name='Mystery 2')
    author = models.Author(name='Author Three', biography='Bio', birth_date='1980-01-01')
    book = models.Book(
        title='Book to Return',
        description='A book to test return',
        publication_date='2023-01-10',
        available_copies=2,
        genres=[genre],
        authors=[author],
    )
    db.add(genre)
    db.add(author)
    db.add(book)
    db.commit()

    user = create_test_user(db)

    loan = models.BookLoan(
        user_id=user.id, book_id=book.id,
        issue_date=date.today(), estimated_return_date=date.today() + timedelta(days=14)
    )
    db.add(loan)
    db.commit()

    token = create_access_token(data={'sub': user.username, 'role': 'reader'})
    response = client.post(f'loans/return/{loan.id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json()['actual_return_date'] is not None


def test_return_book_not_borrowed(db):
    """
    Тест на возврат книги, которую пользователь не арендовал.
    Проверяет, что система не позволяет вернуть книгу, которая не была взята пользователем.
    """
    genre = models.Genre(name='Thriller 2')
    author = models.Author(name='Author Four', biography='Bio', birth_date='1970-01-01')
    book = models.Book(
        title='Another Book to Return',
        description='A book not borrowed by the user',
        publication_date='2022-01-01',
        available_copies=3,
        genres=[genre],
        authors=[author],
    )
    db.add(genre)
    db.add(author)
    db.add(book)
    db.commit()

    user = create_test_user(db)

    token = create_access_token(data={'sub': user.username, 'role': 'reader'})
    response = client.post(f'loans/return/{9999}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 404
    assert response.json()['detail'] == "Loan not found or this loan does not belong to you."


def test_get_my_loans(db):
    """
    Тест на получение списка арендованных книг пользователем.
    Проверяет, что система возвращает правильный список арендованных книг.
    """
    genre = models.Genre(name='Fantasy 2')
    author = models.Author(name='Author Five', biography='Bio', birth_date='1992-01-01')
    book = models.Book(
        title='Book to Get',
        description='Book to test getting loans',
        publication_date='2021-01-01',
        available_copies=3,
        genres=[genre],
        authors=[author],
    )
    db.add(genre)
    db.add(author)
    db.add(book)
    db.commit()

    user = create_test_user(db)

    loan = models.BookLoan(
        user_id=user.id, book_id=book.id,
        issue_date=date.today(), estimated_return_date=date.today() + timedelta(days=14)
    )
    db.add(loan)
    db.commit()

    token = create_access_token(data={'sub': user.username, 'role': 'reader'})
    response = client.get('loans/my', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['book_id'] == book.id


def test_remove_loan_as_admin(db):
    """
    Тест на удаление аренды книги администратором.
    Проверяет, что администратор может удалить аренду книги.
    """
    genre = models.Genre(name='Non-fiction 2')
    author = models.Author(name='Author Six', biography='Bio', birth_date='2000-01-01')
    book = models.Book(
        title='Book to Remove',
        description='A book for removing loans',
        publication_date='2020-01-01',
        available_copies=5,
        genres=[genre],
        authors=[author],
    )
    db.add(genre)
    db.add(author)
    db.add(book)
    db.commit()

    user = create_test_user(db)

    loan = models.BookLoan(
        user_id=user.id, book_id=book.id,
        issue_date=date.today(), estimated_return_date=date.today() + timedelta(days=14)
    )
    db.add(loan)
    db.commit()
    user = create_test_user(db)
    token = create_access_token(data={'sub': user.username, 'role': 'admin'})
    response = client.delete(f'loans/remove/{loan.id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json()['loan_id'] == loan.id
    assert db.query(models.BookLoan).filter(models.BookLoan.id == loan.id).first() is None
