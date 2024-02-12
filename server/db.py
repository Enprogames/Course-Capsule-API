from typing import Optional
import enum

from sqlalchemy import Enum
from sqlmodel import Field, Session, SQLModel, create_engine, select


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


class Course(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
    description: str
    author_id: int


# Database Setup
DATABASE_URL = "sqlite:///db.sqlite3"

engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    # Create tables
    SQLModel.metadata.create_all(engine)

    # Insert initial data
    if not session.exec(select(User)).first():
        session.add_all(
            [
                User(username="admin", password="password", email="fred@example.com", role=UserRole.admin),
                User(username="bob", password="1234", email="bob@example.com", role=UserRole.user),
                User(username="alice", password="1234", email="alice@example.com", role=UserRole.teacher),
            ]
        )
        session.commit()

    if not session.exec(select(Course)).first():
        session.add_all(
            [
                Course(
                    title="First Course",
                    description="This is the first course",
                    author_id=1,
                ),
                Course(
                    title="Second Course",
                    description="This is the second course",
                    author_id=1,
                ),
                Course(
                    title="Third Course",
                    description="This is the third course",
                    author_id=1,
                ),
            ]
        )
        session.commit()
