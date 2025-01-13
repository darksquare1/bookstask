import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from datetime import date
from app.db.database import get_db
from app.db.models import User, Book, Author, Genre, Role
from utils.security import hash_password


def fill_database():
    with next(get_db()) as db:
        genre1 = Genre(name="Fiction")
        genre2 = Genre(name="Science Fiction")
        genre3 = Genre(name="Fantasy")

        author1 = Author(name="Author 1", biography="Biography of Author 1", birth_date=date(1970, 5, 1))
        author2 = Author(name="Author 2", biography="Biography of Author 2", birth_date=date(1980, 8, 12))

        book1 = Book(title="Book 1", description="Description of Book 1", publication_date=date(2000, 1, 1),
                     available_copies=5)
        book2 = Book(title="Book 2", description="Description of Book 2", publication_date=date(2005, 6, 15),
                     available_copies=3)

        user1 = User(username="admin", email="admin@example.com", hashed_password=hash_password("hashedpassword"),
                     role=Role.ADMIN)
        user2 = User(username="reader1", email="reader1@example.com", hashed_password=hash_password("hashedpassword"),
                     role=Role.READER)
        user3 = User(username="reader2", email="reader2@example.com", hashed_password=hash_password("hashedpassword"),
                     role=Role.READER)

        book1.genres.append(genre1)
        book1.genres.append(genre2)
        book2.genres.append(genre3)

        author1.books.append(book1)
        author2.books.append(book2)

        db.add_all([genre1, genre2, genre3, author1, author2, book1, book2, user1, user2, user3])

        db.commit()

        print("Database has been filled with test data.")


if __name__ == "__main__":
    fill_database()
