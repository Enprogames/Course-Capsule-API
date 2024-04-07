"""
main.py

Defines the FastAPI backend server configuration and all API endpoints.
"""

from typing import Generator, Union, Annotated, Optional, Callable

from pydantic import BaseModel
from jose import JWTError
from sqlmodel import Session, select, delete
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Response,
    Security
)
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN
)
from pydantic import ValidationError

from fastapi.middleware.cors import CORSMiddleware

from server.session_security import OAuth2PasswordBearerWithCookie, UserSessionManager
from server.models import User, Course, UserRole, Post, PostWithAuthor, Approval
from sqlalchemy.orm import joinedload


app = FastAPI()

# Modern web browsers require the server to send the CORS headers
# in order to allow the frontend to make requests to the server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:5500",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserLoginSchema(BaseModel):
    username: str
    password: str


class UserRegisterSchema(BaseModel):
    username: str
    email: str
    password: str


class UserStatusSchema(BaseModel):
    logged_in: bool
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[int] = None


# OAuth2
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="login")
optional_oauth2_scheme = OAuth2PasswordBearerWithCookie(
    tokenUrl="login", auto_error=False)


def get_session() -> Generator[Session, None, None]:
    from server.db import engine
    with Session(engine) as session:
        yield session


async def get_user_data(user_id: int, session: Session = Depends(get_session)) -> UserStatusSchema:
    """Get user data from the database
    """
    user = session.exec(select(User).where(User.id == user_id)).first()
    if user:
        return UserStatusSchema(logged_in=True, username=user.username, email=user.email, role=user.role)
    else:
        raise HTTPException(status_code=404, detail="User not found")


def ensure_user_role(
        require_roles: list[UserRole]
        ) -> Callable:

    async def verify_user_role(
        access_token: str = Security(oauth2_scheme)
    ) -> int:
        credentials_exception = HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            token_data = UserSessionManager.decode_jwt(access_token)
            if token_data:
                user_id = token_data.user_id
                user_role = token_data.role
                if user_role not in require_roles:
                    raise HTTPException(
                        status_code=HTTP_403_FORBIDDEN,
                        detail="Not enough permissions",
                    )
                return user_id
            else:
                raise credentials_exception
        except (JWTError, ValidationError):
            raise credentials_exception

    return verify_user_role


@app.post("/courses/create")
async def create_course(
    new_course: Course,
    session: Session = Depends(get_session),
    user_id: int = Depends(ensure_user_role([UserRole.user, UserRole.teacher, UserRole.admin]))
):
    new_course.author_id = user_id
    session.add(new_course)
    session.commit()
    return {"message": "Course created"}


@app.post("/courses/{course_title}/create")
async def create_post(
    course_title: str,
    new_post: Post,
    session: Session = Depends(get_session),
    user_id: int = Depends(ensure_user_role([UserRole.user, UserRole.teacher, UserRole.admin]))
):
    new_post.author_id = user_id
    new_post.course_id = session.exec(select(Course.id).where(Course.title == course_title)).first()
    session.add(new_post)
    session.commit()
    return {"message": "Post created"}


@app.post("/courses/{course_title}/delete")
async def delete_course(
    course_title: str,
    session: Session = Depends(get_session),
    user_id: int = Depends(ensure_user_role([UserRole.admin]))
):
    course = session.exec(select(Course).where(Course.title == course_title)).first()
    if course:
        session.exec(
            delete(Course).where(Course.title == course_title)
        )
        session.commit()
        return {"message": "Course deleted"}
    else:
        raise HTTPException(status_code=404, detail="Course not found")


@app.post("/courses/{course_title}/posts/{post_id}/approve")
async def approve_post(
    post_id: int,
    session: Session = Depends(get_session),
    user_id: int = Depends(ensure_user_role([UserRole.teacher, UserRole.admin]))
):
    post = session.exec(
        select(Post)
        .where(Post.id == post_id)
    ).first()
    if post:
        approval = Approval(post_id=post_id, user_id=user_id)
        session.add(approval)
        session.commit()
        return {"message": "Post approved"}
    else:
        raise HTTPException(status_code=404, detail="Post not found")


# This route is protected by the OAuth2 scheme. The user must be logged in to access this route.
@app.get("/courses")
async def get_courses(
    session: Session = Depends(get_session),
    user_id: int = Depends(ensure_user_role([UserRole.user, UserRole.teacher, UserRole.admin]))
):
    courses = session.exec(select(Course)).all()

    return courses


@app.get("/courses/{course_title}/posts/{post_id}")
async def get_post(
    course_title: str,
    post_id: int,
    session: Session = Depends(get_session),
    user_id: int = Depends(ensure_user_role([UserRole.user, UserRole.teacher, UserRole.admin]))
):
    post = session.exec(
        select(Post)
        .where(Post.id == post_id)
    ).first()
    if post:
        return post
    else:
        raise HTTPException(status_code=404, detail="Note not found")


@app.get("/courses/{course_title}/posts")
async def get_course_posts(
    course_title: str,
    session: Session = Depends(get_session),
    user_id: int = Depends(ensure_user_role([UserRole.user, UserRole.teacher, UserRole.admin]))
) -> list[PostWithAuthor]:
    course = session.exec(
        select(Course)
        .options(
            joinedload(Course.posts).
            joinedload(Post.author),
            joinedload(Course.posts)
            .joinedload(Post.approvals)
            .joinedload(Approval.user))
        .where(Course.title == course_title)
    ).first()
    if course:
        # Return a list of posts with the author's username
        return [{**post.model_dump(),
                 'author_username': post.author.username,
                 'approvers': [approval.user.username for approval in post.approvals]} for post in course.posts]
    else:
        raise HTTPException(status_code=404, detail="Course not found")


@app.get("/verify-token")
async def verify_token(
    session: Session = Depends(get_session),
    access_token: Annotated[Union[str, None],
                            Depends(optional_oauth2_scheme)] = None
):
    """
    While the client is running, they can call this to check if they are logged in.
    It also sends the username and email of the user if they are logged in.
    """
    if access_token:
        token_data = UserSessionManager.decode_jwt(access_token)
        if token_data:
            user_id = token_data.user_id
            print(f"User ID: {user_id}")
            return await get_user_data(user_id, session)

    return UserStatusSchema(logged_in=False)


# Login the user by creating a session token and adding it as a cookie
@app.post("/login")
async def login(
    user_data: UserLoginSchema,
    response: Response,
    session: Session = Depends(get_session)
):
    username = user_data.username
    password = user_data.password
    print(f"Received data: {user_data}")
    user = session.exec(select(User)
                        .where(User.username == username, User.password == password)).first()
    if user:
        jwt_token = UserSessionManager.sign_jwt(user.id, user.role)
        response.set_cookie(
            key='access_token',
            value=f"Bearer {jwt_token}",
            httponly=False,
            secure=False,
            max_age=1800,
            samesite='lax',
            domain='localhost',
        )
        print(f"Logged in as {username}")
        print(f"JWT token: {jwt_token}")
        return {'message': f'successfully logged in as {username}', 'code': 0, 'logged_in': True}
    return {'message': 'fail', 'code': 1, 'logged_in': False}


# Log the user out by deleting their session token from their cookies
@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key='access_token')
    return {'message': 'logged out', 'code': 0, 'logged_in': False}


# Register a new user
@app.post('/register')
async def register(
    user_data: UserRegisterSchema,
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.username == user_data.username)).first()
    if user:
        return {'message': 'User already exists', 'code': 1}
    new_user = User(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
        role=UserRole.user
    )
    session.add(new_user)
    session.commit()
    return {'message': 'User created', 'code': 0}


@app.post('/admin/delete-user')
async def delete_user(
    session: Session = Depends(get_session),
    user_id: int = Depends(ensure_user_role([UserRole.admin]))
):
    user = session.exec(select(User).where(User.id == user_id)).first()
    if user:
        session.delete(user)
        session.commit()
        return {'message': 'User deleted', 'code': 0}
    return {'message': 'User not found', 'code': 1}
