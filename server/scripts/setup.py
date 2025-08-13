"""
Sets up pgbouncer.

This script configures pgbouncer for use with the content database.

Usage: python3 -m scripts.setup
"""

import sqlalchemy
from sqlalchemy import text
from ..env import env

# Generate the engines
content_cluster_url = f"postgresql+psycopg2://{env.CONTENT_DB_USER}:{env.CONTENT_DB_PASSWORD}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}"
content_cluster_engine = sqlalchemy.create_engine(url=content_cluster_url, echo=True)

with content_cluster_engine.connect() as connection:
    connection.execute(sqlalchemy.text("COMMIT"))  # Get out of transaction mode
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
    print("✅ Setup complete.")
    print(
        "⚠️ Please restart the pgbouncer instance in the devcontainer before proceeding."
    )
