"""Association table between users and roles in the admin database."""

from .base import BaseAdminEntity
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class UserRoleEntity(BaseAdminEntity):
    """Database model for the `user_roles` table."""

    # Set the table name for the entity
    __tablename__ = "user_roles"

    # User assigned a role (part of a composite pkey)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    # Role assigned to a user (part of a composite key)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
