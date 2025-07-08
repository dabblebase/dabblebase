"""
Resets the database for development purposes.

This script deletes and recreates the database schema, reseting all data
to the seeded development data. The script can only be used in development
mode.

Usage: python3 -m scripts.reset_db
"""

import sys
import sqlalchemy
from sqlalchemy import text
from ..env import env
from ..entities import BaseAdminEntity
from ..database import admin_db_engine

# Ensures that the script can only be run in development mode
if env.MODE != "development":
    print("This script can only be run in development mode.", file=sys.stderr)
    exit(1)

# Generate the engines
admin_cluster_url = f"postgresql+psycopg2://{env.ADMIN_DB_USER}:{env.ADMIN_DB_PASSWORD}@{env.ADMIN_DB_HOST}:{env.ADMIN_DB_PORT}"
admin_cluster_engine = sqlalchemy.create_engine(url=admin_cluster_url, echo=True)

# Delete and re-create the admin database on reset
with admin_cluster_engine.connect() as connection:
    connection.execute(sqlalchemy.text("COMMIT"))  # Get out of transaction mode
    connection.execute(text(f"DROP DATABASE IF EXISTS {env.ADMIN_DB_DATABASE}"))
with admin_cluster_engine.connect() as connection:
    connection.execute(sqlalchemy.text("COMMIT"))  # Get out of transaction mode
    connection.execute(text(f"CREATE DATABASE {env.ADMIN_DB_DATABASE}"))

# Create the tables in the admin database
BaseAdminEntity.metadata.drop_all(admin_db_engine())
BaseAdminEntity.metadata.create_all(admin_db_engine())
