"""initial

Revision ID: 002445500ae8
Revises: 
Create Date: 2025-01-11 00:52:51.769677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002445500ae8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('authors',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('biography', sa.Text(), nullable=False),
    sa.Column('birth_date', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_authors_id'), 'authors', ['id'], unique=False)
    op.create_table('books',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('publication_date', sa.Date(), nullable=False),
    sa.Column('available_copies', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_books_id'), 'books', ['id'], unique=False)
    op.create_table('genres',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_genres_id'), 'genres', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('username', sa.String(length=150), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('ADMIN', 'READER', name='role'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('book_loans',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('book_id', sa.BigInteger(), nullable=False),
    sa.Column('issue_date', sa.Date(), nullable=False),
    sa.Column('return_date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_book_loans_id'), 'book_loans', ['id'], unique=False)
    op.create_table('books_authors',
    sa.Column('author_id', sa.BigInteger(), nullable=False),
    sa.Column('book_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['authors.id'], ),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
    sa.PrimaryKeyConstraint('author_id', 'book_id')
    )
    op.create_table('books_genres',
    sa.Column('book_id', sa.BigInteger(), nullable=False),
    sa.Column('genre_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], ),
    sa.PrimaryKeyConstraint('book_id', 'genre_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('books_genres')
    op.drop_table('books_authors')
    op.drop_index(op.f('ix_book_loans_id'), table_name='book_loans')
    op.drop_table('book_loans')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_genres_id'), table_name='genres')
    op.drop_table('genres')
    op.drop_index(op.f('ix_books_id'), table_name='books')
    op.drop_table('books')
    op.drop_index(op.f('ix_authors_id'), table_name='authors')
    op.drop_table('authors')
    op.execute('DROP TYPE IF EXISTS "role"')
    # ### end Alembic commands ###
