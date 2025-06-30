"""
Base entities for the admin database for which the other
entities inherit from.
"""

from sqlalchemy.orm import DeclarativeBase


class BaseAdminEntity(DeclarativeBase):
    """
    Base class for all entities of the admin database.
    """

    pass
