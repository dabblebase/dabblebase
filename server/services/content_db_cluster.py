"""Service used to interface with the content database cluster."""

from .base import BaseContentService
from ..env import env
from sqlalchemy import text
from .exceptions import ContentDatabaseTransactionException
from .project import auth_crypto as crypto
from ..env import env


class ContentDbClusterService(BaseContentService):

    def _provision_database(self, db_name: str):
        """
        Provisions a new database in the content database cluster, creating an
        admin user with permissions to the database, and run any setup SQL
        on the database as needed. This method is run as a nested transaction.

        Critical
            - This method is run as a nested transaction, meaning that it is
               intended to be called within a transaction block. For example:
               ```
               with self._content_db.begin():
                 content_db_cluster_svc._provision_database(...)
               ```
               This ensures that if provisioning or any other subsequent cluster
               tasks fail, the entire operation can be rolled back without
               affecting the content database cluster.
            - The db name must be generated using `ContentDbClusterNamingConventions`
              to avoid SQL injection.
        """
        try:
            # Since creating a database cannot be run within a transaction and the
            # standard session is bound to a transaction, ensure that the 'create
            # database' step is performed in a separate connection to the engine
            with self._content_cluster_engine.connect().execution_options(
                isolation_level="AUTOCOMMIT"
            ) as conn:
                # Create the database with the provided name
                conn.execute(text(f"CREATE DATABASE {db_name}"))
            try:
                # Ensure that the database is private to all users by default
                self._content_db.execute(
                    text(f"REVOKE CONNECT ON DATABASE {db_name} FROM PUBLIC")
                )
            except Exception as e:
                # If we fail to revoke connect permissions, we should delete the
                # database we just created to avoid leaving it in a broken state.
                self._provision_database_rollback(db_name)
                raise ContentDatabaseTransactionException(
                    f"Could not provision database - error revoking connect permissions. Error: {e}"
                )
        except Exception as e:
            raise ContentDatabaseTransactionException(
                f"Could not provision database - error creating database. Error: {e}"
            )
        finally:
            # Ensure that the database is committed to the session
            self._content_db.commit()

    def _provision_database_rollback(self, db_name: str):
        """Attempts to roll back database creation in case something goes wrong."""
        try:
            # Drop all active connections to the database to prevent active connections
            # preventing the database drop.
            # SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'tenant123' AND pid <> pg_backend_pid();
            self._content_db.execute(
                text(
                    f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = :db_name AND pid <> pg_backend_pid()",
                ),
                {"db_name": db_name},
            )
            # Now drop the database
            self._content_db.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
        except Exception as e:
            raise ContentDatabaseTransactionException(
                f"Could not rollback provisioning the database. Error: {e}"
            )

    def _provision_role_for_database(
        self, db_name: str, role_name: str, role_password: str, readonly: bool = False
    ):
        """
        Provisions a new role for the database with the provided name.
        This method is run as a nested transaction.

        Critical
            - This method is run as a nested transaction, meaning that it is
              intended to be called within a transaction block. For example:
              ```
              with self._content_db.begin():
                content_db_cluster_svc._provision_role_for_database(...)
              ```
              This ensures that if provisioning or any other subsequent cluster
              tasks fail, the entire operation can be rolled back without
              affecting the content database cluster.
            - The db name and role name must be generated using `ContentDbClusterNamingConventions`
              to avoid SQL injection.
        """
        try:
            with self._content_db.begin_nested():
                # Create a new role with the provided name
                self._content_db.execute(
                    text(f"CREATE ROLE {role_name} LOGIN PASSWORD :role_password"),
                    {"role_password": role_password},
                )
                # Grant the role access to the database`
                self._content_db.execute(
                    text(f"GRANT CONNECT ON DATABASE {db_name} TO {role_name}")
                )
        except Exception as e:
            self._content_db.rollback()
            raise ContentDatabaseTransactionException(
                f"Could not provision role for database. Error: {e}"
            )
