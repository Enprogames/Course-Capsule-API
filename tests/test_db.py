"""
test/test_endpoints.py

Simple unit tests for database models.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from server.models import User, UserRole, Course, Post, Approval
from utils import session_fixture  # noqa: F401


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


def test_course_creation(session: Session):
    user = User(
        email='teacher@example.com',
        username='techeruser',
        password='mypassword',
        role=UserRole.teacher
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    course = Course(
        title='Intro to systems design',
        description='Course on the basics of systems design and development',
        author_id=user.id
    )
    session.add(course)
    session.commit()
    session.refresh(user)
    session.refresh(course)

    assert course.id is not None
    assert course.title == 'Intro to systems design'
    assert course.author_id == user.id
    assert course.created_at is not None


def test_approval_creation(session: Session):
    user = User(
        email="approver@example.com",
        username="approveruser",
        password="password",
        role=UserRole.admin
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    course = Course(
        title='Intro to systems design',
        description='Course on the basics of systems design and development',
        author_id=user.id
    )
    session.add(course)
    session.commit()
    session.refresh(course)
    post = Post(
        title="Python Post",
        description="Discussing variables",
        type="Note",
        content="Variables in Python are...",
        author_id=user.id,
        course_id=course.id  # Assuming a course with ID 1 exists
    )
    session.add(post)
    session.commit()
    session.refresh(post)
    approval = Approval(
        post_id=post.id,
        user_id=user.id
    )
    session.add(user)
    session.add(post)
    session.add(approval)
    session.commit()
    session.refresh(user)
    session.refresh(post)
    session.refresh(approval)

    assert approval.id is not None
    assert approval.post_id == post.id
    assert approval.user_id == user.id


def test_unique_approval_constraint(session: Session):
    """
    Test to ensure a user cannot approve the same post more than once
    """
    user = User(
        email="approver@example.com",
        username="approveruser",
        password="password",
        role=UserRole.admin
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    course = Course(
        title='Intro to systems design',
        description='Course on the basics of systems design and development',
        author_id=user.id
    )
    session.add(course)
    session.commit()
    session.refresh(course)
    post = Post(
        title="Python Post",
        description="Discussing variables",
        type="Note",
        content="Variables in Python are...",
        author_id=user.id,
        course_id=course.id  # Assuming a course with ID 1 exists
    )
    session.add(post)
    session.commit()
    session.refresh(post)

    approval1 = Approval(
        post_id=post.id,
        user_id=user.id
    )
    approval2 = Approval(
        post_id=post.id,
        user_id=user.id
    )
    session.add(user)
    session.add(post)
    session.add(approval1)
    session.add(approval2)
    with pytest.raises(IntegrityError):
        session.commit()
