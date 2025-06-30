"""Helpers and fixtures for spinning up and connecting to test databases (created specifically for testing.)"""

import pytest
from typing import Callable
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, ProgrammingError
from ...env import env
from ...database import _admin_db_url, _content_db_url
from ...services import HealthService


def reset_database(database: str, user: str, database_url_fn: Callable[[str], str]):
    """Resets the specified database by dropping and recreating it."""
    engine = create_engine(database_url_fn(""))
    with engine.connect() as connection:
        try:
            conn = connection.execution_options(autocommit=False)
            conn.execute(text("ROLLBACK"))  # Get out of transactional mode...
            conn.execute(text(f"DROP DATABASE {database}"))
        except ProgrammingError:
            ...
        except OperationalError:
            print(
                "Could not drop database because it's being accessed by others (psql open?)"
            )
            exit(1)

        conn.execute(text(f"CREATE DATABASE {database}"))
        conn.execute(text(f"GRANT ALL PRIVILEGES ON DATABASE {database} TO {user}"))


@pytest.fixture(scope="session")
def test_admin_engine() -> Engine:
    test_admin_database = f"{env.ADMIN_DB_DATABASE}_test"
    reset_database(test_admin_database, env.ADMIN_DB_USER, _admin_db_url)
    return create_engine(_admin_db_url(test_admin_database))


@pytest.fixture(scope="session")
def test_content_engine() -> Engine:
    test_content_database = f"{env.CONTENT_DB_DATABASE}_test"
    reset_database(test_content_database, env.CONTENT_DB_USER, _content_db_url)
    return create_engine(_content_db_url(test_content_database))


@pytest.fixture(scope="function")
def admin_db_session(test_admin_engine: Engine):
    # entities.EntityBase.metadata.drop_all(test_admin_engine)
    # entities.EntityBase.metadata.create_all(test_admin_engine)
    session = Session(test_admin_engine)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def content_db_session(test_content_engine: Engine):
    # entities.EntityBase.metadata.drop_all(test_content_engine)
    # entities.EntityBase.metadata.create_all(test_content_engine)
    session = Session(test_content_engine)
    try:
        yield session
    finally:
        session.close()
