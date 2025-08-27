"""Definition of the `roles` table in the admin database."""

from .base import BaseAdminEntity
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RoleEntity(BaseAdminEntity):
    """Database model for the `roles` table."""

    # Set the table name for the entity
    __tablename__ = "roles"

    # Unique ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Name of the role
    name: Mapped[str] = mapped_column(String, unique=True)

    # All of the users with this role.
    users: Mapped[list["UserEntity"]] = relationship(
        secondary="user_roles", back_populates="roles"
    )

    # All of the permissions with the given role.
    permissions: Mapped[list["PermissionEntity"]] = relationship(back_populates="role")
