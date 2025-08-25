"""
Base entities for the admin database for which the other
entities inherit from.
"""

from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, Session


class BaseAdminEntity(DeclarativeBase):
    """
    Base class for all entities of the admin database.
    """

    pass
