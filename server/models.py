import enum
from typing import Optional
import datetime

from sqlalchemy import Enum, UniqueConstraint
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
    approvals: list["Approval"] = Relationship(back_populates="user")


class Course(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str
    description: str
    author_id: int = Field(foreign_key="user.id")
    created_at: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.now)

    author: Optional[User] = Relationship(back_populates="courses")
    posts: list["Post"] = Relationship(back_populates="course")


"""
### Inheritance of Note and FlashcardSet from Post ###

The `Note` class (and `FlashcardSet` in the future) inherit from the `Post` class. But since
we are using single table inheritance, they are actually represented by one `Post` class. This
means that all attributes are inherited from the `Post` class, and additional attributes may or
may not be null depending on the type of post.

Concrete inheritance in databases means that multiple types of objects are stored in the same
table, and a column is used to differentiate between the types. In this case, the `type` column
is used to differentiate between `Note` and `FlashcardSet`.
"""


class BasePost(SQLModel, table=False):
    id: Optional[int] = Field(primary_key=True)
    title: str
    description: str
    type: str = Field(sa_column_kwargs={"nullable": False})

    created_at: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.now)
    author_id: int = Field(foreign_key="user.id")
    course_id: int = Field(foreign_key="course.id")


class Post(BasePost, table=True):
    """Base class for all posts. This class itself should not be used to create any posts.
    Instead, use the `Note` class to create notes.
    In the future, other types of posts can be created, such as `FlashcardSet`.

    Args:
        SQLModel: Data model. This class can be used as a database table, and types are strongly enforced.
        table: This model will be stored persistently in the database.
    """

    # field specific to notes
    content: Optional[str] = Field(sa_column_kwargs={"nullable": True})

    author: Optional[User] = Relationship(back_populates="posts")
    course: Optional[Course] = Relationship(back_populates="posts")
    approvals: list["Approval"] = Relationship(back_populates="post")


class PostWithAuthor(BasePost, table=False):
    id: int
    content: str
    author_username: str
    approvers: list[str]

    class Config:
        arbitrary_types_allowed = True

class Approval(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    created_at: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.now)

    post_id: int = Field(foreign_key="post.id")
    user_id: int = Field(foreign_key="user.id")

    post: Optional[Post] = Relationship(back_populates="approvals")
    user: Optional[User] = Relationship(back_populates="approvals")

    # composite unique constraint
    __table_args__ = (
        UniqueConstraint("post_id", "user_id"),
    )
