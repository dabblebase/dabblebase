"""Helpers and fixtures for spinning up and connecting to test databases (created specifically for testing.)"""

import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session
from server.configuration import (
    setup_admin_db_cluster,
    setup_content_db_cluster,
    teardown_admin_db_cluster,
    teardown_content_db_cluster,
)
from server.entities.base import BaseAdminEntity
from ...database import (
    admin_db_url,
    content_db_cluster_url,
)


@pytest.fixture(scope="session")
def test_admin_engine() -> Engine:
    teardown_admin_db_cluster()
    setup_admin_db_cluster()
    return create_engine(admin_db_url())


@pytest.fixture(scope="session")
def test_content_engine() -> Engine:
    teardown_content_db_cluster()
    setup_content_db_cluster()
    return create_engine(content_db_cluster_url())


@pytest.fixture(scope="function")
def admin_db_session(test_admin_engine: Engine):
    BaseAdminEntity.metadata.drop_all(test_admin_engine)
    BaseAdminEntity.metadata.create_all(test_admin_engine)
    session = Session(test_admin_engine)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def content_db_session(test_content_engine: Engine):
    teardown_content_db_cluster()
    session = Session(test_content_engine)
    try:
        yield session
    finally:
        session.close()
