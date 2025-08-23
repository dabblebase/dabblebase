"""
Sets up the environment for production use, including setting up
the databases.

Note that this script only runs setup steps on the db clusters and
does not seed the database or perform any destructive actions (so,
it will likely fail if the production environment is already set up)

Usage: python3 -m server.scripts.setup_prod
"""

from ..seeds.demo import insert_seed_data as insert_demo_seed
from ..env import env
from ..configuration import (
    setup_admin_db_cluster,
    teardown_admin_db_cluster,
    setup_content_db_cluster,
    teardown_content_db_cluster,
)


setup_admin_db_cluster()
print("✅ Set up the admin db cluster")

setup_content_db_cluster()
print("✅ Set up the content db cluster")

print("🚀 Setup complete.")
print("⚠️ Please restart the pgbouncer instance before proceeding.")
