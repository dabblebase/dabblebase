"""Service used to interface with the content database cluster."""

from .base import BaseContentService
from ..env import env
from sqlalchemy import text, Engine, create_engine
from ..services.content_database import ContentDatabaseNamingConventions
from .exceptions import ContentDatabaseTransactionException
from .project import auth_crypto as crypto
from ..env import env, in_production


class ContentDbClusterService(BaseContentService):

    def _provision_database(self, db_name: str) -> tuple[str, str]:
        """
        Provisions a new database in the content database cluster, creating an
        admin user with permissions to the database, and run any setup SQL
        on the database as needed.

        Critical:
            - The db name must be generated using `ContentDbClusterNamingConventions`
              to avoid SQL injection.

        Returns:
            - Admin role credentials of the generated database, displayed in a tuple
              of format (admin_role_name, admin_role_password)
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
                # Create a new role for the database
                role_name = (
                    ContentDatabaseNamingConventions.name_for_database_admin_role(
                        db_name
                    )
                )
                role_password = crypto.generate_secure_password()
                self._provision_role_for_database(db_name, role_name, role_password)
                # If all succeeds, return the role_name, and role_password
                return role_name, role_password
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
            # Now drop the database using the engine
            with self._content_cluster_engine.connect().execution_options(
                isolation_level="AUTOCOMMIT"
            ) as conn:
                conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
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
        self._content_db.rollback()
        try:
            with self._engine_for_provisioned_db_as_superuser(db_name).begin() as conn:
                # Create a new role with the provided name
                conn.execute(
                    text(f"CREATE ROLE {role_name} LOGIN PASSWORD :role_password"),
                    {"role_password": role_password},
                )
                # Grant the role access to the database
                conn.execute(
                    text(f"GRANT CONNECT ON DATABASE {db_name} TO {role_name}")
                )
                # Grant priveleges to the public schema of the database to the role
                schema_permissions = "ALL" if not readonly else "USAGE"
                conn.execute(
                    text(f"GRANT {schema_permissions} ON SCHEMA public TO {role_name}")
                )
                # Grant priveleges to objects within the public schema to the role
                object_permissions = "ALL" if not readonly else "SELECT"
                conn.execute(
                    text(
                        f"GRANT {object_permissions} ON ALL TABLES IN SCHEMA public TO {role_name}"
                    )
                )
                conn.execute(
                    text(
                        f"GRANT {object_permissions} ON ALL SEQUENCES IN SCHEMA public TO {role_name}"
                    )
                )
                if not readonly:
                    conn.execute(
                        text(
                            f"GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO {role_name}"
                        )
                    )
                # Alter the default privileges for the public schema to ensure that
                # any future objects created in the public schema will also be accessible
                # by the role.
                conn.execute(
                    text(
                        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT {object_permissions} ON TABLES TO {role_name}"
                    )
                )
                conn.execute(
                    text(
                        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT {object_permissions} ON SEQUENCES TO {role_name}"
                    )
                )
                if not readonly:
                    conn.execute(
                        text(
                            f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO {role_name}"
                        )
                    )
        except Exception as e:
            conn.rollback()
            raise ContentDatabaseTransactionException(
                f"Could not provision role for database. Error: {e}"
            )
        finally:
            conn.commit()

    def _engine_for_provisioned_db_as_superuser(self, db_name: str) -> Engine:
        """Generates the engine for a provisioned database as a superuser."""
        return create_engine(
            f"postgresql+psycopg2://{env.CONTENT_DB_USER}:{env.CONTENT_DB_PASSWORD}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{db_name}",
            echo=not in_production(),
        )
