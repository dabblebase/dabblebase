"""Definition of the `permissions` table in the admin database."""

from .base import BaseAdminEntity
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PermissionEntity(BaseAdminEntity):
    """Database model for the `permissions` table."""

    # Set the table name for the entity
    __tablename__ = "permissions"

    # Unique ID for the permission entry
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Represents what a user or entity can do
    action: Mapped[str] = mapped_column(String)

    # Represents what which specific data the users can control
    resource: Mapped[str] = mapped_column(String)

    # Role permission is attached to
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    role: Mapped["RoleEntity"] = relationship(back_populates="permissions")  # type: ignore
