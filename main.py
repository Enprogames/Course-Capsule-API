from typing import Union, Annotated, Optional

from pydantic import BaseModel
from sqlmodel import Session, select
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Request,
    Response
)

from fastapi.middleware.cors import CORSMiddleware

from server.session_security import OAuth2PasswordBearerWithCookie, decode_jwt, sign_jwt
from server.db import User, Course, engine, UserRoles


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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Union[int, None] = None


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


# Simple API route. Try typing http://localhost:8000 in your browser to see the result.
# This makes a GET request to the server and the server responds with a JSON object.
@app.get("/")
async def root():
    return {"message": "Hello World"}


# This route is protected by the OAuth2 scheme. The user must be logged in to access this route.
@app.get("/courses")
async def get_courses(
    access_token: Annotated[str, Depends(oauth2_scheme)]
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
            user_id = token_data['user_id']
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
        jwt_token = sign_jwt(user.id)
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
            role=UserRoles.user
        )
        session.add(new_user)
        session.commit()
    return {'message': 'User created', 'code': 0}
