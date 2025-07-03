"""Service used to interface with the content database."""

from .base import BaseContentService
from ..env import env
from sqlalchemy import text
from .exceptions import ContentDatabaseTransactionException
from .project import auth_crypto as crypto
from ..env import env
import secrets
import base64


class ContentDatabaseService(BaseContentService):

    def create_schema(self, schema_name: str):
        """
        Creates a new schema in the content database with the given name, as well as
        an owner role which can be granted to user roles for access. This created
        schema serves as a "private database" for a student project - a slice of the
        database that only postgres users granted the owner role can access.

        Critical:
            - This function must be called within a transaction block. For example:
                ```
                with self._content_db.begin():
                    content_db_svc.create_schema("...")
                ```
            - The schema name must be generated using `ContentDatabaseNamingConventions`
            to avoid SQL injection.
        """
        # Set up a database transaction so that if any SQL commands fail, none
        # ultimately affect the database.
        try:
            with self._content_db.begin_nested():
                # Create a schema with the schema name
                self._content_db.execute(
                    text(
                        f"CREATE SCHEMA {schema_name} AUTHORIZATION {env.CONTENT_DB_USER}"
                    ),
                )
                # Create an owner role with full permissions to the schema
                # owner_role_name = f"{schema_name}"
                # self._content_db.execute(
                #     text(f"CREATE ROLE {owner_role_name} NOLOGIN"),
                # )
                # self._content_db.execute(
                #     text(f"GRANT USAGE ON SCHEMA {schema_name} TO {owner_role_name}"),
                # )
                # # Grant all permissions on current items in the database
                # self._content_db.execute(
                #     text(
                #         f"GRANT ALL ON ALL TABLES IN SCHEMA {schema_name} TO {owner_role_name}"
                #     ),
                # )
                # self._content_db.execute(
                #     text(
                #         f"GRANT ALL ON ALL SEQUENCES IN SCHEMA {schema_name} TO {owner_role_name}"
                #     ),
                # )
                # self._content_db.execute(
                #     text(
                #         f"GRANT ALL ON ALL FUNCTIONS IN SCHEMA {schema_name} TO {owner_role_name}"
                #     ),
                # )
                # # Alter priveleges so the user has access when new items are created in the database
                # self._content_db.execute(
                #     text(
                #         f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT ALL ON TABLES TO {owner_role_name}"
                #     ),
                # )
                # self._content_db.execute(
                #     text(
                #         f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT ALL ON SEQUENCES TO {owner_role_name}"
                #     ),
                # )
                # self._content_db.execute(
                #     text(
                #         f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT ALL ON FUNCTIONS TO {owner_role_name}"
                #     ),
                # )
        except Exception as e:
            self._content_db.rollback()
            raise ContentDatabaseTransactionException(
                f"Could not create schema. Error: {e}"
            )

    def delete_schema(self, schema_name: str): ...

    def create_role_scoped_to_schema(
        self,
        role_name: str,
        role_password: str,
        schema_name: str,
        readonly: bool = False,
    ):
        """
        Creates a new role scoped to a provided schema such that accessing the database
        using the role treats the schema as the role's entire database - allowing for
        simulating a private database environment from within one large database.

        Critical:
            - This function must be called within a transaction block. For example:
                ```
                with self._content_db.begin():
                    content_db_svc.create_role_scoped_to_schema(...)
                ```
            - The schema name and role name must be generated using
              `ContentDatabaseNamingConventions` to avoid SQL injection.
        """
        # Set up a database transaction so that if any SQL commands fail, none
        # ultimately affect the database.
        try:
            with self._content_db.begin_nested():
                # Create role with the provided name and password
                self._content_db.execute(
                    text(f"CREATE ROLE {role_name} LOGIN PASSWORD :role_password"),
                    {"role_password": role_password},
                )

                if not readonly:
                    # Grant schema-level permissions
                    self._content_db.execute(
                        text(
                            f"GRANT USAGE, CREATE ON SCHEMA {schema_name} TO {role_name}"
                        ),
                    )
                    # Grant permissions on existing objects, if any
                    self._content_db.execute(
                        text(
                            f"GRANT ALL ON ALL TABLES IN SCHEMA {schema_name} TO {role_name}"
                        ),
                    )
                    self._content_db.execute(
                        text(
                            f"GRANT ALL ON ALL SEQUENCES IN SCHEMA {schema_name} TO {role_name}"
                        ),
                    )
                    self._content_db.execute(
                        text(
                            f"GRANT ALL ON ALL FUNCTIONS IN SCHEMA {schema_name} TO {role_name}"
                        ),
                    )
                    # Alter privileges to grant permissions on future objects
                    self._content_db.execute(
                        text(
                            f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT ALL ON TABLES TO {role_name}"
                        ),
                    )
                    self._content_db.execute(
                        text(
                            f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT ALL ON SEQUENCES TO {role_name}"
                        ),
                    )
                    self._content_db.execute(
                        text(
                            f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT ALL ON FUNCTIONS TO {role_name}"
                        ),
                    )
                else:
                    # If readonly (used only in creating the view schema role for test schemas),
                    # we want to create the new role and only grant view access.
                    # TODO: PROB BROKEN
                    self._content_db.execute(
                        text(
                            f"GRANT USAGE, CREATE ON SCHEMA {schema_name} TO {role_name}"
                        ),
                    )
                    # Grant read-only access to all current items in the schema
                    self._content_db.execute(
                        text(
                            f"GRANT SELECT ON ALL TABLES IN SCHEMA {schema_name} TO {role_name}"
                        ),
                    )
                    self._content_db.execute(
                        text(
                            f"GRANT SELECT ON ALL SEQUENCES IN SCHEMA {schema_name} TO {role_name}"
                        ),
                    )
                    self._content_db.execute(
                        text(
                            f"GRANT SELECT ON ALL SEQUENCES IN SCHEMA {schema_name} TO {role_name}"
                        ),
                    )
                    # Alter privileges to grant read-only access to all future item in the schema
                    self._content_db.execute(
                        text(
                            f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT SELECT ON TABLES TO {role_name}"
                        ),
                    )
                    self._content_db.execute(
                        text(
                            f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT SELECT ON SEQUENCES TO {role_name}"
                        ),
                    )

                # Set the `search_path` for the role so that it limits the ability of the role to see
                # anything past the schema they are being attached to
                self._content_db.execute(
                    text(f"ALTER ROLE {role_name} SET search_path = {schema_name}"),
                )
                # Finally, we wnat to revoke the role's ability to access the public schema in any way,
                # as well as any information about other roles in the database.
                self._content_db.execute(
                    text(f"REVOKE ALL ON SCHEMA public FROM {role_name}")
                )
                self._content_db.execute(
                    text(f"REVOKE ALL ON pg_authid FROM {role_name}")
                )
                self._content_db.execute(
                    text(f"REVOKE ALL ON pg_roles FROM {role_name}")
                )
                self._content_db.execute(
                    text(f"REVOKE ALL ON pg_user FROM {role_name}")
                )
                self._content_db.execute(
                    text(f"REVOKE ALL ON pg_database FROM {role_name}")
                )
                self._content_db.execute(
                    text(f"REVOKE ALL ON information_schema.schemata FROM {role_name}")
                )
                self._content_db.execute(
                    text(f"REVOKE ALL ON information_schema.tables FROM {role_name}")
                )
                self._content_db.execute(
                    text(f"REVOKE ALL ON information_schema.columns FROM {role_name}")
                )
                self._content_db.execute(
                    text(
                        f"REVOKE ALL ON information_schema.table_constraints FROM {role_name}"
                    )
                )
                self._content_db.execute(
                    text(
                        f"REVOKE ALL ON information_schema.key_column_usage FROM {role_name}"
                    )
                )
                self._content_db.execute(
                    text(f"REVOKE ALL ON pg_catalog.pg_tables FROM {role_name}")
                )
                self._content_db.execute(
                    text(f"REVOKE ALL ON pg_catalog.pg_class FROM {role_name}")
                )
                self._content_db.execute(
                    text(f"REVOKE ALL ON pg_catalog.pg_namespace FROM {role_name}")
                )
                self._content_db.execute(
                    text(f"REVOKE ALL ON pg_catalog.pg_roles FROM {role_name}")
                )
                self._content_db.execute(
                    text(f"REVOKE ALL ON pg_catalog.pg_user FROM {role_name}")
                )
                self._content_db.execute(
                    text(
                        f"REVOKE EXECUTE ON FUNCTION pg_catalog.pg_table_is_visible(oid) FROM PUBLIC"
                    )
                )

        except Exception as e:
            self._content_db.rollback()
            raise ContentDatabaseTransactionException(
                f"Could not create schema role: {e}"
            )

    def delete_role(self, role_name: str): ...

    def encrypt_role_password(self, password: str, assignment_id: int) -> str:
        encryption_key = self._calculate_encryption_key_for_role_password(assignment_id)
        return crypto.encrypt(password, encryption_key)

    def decrypt_role_password(self, encrypted_password: str, assignment_id: int) -> str:
        encryption_key = self._calculate_encryption_key_for_role_password(assignment_id)
        return crypto.decrypt(encrypted_password, encryption_key)

    def _calculate_encryption_key_for_role_password(self, assignment_id: int) -> bytes:
        return crypto.hkdf_derive_encryption_key(env.AUTH_MASTER_SECRET, assignment_id)


class ContentDatabaseNamingConventions:

    @classmethod
    def name_for_assignment_test_schema(cls, assignment_id: int) -> str:
        return f"assignment_{assignment_id}_test"

    @classmethod
    def name_for_database_admin_role(cls, db_name: str) -> str:
        return f"{db_name}_admin"

    # @classmethod
    # def name_for_assignment_test_schema_admin_role(cls, assignment_id: int) -> str:
    #     return f"assignment_{assignment_id}_test_admin"

    @classmethod
    def name_for_assignment_test_db_readonly_role(cls, assignment_id: int) -> str:
        return f"assignment_{assignment_id}_test_view"

    @classmethod
    def name_for_assignment_schema(cls, assignment_id: int, project_id: int) -> str:
        return f"assignment_{assignment_id}_project_{project_id}"

    @classmethod
    def name_for_assignment_schema_permission_role(
        cls, assignment_id: int, project_id: int
    ) -> str:
        return f"assignment_{assignment_id}_project_{project_id}"

    @classmethod
    def name_for_assignment_schema_user_role(
        cls, assignment_id: int, project_id: int, user_id: int
    ) -> str:
        return f"assignment_{assignment_id}_project_{project_id}_user_{user_id}"
