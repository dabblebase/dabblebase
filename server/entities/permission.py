"""Definition of the `permissions` table in the admin database."""

from .base import BaseAdminEntity
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PermissionEntity(BaseAdminEntity):
    """Database model for the `permissions` table."""

    # Set the table name for the entity
    __tablename__ = "permissions"

    # Unique ID for the permission entry
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Represents what a user or entity can do
    action: Mapped[str] = mapped_column(String)

    # Represents what which specific data the users can control
    resource: Mapped[str] = mapped_column(String)

    # User assigned the permission
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    user: Mapped["UserEntity"] = relationship(back_populates="permissions")  # type: ignore
