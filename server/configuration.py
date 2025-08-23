"""Functions that handle the setup and teardown of the dev setup."""

from server.database import (
    admin_db_cluster_url,
    admin_db_url,
    content_db_cluster_url,
    content_db_url,
)
from .env import env
from sqlalchemy import create_engine, text
from .entities import BaseAdminEntity


def setup_admin_db_cluster():
    """Sets up the empty admin db cluster."""
    # Create the engine
    admin_db_cluster_engine = create_engine(admin_db_cluster_url())
    # Create the admin database
    with admin_db_cluster_engine.connect() as conn:
        conn.execute(text("COMMIT"))  # Get out of transaction mode
        conn.execute(text(f"CREATE DATABASE {env.ADMIN_DB_DATABASE}"))

    # Now connect to the newly created database to set up tables and functions
    admin_db_engine = create_engine(admin_db_url())
    with admin_db_engine.connect() as conn:
        # Create the tables in the admin database
        BaseAdminEntity.metadata.drop_all(conn)
        BaseAdminEntity.metadata.create_all(conn)

        # Create a function that notifies when a new project is created
        # This function is used to notify the realtime server when new projects
        # are created so that it can begin listening to the project for
        # changes and updates.
        notify_new_project_sql = """
        CREATE FUNCTION notify_new_project() RETURNS trigger AS $$
        BEGIN
          PERFORM pg_notify('new_project', row_to_json(NEW)::text);
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trg_new_project
        AFTER INSERT ON projects
        FOR EACH ROW EXECUTE FUNCTION notify_new_project();
        """
        conn.execute(text(notify_new_project_sql))
        conn.commit()


def teardown_admin_db_cluster():
    """Tears down the admin db cluster."""
    # Create the engine
    admin_db_cluster_engine = create_engine(admin_db_cluster_url())
    # Deletes the admin database
    with admin_db_cluster_engine.connect() as conn:
        conn.execute(text("COMMIT"))  # Get out of transaction mode
        # Deletes the database (this will remove all objects including functions and triggers)
        conn.execute(text(f"DROP DATABASE IF EXISTS {env.ADMIN_DB_DATABASE}"))


def setup_content_db_cluster():
    """Sets up the content db cluster."""
    # Create the engine
    content_db_cluster_engine = create_engine(content_db_cluster_url())
    with content_db_cluster_engine.connect() as connection:
        # Ensure we are not in a transaction
        conn = connection.execution_options(autocommit=False)
        conn.execute(text("ROLLBACK"))

        # Implement pgbouncer function for current database
        pgbouncer_function = f"""
        -- Create a schema to hold the auth function
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
        """
        conn.execute(text(pgbouncer_function))
        conn.commit()

        # Set up pgbouncer admin user
        setup_pgbouncer_sql = f"""
        DO $$
        BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='pgbouncer_auth') THEN
            CREATE ROLE pgbouncer_auth LOGIN PASSWORD '{env.PGBOUNCER_PASSWORD}';
        ELSE
            ALTER ROLE pgbouncer_auth WITH LOGIN PASSWORD '{env.PGBOUNCER_PASSWORD}';
        END IF;
        END$$;

        -- show the stored hash (SCRAM by default on PG15)
        SELECT rolpassword FROM pg_authid WHERE rolname='pgbouncer_auth';
        """
        connection.execute(text(setup_pgbouncer_sql))

    # Also create the function in template1 so new databases inherit it
    template1_engine = create_engine(content_db_url("template1"))
    with template1_engine.connect() as conn:
        template1_function = f"""
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
        conn.execute(text(template1_function))
        conn.commit()


def teardown_content_db_cluster():
    """Tears down the content db cluster."""
    # Create the engine
    content_db_cluster_engine = create_engine(content_db_cluster_url())
    # Start tearing down cluster
    with content_db_cluster_engine.connect() as connection:
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
            temp_engine = create_engine(content_db_url(db))
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

        # Finally, drop roles
        for role in roles:
            try:
                conn.execute(text(f"DROP ROLE IF EXISTS {role}"))
            except Exception as e:
                print(f"Failed to drop role {role}: {e}")
