import enum
from typing import Optional
import datetime

from sqlalchemy import Enum
from sqlmodel import Field, Relationship, SQLModel


class UserRole(enum.Enum):
    user = 0
    teacher = 1
    admin = 2


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    email: str = Field(sa_column_kwargs={"nullable": True})
    username: str = Field(sa_column_kwargs={"unique": True})
    password: str
    role: UserRole = Field(sa_column=Enum(UserRole))

    courses: list["Course"] = Relationship(back_populates="author")
    posts: list["Post"] = Relationship(back_populates="author")


class Course(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str
    description: str
    author_id: int = Field(foreign_key="user.id")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    author: Optional[User] = Relationship(back_populates="courses")
    posts: list["Post"] = Relationship(back_populates="course")


class Post(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
    content: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    author_id: int = Field(foreign_key="user.id")
    course_id: int = Field(foreign_key="course.id")

    author: Optional[User] = Relationship(back_populates="posts")
    course: Optional[Course] = Relationship(back_populates="posts")
