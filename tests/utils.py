import uuid

from app.db import models


def create_test_user(db):
    unique_id = str(uuid.uuid4())
    user = models.User(
        username=f'testuser_{unique_id}',
        email=f'testuser_{unique_id}@example.com',
        hashed_password='testpassword'
    )
    db.add(user)
    db.commit()
    return user