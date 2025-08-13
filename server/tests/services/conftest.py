"""Helpers and fixtures for spinning up and connecting to test databases (created specifically for testing.)"""

import pytest
from typing import Callable
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, ProgrammingError
from ...env import env
from ...database import _admin_db_url, _content_db_url
from ...services import HealthService
from ...entities import BaseAdminEntity


def reset_database(
    database: str | None, user: str, database_url_fn: Callable[[str], str]
):
    """Resets the specified database by dropping and recreating it."""
    engine = create_engine(database_url_fn(""))
    with engine.connect() as connection:

        # Ensure we are not in a transaction
        conn = connection.execution_options(autocommit=False)
        conn.execute(text("ROLLBACK"))

        # Drop all databases except the protected ones
        DROP_PROTECTED = {"postgres", "template0", "template1"}
        result = conn.execute(
            text("SELECT datname FROM pg_database WHERE datistemplate = false")
        )
        databases = [row[0] for row in result]
        droppable_dbs = [db for db in databases if db not in DROP_PROTECTED]

        # Get all roles to delete
        roles_result = conn.execute(
            text(
                """
                SELECT rolname FROM pg_roles
                WHERE rolname NOT IN (
                    'postgres', 'pg_read_all_data', 'pg_write_all_data',
                    'pg_monitor', 'pg_signal_backend'
                ) AND rolname NOT LIKE 'pg_%'
            """
            )
        )
        roles = [row[0] for row in roles_result]

        # Drop owned objects for each role in each droppable database
        for db in droppable_dbs:
            print(f"Cleaning up roles in database {db}...")
            temp_engine = create_engine(database_url_fn(db))
            with temp_engine.connect() as temp_conn:
                for role in roles:
                    try:
                        temp_conn.execute(text(f"REASSIGN OWNED BY {role} TO postgres"))
                        temp_conn.execute(text(f"DROP OWNED BY {role}"))
                    except Exception as e:
                        print(f"Failed to clean role {role} in {db}: {e}")

        # Now that roles have no dependencies, drop the databases
        for db in droppable_dbs:
            try:
                conn.execute(
                    text(
                        f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = :db"
                    ),
                    {"db": db},
                )
                conn.execute(text(f'DROP DATABASE "{db}"'))
            except Exception as e:
                print(f"Failed to drop database {db}: {e}")

        # Now drop roles
        for role in roles:
            try:
                conn.execute(text(f"DROP ROLE IF EXISTS {role}"))
            except Exception as e:
                print(f"Failed to drop role {role}: {e}")

        # Finally, recreate the test database
        if database is not None:
            conn.execute(text(f"CREATE DATABASE {database}"))
            conn.execute(text(f"GRANT ALL PRIVILEGES ON DATABASE {database} TO {user}"))
            # Implement pgbouncer function
            pgbouncer_function = f"""
            -- Create a schema to hold the auth function (in template1 so NEW DBs inherit it)
            CREATE SCHEMA IF NOT EXISTS pgbouncer;

            -- Create the lookup function AS SUPERUSER so it can read pg_authid safely.
            -- SECURITY DEFINER ensures callers don't need superuser.
            CREATE OR REPLACE FUNCTION pgbouncer.get_auth(in uname text)
            RETURNS TABLE(usename text, passwd text)
            LANGUAGE sql
            SECURITY DEFINER
            SET search_path = pg_catalog
            AS $$
            SELECT rolname::text, rolpassword::text
            FROM pg_authid
            WHERE rolname = uname
            $$;

            -- Lock down the function a bit
            REVOKE ALL ON FUNCTION pgbouncer.get_auth(text) FROM PUBLIC;

            -- Create the dedicated "auth user" PgBouncer will use to run auth_query.
            -- Give it ONLY EXECUTE on the function.
            DO $$
            BEGIN
            IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'pgbouncer_auth') THEN
                CREATE ROLE pgbouncer_auth LOGIN PASSWORD 'dev-auth-password';
            END IF;
            END$$;

            GRANT USAGE ON SCHEMA pgbouncer TO pgbouncer_auth;
            GRANT EXECUTE ON FUNCTION pgbouncer.get_auth(text) TO pgbouncer_auth;

            -- Ensure NEW databases inherit the function (create it in template1 as well)
            \\c template1
            CREATE SCHEMA IF NOT EXISTS pgbouncer;
            CREATE OR REPLACE FUNCTION pgbouncer.get_auth(in uname text)
            RETURNS TABLE(usename text, passwd text)
            LANGUAGE sql
            SECURITY DEFINER
            SET search_path = pg_catalog
            AS $$
            SELECT rolname::text, rolpassword::text
            FROM pg_authid
            WHERE rolname = uname
            $$;
            REVOKE ALL ON FUNCTION pgbouncer.get_auth(text) FROM PUBLIC;
            GRANT USAGE ON SCHEMA pgbouncer TO pgbouncer_auth;
            GRANT EXECUTE ON FUNCTION pgbouncer.get_auth(text) TO pgbouncer_auth;
            """
            conn.execute(text(pgbouncer_function))


@pytest.fixture(scope="session")
def test_admin_engine() -> Engine:
    test_admin_database = f"{env.ADMIN_DB_DATABASE}_test"
    reset_database(test_admin_database, env.ADMIN_DB_USER, _admin_db_url)
    return create_engine(_admin_db_url(test_admin_database))


@pytest.fixture(scope="function")
def test_content_engine() -> Engine:
    test_content_database = f"{env.CONTENT_DB_DATABASE}_test"
    reset_database(test_content_database, env.CONTENT_DB_USER, _content_db_url)
    return create_engine(_content_db_url(test_content_database))


@pytest.fixture(scope="function")
def admin_db_session(test_admin_engine: Engine):
    BaseAdminEntity.metadata.drop_all(test_admin_engine)
    BaseAdminEntity.metadata.create_all(test_admin_engine)
    session = Session(test_admin_engine)
    BaseAdminEntity.setup_functions(session)
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
