import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from server.models import User, UserRole, Course, Post
from utils import session_fixture


def test_user(session: Session):
    user = User(
        id=1,
        email="user@example.com",
        username="testuser",
        password="password",
        role=UserRole.user
    )
    assert user.id == 1
    assert user.email == "user@example.com"
    assert user.username == "testuser"


def test_username_uniqueness(session: Session):
    """Test database constraint ensuring two users cannot have the same username
    """
    user1 = User(
        email="user1@example.com",
        username="testuser",
        password="password",
        role=UserRole.user
    )
    user2 = User(
        email="user2@example.com",
        username="testuser",
        password="password",
        role=UserRole.user
    )
    session.add(user1)
    session.add(user2)
    with pytest.raises(IntegrityError):
        session.commit()
