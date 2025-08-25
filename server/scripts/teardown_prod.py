"""
Tears down the production environment.

THIS IS A DANGEROUS OPERATION! DO NOT RUN IT IN PRODUCTION UNLESS
YOU ARE SURE THAT YOU WANT ALL DATA ERASED.

Usage: python3 -m server.scripts.teardown_prod
"""

from ..configuration import (
    teardown_admin_db_cluster,
    teardown_content_db_cluster,
)


teardown_admin_db_cluster()
print("✅ Tore down the admin db cluster")

teardown_content_db_cluster()
print("✅ Set up the content db cluster")

print("🚀 Teardown complete.")
