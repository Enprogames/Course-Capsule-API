from server.models import User, Course, Post

from sqlmodel import SQLModel


def test_user():
    user = User(
        id=1,
        email="user@example.com",
        username="testuser",
        password="password",
        role="user"
    )
    assert user.id == 1
    assert user.email == "user@example.com"
    assert user.username == "testuser"
