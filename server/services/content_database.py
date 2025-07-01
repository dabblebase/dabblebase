"""Service used to interface with the content database."""

from .base import BaseContentService
from ..env import env
from sqlalchemy import text
from .exceptions import ContentDatabaseTransactionException


class ContentDatabaseService(BaseContentService):

    def create_schema(self, schema_name: str):
        """
        Creates a new schema in the content database with the given name, as well as
        an owner role which can be granted to user roles for access. This created
        schema serves as a "private database" for a student project - a slice of the
        database that only postgres users granted the owner role can access.
        """
        # Set up a database transaction so that if any SQL commands fail, none
        # ultimately affect the database.
        try:
            # Create a schema with the schema name
            self._content_db.execute(
                text("CREATE SCHEMA :schema_name AUTHORIZATION :user"),
                {"schema_name": schema_name, "user": env.CONTENT_DB_USER},
            )
            # Create an owner role with full permissions to the schema
            owner_role_name = f"{schema_name}_owner"
            self._content_db.execute(
                text("CREATE ROLE :role_name NOLOGIN"),
                {"role_name": owner_role_name},
            )
            self._content_db.execute(
                text("GRANT USAGE ON SCHEMA :schema_name TO :role_name"),
                {"schema_name": schema_name, "role_name": owner_role_name},
            )
            self._content_db.execute(
                text("GRANT ALL ON ALL TABLES IN SCHEMA :schema_name TO :role_name"),
                {"schema_name": schema_name, "role_name": owner_role_name},
            )
            # Commit changes
            self._content_db.commit()
        except:
            self._content_db.rollback()
            raise ContentDatabaseTransactionException(f"Could not create schema.")

    def delete_schema(self, schema_name: str): ...

    def create_role_scoped_to_schema(self, role_name: str, schema_name: str): ...

    def delete_role(self, role_name: str): ...
