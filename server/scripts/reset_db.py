"""
Resets the database for development purposes.

This script deletes and recreates the database schema, reseting all data
to the seeded development data. The script can only be used in development
mode.

Usage: python3 -m scripts.reset_db
"""

import sys
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..env import env
from ..entities import BaseAdminEntity
from ..database import admin_db_engine
from ..tests.services.seed import insert_seed_data
from ..tests.services.conftest import reset_database

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

# Run the reset script on the content database
reset_database(
    database=None,
    user=env.CONTENT_DB_USER,
    database_url_fn=lambda db: f"postgresql+psycopg2://{env.CONTENT_DB_USER}:{env.CONTENT_DB_PASSWORD}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{db}",
)

# Create the tables in the admin database
BaseAdminEntity.metadata.drop_all(admin_db_engine())
BaseAdminEntity.metadata.create_all(admin_db_engine())

# Insert seed data
# TODO: Separate seed data for testing and for demo purposes
session = Session(admin_db_engine())
BaseAdminEntity.setup_functions(session)
insert_seed_data(session)
