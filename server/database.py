"""Contains injectible SQLAlchemy session connections to the databases."""

import sqlalchemy
from sqlalchemy.orm import Session
from .env import env, in_production
from celery import Celery


def admin_db_cluster_url() -> str:
    """Constructs a url for the admin db cluster"""
    return f"postgresql+psycopg2://{env.ADMIN_DB_USER}:{env.ADMIN_DB_PASSWORD}@{env.ADMIN_DB_HOST}:{env.ADMIN_DB_PORT}"


def admin_db_url(database: str = env.ADMIN_DB_DATABASE) -> str:
    """Construct the URL a database in the admin db cluster."""
    return f"{admin_db_cluster_url()}/{database}"


def content_db_cluster_url() -> str:
    """Constructs a url for the content db cluster"""
    return f"postgresql+psycopg2://{env.CONTENT_DB_USER}:{env.CONTENT_DB_PASSWORD}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}"


def content_db_url(database: str = env.CONTENT_DB_DATABASE) -> str:
    """Construct the URL a database in the content db cluster."""
    return f"{content_db_cluster_url()}/{database}"


def admin_db_engine(echo: bool = not in_production()):
    """Injectible generator for the admin db engine."""
    return sqlalchemy.create_engine(
        url=admin_db_url(),
        echo=echo,
    )


def content_db_engine(echo: bool = not in_production()):
    """Injectible generator for the admin db engine."""
    return sqlalchemy.create_engine(
        url=content_db_url(),
        echo=echo,
    )


def admin_db_session(echo: bool = not in_production()):
    """Injectible generator for the admin db session."""
    session = Session(admin_db_engine(echo))
    try:
        yield session
    finally:
        session.close()


def content_db_session(echo: bool = not in_production()):
    """Injectible generator for the content db session."""
    session = Session(content_db_engine(echo))
    try:
        yield session
    finally:
        session.close()
