"""Definition of the `users` table in the admin database."""

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseAdminEntity


class UserEntity(BaseAdminEntity):
    """Database model for the `users` table."""

    """NOTE: This entity is a work-in-progress and is minimally viable for the auth feature."""

    # Set the table name for the entity
    __tablename__ = "users"

    # Unique ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
