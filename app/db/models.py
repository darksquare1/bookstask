from sqlalchemy import String, Integer, Date, ForeignKey, Text, BigInteger, Table, Column, Enum as AlchEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from app.db.database import Base


class Role(Enum):
    ADMIN = 'admin'
    READER = 'reader'


books_genres = Table(
    'books_genres',
    Base.metadata,
    Column('book_id', ForeignKey('books.id'), primary_key=True),
    Column('genre_id', ForeignKey('genres.id'), primary_key=True),
)

books_authors = Table(
    'books_authors',
    Base.metadata,
    Column('author_id', ForeignKey('authors.id'), primary_key=True),
    Column('book_id', ForeignKey('books.id'), primary_key=True),
)


class Genre(Base):
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name : Mapped[str] = mapped_column(String(128), nullable=False, unique=True)


class Book(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    publication_date: Mapped[Date] = mapped_column(Date, nullable=True)
    genres: Mapped[list[Genre]] = relationship(secondary=books_genres)
    available_copies: Mapped[int] = mapped_column(Integer, default=0, nullable=True)

    loans: Mapped[list['BookLoan']] = relationship( back_populates='book')
    authors: Mapped[list['Author']] = relationship(secondary=books_authors, back_populates='books')

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(AlchEnum(Role), default=Role.READER)

    borrowed_books: Mapped[list['BookLoan']] = relationship(back_populates='user')


class Author(Base):
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    biography: Mapped[str] = mapped_column(Text, nullable=True)
    birth_date: Mapped[Date] = mapped_column(Date)

    books: Mapped[list[Book]] = relationship(secondary=books_authors, back_populates='authors')


class BookLoan(Base):
    __tablename__ = 'book_loans'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'))
    issue_date: Mapped[Date] = mapped_column(Date)
    return_date: Mapped[Date] = mapped_column(Date, nullable=True)

    user: Mapped['User'] = relationship(back_populates='borrowed_books')
    book: Mapped['Book'] = relationship(back_populates='loans')
