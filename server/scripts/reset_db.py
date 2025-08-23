"""
Resets the database for development purposes.

This script deletes and recreates the database schema, reseting all data
to the seeded development data. The script can only be used in development
mode.

Usage: python3 -m scripts.reset_db
"""

import sys
from sqlalchemy.orm import Session
from sqlalchemy import text

from server.database import admin_db_engine
from server.tests.services.seed import insert_seed_data
from ..env import env

# from ..database import admin_db_engine
from ..configuration import (
    setup_admin_db_cluster,
    teardown_admin_db_cluster,
    setup_content_db_cluster,
    teardown_content_db_cluster,
)

# Ensures that the script can only be run in development mode
if env.MODE != "development":
    print("This script can only be run in development mode.", file=sys.stderr)
    exit(1)

# Reset the admin db cluster
teardown_admin_db_cluster()
print("✅ Cleared the admin db cluster")
setup_admin_db_cluster()
print("✅ Set up the admin db cluster")
# Reset the content db cluster
teardown_content_db_cluster()
print("✅ Cleared the content db cluster")
setup_content_db_cluster()
print("✅ Set up the content db cluster")

# Seed the data
# TODO: Separate seed data for testing and for demo purposes
session = Session(admin_db_engine())
insert_seed_data(session)
