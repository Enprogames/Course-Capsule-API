import datetime
import pytest
from urllib.parse import quote

from fastapi.testclient import TestClient
from sqlmodel import Session, select, insert

from main import app
from server.models import User, UserRole, Course, Post
from server.session_security import UserSessionManager
from utils import session_fixture

# Constants
TEST_DATABASE_URL = "sqlite:///:memory:"

# Test client
client = TestClient(app=app)


@pytest.fixture()
def populate_database(session: Session):
    # Populate the database with necessary initial data
    admin1 = User(
            id=1,
            email="admin1@example.com",
            username="admin1",
            password="password",
            role=UserRole.admin
    )
    user1 = User(
            id=2,
            email="user1@example.com",
            username="user1",
            password="password",
            role=UserRole.user
    )
    course1 = Course(
            id=1,
            title="First Course",
            description="This is the first course",
            author_id=admin1.id
    )
    post1 = Post(
            title="Initial Post",
            description="This is the initial post",
            author_id=user1.id,
            course_id=course1.id,
            type="post",
            content="This is the content of the post"
    )
    session.add_all([admin1, user1, course1, post1])
    session.commit()

    yield

    # The database is automatically cleared after each test because of the session fixture


@pytest.fixture(name='user_factory')
def user_factory_fixture(session: Session):

    def valid_user(
            role: UserRole = UserRole.user,
            valid: bool = True,
            username: str = 'mynewuser',
            password: str = 'password123'
        ):
        new_user = User(username=username, role=role, password=password)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        if valid:
            session_token = UserSessionManager.sign_jwt(new_user.id, new_user.role)
        else:
            session_token = "Bearer invalidtoken"

        client.cookies.update({"access_token": f"Bearer {session_token}"})
        return new_user

    yield valid_user

    # cleanup
    del client.cookies['access_token']


def test_create_course(populate_database, user_factory):
    """Ensure a logged in user can create a course"""

    # Log in a valid user
    user_factory(role=UserRole.user, valid=True)

    response = client.post(
        f"/courses/create",
        json={
            'title': 'My New Course',
            'description': 'This is my new course.'
        }
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Course created"}

def test_delete_course_no_user_denied(session: Session, populate_database):
    """Ensure that when there is no user logged in, a course cannot be deleted"""

    some_course = session.exec(
        select(Course)
    ).first()

    escaped_title = quote(some_course.title, safe='')

    response = client.post(
        f"/courses/{escaped_title}/delete"
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    # ensure the course still exists in the database
    some_course = session.exec(
        select(Course)
        .where(Course.id == some_course.id)
    ).first()
    assert some_course is not None

def test_delete_course_invalid_user_denied(session: Session, populate_database, user_factory):
    """Ensure that an invalid user is unable to delete a course"""
    # Log in a valid user
    user_factory(role=UserRole.user, valid=False)

    some_course = session.exec(
        select(Course)
    ).first()

    escaped_title = quote(some_course.title, safe='')

    response = client.post(
        f"/courses/{escaped_title}/delete"
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

    # ensure the course still exists in the database
    some_course = session.exec(
        select(Course)
        .where(Course.id == some_course.id)
    ).first()
    assert some_course is not None

def test_delete_course_user_denied(session: Session, populate_database, user_factory):
    """Ensure that a logged in user is unable to delete a course"""
    # Log in a valid user
    user_factory(role=UserRole.user, valid=True)

    some_course = session.exec(
        select(Course)
    ).first()

    escaped_title = quote(some_course.title, safe='')

    response = client.post(
        f"/courses/{escaped_title}/delete"
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}

    # ensure the course still exists in the database
    some_course = session.exec(
        select(Course)
        .where(Course.id == some_course.id)
    ).first()
    assert some_course is not None

def test_delete_course_teacher_denied(session: Session, populate_database, user_factory):
    """Ensure that a logged in teacher is unable to delete a course"""
    # Log in a valid teacher
    user_factory(role=UserRole.teacher, valid=True)

    some_course = session.exec(
        select(Course)
    ).first()

    escaped_title = quote(some_course.title, safe='')

    response = client.post(
        f"/courses/{escaped_title}/delete"
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}

    # ensure the course still exists in the database
    some_course = session.exec(
        select(Course)
        .where(Course.id == some_course.id)
    ).first()
    assert some_course is not None

def test_delete_course_admin_success(session: Session, populate_database, user_factory):
    """Ensure that a logged in teacher is unable to delete a course"""
    # Log in a valid admin
    user_factory(role=UserRole.admin, valid=True)

    some_course = session.exec(
        select(Course)
    ).first()

    escaped_title = quote(some_course.title, safe='')

    response = client.post(
        f"/courses/{escaped_title}/delete"
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Course deleted"}

    # ensure the course no longer exists in the database
    some_course = session.exec(
        select(Course)
        .where(Course.id == some_course.id)
    ).first()
    assert some_course is None

def test_view_post_no_token(session: Session, populate_database):
    """Test creating a post without a session token
    """
    first_post = session.exec(select(Post)).first()
    some_course = session.exec(
        select(Course).where(Course.id == first_post.course_id)
    ).first()

    escaped_title = quote(some_course.title, safe='')
    response = client.get(
        f"/courses/{escaped_title}/posts/{first_post.id}"
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    response = client.get(
        f"/courses/{escaped_title}/posts"
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_view_post_invalid_token(session: Session, populate_database, user_factory):
    """Test creating a post with an invalid session token
    """

    invalid_user = user_factory(role=UserRole.user, valid=False)

    first_post = session.exec(select(Post)).first()
    some_course = session.exec(
        select(Course).where(Course.id == first_post.course_id)
    ).first()

    escaped_title = quote(some_course.title, safe='')
    response = client.get(f"/courses/{escaped_title}/posts/{first_post.id}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

    response = client.get(f"/courses/{escaped_title}/posts")
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


def test_view_post_valid_token(
        session: Session,
        populate_database,
        user_factory):
    my_user = user_factory(UserRole.user)

    user1 = session.exec(select(User).where(User.username == "user1")).first()
    first_post = session.exec(select(Post)).first()
    some_course = session.exec(
        select(Course).where(Course.id == first_post.course_id)
    ).first()

    escaped_title = quote(some_course.title, safe='')

    response = client.get(f"/courses/{escaped_title}/posts/{first_post.id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": first_post.id,
        "title": first_post.title,
        "description": first_post.description,
        "author_id": first_post.author_id,
        "course_id": first_post.course_id,
        "created_at": first_post.created_at.isoformat(),
        "type": first_post.type,
        "content": first_post.content
    }

    response = client.get(f"/courses/{escaped_title}/posts")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": first_post.id,
            "title": first_post.title,
            "description": first_post.description,
            "author_id": first_post.author_id,
            "author_username": user1.username,
            "approvers": [],
            "course_id": first_post.course_id,
            "created_at": first_post.created_at.isoformat(),
            "type": first_post.type,
            "content": first_post.content
        }
    ]
