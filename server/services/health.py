"""
Verify connectivity of the server to other services including the database.
"""

from sqlalchemy import text
from .base import BaseService


class HealthService(BaseService):

    def check(self):
        statement = text("SELECT 'OK', NOW()")
        admin_db_response = self._admin_db.execute(statement).fetchone()
        content_db_response = self._content_db.execute(statement).fetchone()
        return f"admin db: {admin_db_response[0]} @ {admin_db_response[1]}, content db: {content_db_response[0]} @ {content_db_response[1]}"
