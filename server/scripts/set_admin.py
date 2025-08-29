"""
Elevates a user to admin permissions.

Usage: python3 -m server.scripts.set_admin <user ID>
"""

import argparse
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from server.database import admin_db_cluster_url, admin_db_url
from server.models.auth import Subject
from server.services.permission import PermissionService


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments and validate types"""
    parser = argparse.ArgumentParser(
        prog="python -m server.scripts.set_admin",
        description="Elevate a user (by numeric ID) to admin permissions",
    )
    parser.add_argument(
        "user_id",
        type=int,
        help="Numeric user ID to elevate",
    )
    return parser.parse_args()


def main() -> None:
    """Runner for the script"""
    # Parse the user ID as an int
    args = parse_args()
    user_id: int = args.user_id

    # Connect to the admin database
    admin_db_engine = create_engine(admin_db_url())
    session = Session(admin_db_engine)

    # Try to elevate the user to admin status
    try:
        permission_svc = PermissionService(session)
        permission_svc.grant_superuser_permission(Subject(id=user_id))
        print(f"✅ Successfully added admin permissions for user {user_id}")
    except Exception as e:
        print(f"❌ Failed to add admin permissions for user {user_id} with reason: {e}")
    finally:
        # Close the session
        session.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
