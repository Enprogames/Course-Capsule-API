from typing import Union, Annotated, Optional, Callable

from pydantic import BaseModel
from jose import JWTError
from sqlmodel import Session, select
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Request,
    Response,
    Security
)
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN
)
from pydantic import ValidationError

from fastapi.middleware.cors import CORSMiddleware

from server.session_security import OAuth2PasswordBearerWithCookie, decode_jwt, sign_jwt
from server.models import User, Course, UserRole
from server.db import engine


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


async def get_user_data(user_id: int) -> UserStatusSchema:
    """Get user data from the database
    """
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
    if user:
        return UserStatusSchema(logged_in=True, username=user.username, email=user.email, role=user.role)
    else:
        raise HTTPException(status_code=404, detail="User not found")


def ensure_user_role(
        require_roles: list[UserRole]
        ) -> Callable:

    async def verify_user_role(
        access_token: str = Security(oauth2_scheme),
    ) -> int:
        credentials_exception = HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            token_data = decode_jwt(access_token)
            if token_data:
                user_id = token_data.user_id
                user_role = token_data.role
                if user_role not in require_roles:
                    raise HTTPException(
                        status_code=HTTP_403_FORBIDDEN,
                        detail="Not enough permissions",
                    )
        except (JWTError, ValidationError):
            raise credentials_exception

        return user_id
    return verify_user_role


# Simple API route. Try typing http://localhost:8000 in your browser to see the result.
# This makes a GET request to the server and the server responds with a JSON object.
@app.get("/")
async def root():
    return {"message": "Hello World"}


# This route is protected by the OAuth2 scheme. The user must be logged in to access this route.
@app.get("/courses")
async def get_courses(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    user_id: int = Depends(ensure_user_role([UserRole.user, UserRole.teacher, UserRole.admin]))
):
    with Session(engine) as session:
        courses = session.exec(select(Course)).all()
    return courses


# While the client is running, they can call this to check if they are logged in.
# It also sends the username and email of the user if they are logged in.
@app.get("/verify-token")
async def verify_token(
    access_token: Annotated[Union[str, None],
                            Depends(optional_oauth2_scheme)] = None
):

    if access_token:
        token_data = decode_jwt(access_token)
        if token_data:
            user_id = token_data.user_id
            print(f"User ID: {user_id}")
            return await get_user_data(user_id)

    return UserStatusSchema(logged_in=False)


# Login the user by creating a session token and adding it as a cookie
@app.post("/login")
async def login(user_data: UserLoginSchema, request: Request, response: Response):
    username = user_data.username
    password = user_data.password
    print(f"Received data: {user_data}")
    with Session(engine) as session:
        user = session.exec(select(User)
                            .where(User.username == username, User.password == password)).first()
    if user:
        jwt_token = sign_jwt(user.id, user.role)
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
async def register(user_data: UserRegisterSchema):
    with Session(engine) as session:
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
    user_id: int = Depends(ensure_user_role([UserRole.admin]))
):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if user:
            session.delete(user)
            session.commit()
            return {'message': 'User deleted', 'code': 0}
    return {'message': 'User not found', 'code': 1}
