from sqlmodel import Session, SQLModel, create_engine, select

from server.models import User, Course, Post, UserRole

# Database Setup
DATABASE_URL = "sqlite:///db.sqlite3"

engine = create_engine(DATABASE_URL)

with Session(engine) as session:

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
                Course(
                    title="Fourth Course",
                    description="This is the fourth course",
                    author_id=1,
                ),
                Course(
                    title="Fifth Course",
                    description="This is the fifth course",
                    author_id=1,
                ),
                Course(
                    title="Sixth Course",
                    description="This is the sixth course",
                    author_id=1,
                ),
                Course(
                    title="Seventh Course",
                    description="This is the seventh course",
                    author_id=1,
                ),
                Course(
                    title="Eighth Course",
                    description="This is the eighth course",
                    author_id=1,
                ),
            ]
        )
        session.commit()

    if not session.exec(select(Post)).first():
        session.add_all(
            [
                Post(
                    title="First Post",
                    content="This is the first post",
                    author_id=1,
                    course_id=1,
                ),
                Post(
                    title="Second Post",
                    content="This is the second post",
                    author_id=1,
                    course_id=1,
                ),
                Post(
                    title="Third Post",
                    content="This is the third post",
                    author_id=1,
                    course_id=1,
                ),
            ]
        )
        session.commit()
