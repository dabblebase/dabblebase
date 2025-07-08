"""
Verify connectivity of the server to other services including the database.
"""

from sqlalchemy import text
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..database import admin_db_session, content_db_session


class HealthService:

    _admin_db: Session
    _content_db: Session

    def __init__(
        self,
        admin_db: Session = Depends(admin_db_session),
        content_db: Session = Depends(content_db_session),
    ):
        self._admin_db = admin_db
        self._content_db = content_db

    def check(self):
        statement = text("SELECT 'OK', NOW()")
        admin_db_response = self._admin_db.execute(statement).fetchone()
        content_db_response = self._content_db.execute(statement).fetchone()
        return f"admin db: {admin_db_response[0]} @ {admin_db_response[1]}, content db: {content_db_response[0]} @ {content_db_response[1]}"  # type: ignore
