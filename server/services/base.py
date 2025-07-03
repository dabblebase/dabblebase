"""
Create a primitive base service that provides access to the injected
database connections.
"""

from fastapi import Depends
from sqlalchemy import text, Engine
from sqlalchemy.orm import Session
from ..database import admin_db_session, content_db_session, content_db_engine


class BaseService:

    _admin_db: Session

    def __init__(
        self,
        admin_db: Session = Depends(admin_db_session),
    ):
        self._admin_db = admin_db


class BaseContentService:
    _content_db: Session
    _content_cluster_engine: Engine

    def __init__(
        self,
        content_db: Session = Depends(content_db_session),
        content_cluster_engine: Engine = Depends(content_db_engine),
    ):
        self._content_db = content_db
        self._content_cluster_engine = content_cluster_engine
