"""
Resets the database for development purposes.

This script deletes and recreates the database schema, reseting all data
to the seeded development data. The script can only be used in development
mode.

Usage: python3 -m scripts.reset_db
"""

import sys
import sqlalchemy
from ..env import env
from ..database import admin_db_engine, content_db_engine
from ..entities import BaseAdminEntity

# Ensures that the script can only be run in development mode
if env.MODE != "development":
    print("This script can only be run in development mode.", file=sys.stderr)
    exit(1)

# Create the tables in the admin database
BaseAdminEntity.metadata.drop_all(admin_db_engine)
BaseAdminEntity.metadata.create_all(admin_db_engine)
