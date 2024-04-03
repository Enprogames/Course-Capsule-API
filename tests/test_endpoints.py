import pytest
from urllib.parse import quote

from fastapi.testclient import TestClient
from sqlmodel import Session, select

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



def test_create_course(session: Session):
    # TODO: Implement test for creating a course
    pass


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


def test_view_post_invalid_token(session: Session, populate_database):
    """Test creating a post with an invalid session token
    """
    first_post = session.exec(select(Post)).first()
    some_course = session.exec(
        select(Course).where(Course.id == first_post.course_id)
    ).first()

    client.cookies.update({"access_token": "Bearer invalidtoken"})

    escaped_title = quote(some_course.title, safe='')
    response = client.get(f"/courses/{escaped_title}/posts/{first_post.id}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

    response = client.get(f"/courses/{escaped_title}/posts")
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


def test_view_post_valid_token(session: Session, populate_database):
    user1 = session.exec(select(User).where(User.username == "user1")).first()
    first_post = session.exec(select(Post)).first()
    some_course = session.exec(
        select(Course).where(Course.id == first_post.course_id)
    ).first()
    valid_token = UserSessionManager.sign_jwt(user1.id, user1.role)

    client.cookies.update({"access_token": f"Bearer {valid_token}"})

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
