import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from main import app, get_session


# Constants
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(name='session')
def session_fixture():
    # Set up an in-memory SQLite database for testing
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    # Begin a transaction
    with engine.connect() as conn:
        with conn.begin() as transaction:
            with Session(bind=conn, join_transaction_mode="create_savepoint") as session:
                def get_session_override():  
                    return session  

                # API endpoints use the get_session dependency to access the
                # database. We override the dependency with the session fixture.
                app.dependency_overrides[get_session] = get_session_override

                yield session

                app.dependency_overrides.clear()

            transaction.rollback()  # Rollback the transaction to clear the data
