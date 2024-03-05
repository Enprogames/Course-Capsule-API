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
    notes: list["Note"] = Relationship(back_populates="author")


class Course(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str
    description: str
    author_id: int = Field(foreign_key="user.id")
    created_at: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.now)

    author: Optional[User] = Relationship(back_populates="courses")
    notes: list["Note"] = Relationship(back_populates="course")


"""
### Inheritance of Note from Post ###

The `Note` class inherits from the `Post` class. This means
that all attributes are inherited. A decision was made to not
let `Post` be its own table. 
"""


class Post(SQLModel):
    """Base class for all posts. This class itself should not be used to create any posts.
    Instead, use the `Note` class to create notes.
    In the future, other types of posts can be created, such as `FlashcardSet`.

    Args:
        SQLModel: Data model. This class can be used as a database table, and types are strongly enforced.
        table: This model will be stored persistently in the database.
    """
    id: Optional[int] = Field(primary_key=True)
    title: str
    description: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    author_id: int = Field(foreign_key="user.id")
    course_id: int = Field(foreign_key="course.id")


class Note(Post, table=True):
    content: Optional[str] = Field(sa_column_kwargs={"nullable": True})

    author: Optional[User] = Relationship(back_populates="notes")
    course: Optional[Course] = Relationship(back_populates="notes")
