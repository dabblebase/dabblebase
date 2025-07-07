"""Contains injectible SQLAlchemy session connections to the databases."""

import sqlalchemy
from sqlalchemy.orm import Session
from .env import env, in_production
from celery import Celery


def _admin_db_url(database: str = env.ADMIN_DB_DATABASE) -> str:
    """Construct the URL for the admin database."""
    return f"postgresql+psycopg2://{env.ADMIN_DB_USER}:{env.ADMIN_DB_PASSWORD}@{env.ADMIN_DB_HOST}:{env.ADMIN_DB_PORT}/{database}"


def _content_db_url(database: str = env.CONTENT_DB_DATABASE) -> str:
    """Construct the URL for the content database."""
    return f"postgresql+psycopg2://{env.CONTENT_DB_USER}:{env.CONTENT_DB_PASSWORD}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{database}"


def admin_db_engine():
    """Injectible generator for the admin db engine."""
    return sqlalchemy.create_engine(
        url=_admin_db_url(),
        echo=not in_production(),
    )


def content_db_engine():
    """Injectible generator for the admin db engine."""
    return sqlalchemy.create_engine(
        url=_content_db_url(),
        echo=not in_production(),
    )


def admin_db_session():
    """Injectible generator for the admin db session."""
    session = Session(admin_db_engine())
    try:
        yield session
    finally:
        session.close()


def content_db_session():
    """Injectible generator for the content db session."""
    session = Session(content_db_engine())
    try:
        yield session
    finally:
        session.close()
