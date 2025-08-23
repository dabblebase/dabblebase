"""
Sets up the development environment for local use, including setting up
the databases and seeding the database with the demo data.

Usage: python3 -m server.scripts.setup_dev
"""

from ..seeds.demo import insert_seed_data as insert_demo_seed
from ..env import env
from ..configuration import (
    setup_admin_db_cluster,
    teardown_admin_db_cluster,
    setup_content_db_cluster,
    teardown_content_db_cluster,
)

# Ensures that the script can only be run in development mode
if env.MODE != "development":
    print("❌ This script can only be run in development mode.")
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

insert_demo_seed()
print("🌱 Seeded the database with demo data")

print("🚀 Setup complete.")
print("⚠️ Please restart the pgbouncer instance in the devcontainer before proceeding.")
