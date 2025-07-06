"""Service used to interface with the content database cluster."""

from .base import BaseContentService
from ..env import env
from sqlalchemy import text, Engine, create_engine
from .exceptions import ContentDatabaseTransactionException
from .project import auth_crypto as crypto
from ..env import env, in_production


class ContentDbClusterService(BaseContentService):

    def provision_database(self, db_name: str) -> tuple[str, str]:
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
                role_name = ContentDatabaseNamingConventions.name_for_db_admin_role(
                    db_name
                )
                role_password = crypto.generate_secure_password()
                self.provision_role_for_database(db_name, role_name, role_password)
                # If all succeeds, return the role_name, and role_password
                return role_name, role_password
            except Exception as e:
                # If we fail to revoke connect permissions, we should delete the
                # database we just created to avoid leaving it in a broken state.
                self.delete_database(db_name)
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

    def delete_database(self, db_name: str):
        """Attempts to devprovision a given database."""
        try:
            # Drop all active connections to the database to prevent active connections
            # preventing the database drop.
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

    def provision_role_for_database(
        self,
        db_name: str,
        role_name: str,
        role_password: str,
        readonly: bool = False,
        issuer_role_name: str | None = None,
        issuer_role_password: str | None = None,
    ):
        """
        Provisions a new role for the database with the provided name. The role will be granted
        full access to the database and its public schema, assuming `readonly` is False.

        Note that if `issuer_role_name` and `issuer_role_password` are provided, then the new role will be
        provisioned by the issuer role. If not, the role will be provisioned by the superuser. This has
        interesting implications - new roles can only access items in the database that was created by the
        issuer. For this purpose, an admin role can be provisioned by the superuser, but then all other roles
        (especially readonly roles) should be provisioned by the admin role.

        Critical
            - The db name and role name must be generated using `ContentDbClusterNamingConventions`
              to avoid SQL injection.
        """
        self._content_db.rollback()
        try:
            # First, the creation of the role is always done by the superuser because
            # no other role can create other roles.
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
            # Then, permissions can be granted by either the superuser or the issuer role.
            engine = (
                self._engine_for_provisioned_db_as_user(
                    db_name, issuer_role_name, issuer_role_password
                )
                if issuer_role_name is not None and issuer_role_password is not None
                else self._engine_for_provisioned_db_as_superuser(db_name)
            )
            with engine.begin() as conn:
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

    def reset_database(
        self,
        db_name: str,
        role_name: str | None = None,
        role_password: str | None = None,
    ):
        """Resets a database in the content db cluster by dropping all user-defined objects."""
        # This SQL script contains the logic to drop all user-defined objects in the
        # database, which includes views, tables, sequences, functions, and types
        # (such as enums). This effectiely resets the database to a clean slate.
        drop_objects_sql_script = """
        DO $$
        DECLARE
            obj RECORD;
        BEGIN
            -- Drop views
            FOR obj IN
                SELECT table_name
                FROM information_schema.views
                WHERE table_schema = 'public'
            LOOP
                EXECUTE format('DROP VIEW IF EXISTS public.%I CASCADE', obj.table_name);
            END LOOP;

            -- Drop tables (this also drops RLS policies and constraints)
            FOR obj IN
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
            LOOP
                EXECUTE format('DROP TABLE IF EXISTS public.%I CASCADE', obj.tablename);
            END LOOP;

            -- Drop sequences
            FOR obj IN
                SELECT sequencename
                FROM pg_sequences
                WHERE schemaname = 'public'
            LOOP
                EXECUTE format('DROP SEQUENCE IF EXISTS public.%I CASCADE', obj.sequencename);
            END LOOP;

            -- Drop functions (includes overloaded ones)
            FOR obj IN
                SELECT p.oid::regprocedure::text AS funcsig
                FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname = 'public'
            LOOP
                EXECUTE format('DROP FUNCTION IF EXISTS %s CASCADE', obj.funcsig);
            END LOOP;

            -- Drop user-defined composite and enum types
            FOR obj IN
                SELECT t.typname
                FROM pg_type t
                JOIN pg_namespace n ON t.typnamespace = n.oid
                WHERE n.nspname = 'public'
                AND t.typtype IN ('e', 'c')  -- e = enum, c = composite
            LOOP
                EXECUTE format('DROP TYPE IF EXISTS public.%I CASCADE', obj.typname);
            END LOOP;
        END $$;
        """
        # Execute the SQL script to drop all user-defined objects in the database
        try:
            engine = (
                self._engine_for_provisioned_db_as_user(
                    db_name, role_name, role_password
                )
                if role_name is not None and role_password is not None
                else self._engine_for_provisioned_db_as_superuser(db_name)
            )
            with engine.begin() as conn:
                # Ensure we are not in a transaction
                conn = conn.execution_options(autocommit=False)
                conn.execute(text("ROLLBACK"))
                # Execute the SQL script to drop all user-defined objects
                conn.execute(text(drop_objects_sql_script))
        except Exception as e:
            raise ContentDatabaseTransactionException(
                f"Could not reset database. Error: {e}"
            )

    def run_sql_on_database(
        self, db_name: str, role_name: str, role_password: str, sql: str
    ):
        """
        Runs SQL on a target database as a role.
        """
        try:
            engine = self._engine_for_provisioned_db_as_user(
                db_name, role_name, role_password
            )
            with engine.begin() as conn:
                # Ensure we are not in a transaction
                conn = conn.execution_options(autocommit=False)
                conn.execute(text("ROLLBACK"))
                # Execute the SQL
                conn.execute(text(sql))
        except Exception as e:
            # Directly raise the SQL error up
            raise ContentDatabaseTransactionException(f"{e}")

    def db_url_for_provisioned_db(
        self, db_name: str, role_name: str, role_password: str
    ) -> str:
        """Generates the database URL for a provisioned database."""
        return f"postgresql+psycopg2://{role_name}:{role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{db_name}"

    def _engine_for_provisioned_db_as_superuser(self, db_name: str) -> Engine:
        """Generates the engine for a provisioned database as a superuser."""
        return create_engine(
            self.db_url_for_provisioned_db(
                db_name, env.ADMIN_DB_USER, env.ADMIN_DB_PASSWORD
            ),
            echo=not in_production(),
        )

    def _engine_for_provisioned_db_as_user(
        self, db_name: str, role_name: str, role_password: str
    ) -> Engine:
        """Generates the engine for a provisioned database as a superuser."""
        return create_engine(
            self.db_url_for_provisioned_db(db_name, role_name, role_password),
            echo=not in_production(),
        )

    def encrypt_role_password(self, password: str, assignment_id: int) -> str:
        """Encrypts the password for a role in the content database."""
        encryption_key = self._calculate_encryption_key_for_role_password(assignment_id)
        return crypto.encrypt(password, encryption_key)

    def decrypt_role_password(self, encrypted_password: str, assignment_id: int) -> str:
        """Decrypts the password for a role in the content database."""
        encryption_key = self._calculate_encryption_key_for_role_password(assignment_id)
        return crypto.decrypt(encrypted_password, encryption_key)

    def _calculate_encryption_key_for_role_password(self, assignment_id: int) -> bytes:
        """Rule for how the encryption key is calculated for role passwords."""
        return crypto.hkdf_derive_encryption_key(env.AUTH_MASTER_SECRET, assignment_id)


class ContentDatabaseNamingConventions:
    """
    Collection of naming conventions for content databases and roles.

    These must be used in conjunction with the `ContentDbClusterService` methods to
    prevent potential SQL injection risks.
    """

    @classmethod
    def name_for_assignment_test_db(cls, assignment_id: int) -> str:
        return f"assignment_{assignment_id}_test"

    @classmethod
    def name_for_db_admin_role(cls, db_name: str) -> str:
        return f"{db_name}_admin"

    @classmethod
    def name_for_assignment_test_db_readonly_role(cls, assignment_id: int) -> str:
        return f"assignment_{assignment_id}_test_view"

    @classmethod
    def name_for_assignment_db(cls, assignment_id: int, project_id: int) -> str:
        return f"assignment_{assignment_id}_project_{project_id}"

    @classmethod
    def name_for_assignment_db_user_role(
        cls, assignment_id: int, project_id: int, user_id: int
    ) -> str:
        return f"assignment_{assignment_id}_project_{project_id}_user_{user_id}"
