"""Definition of the `projects` table in the admin database."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseAdminEntity


class ProjectEntity(BaseAdminEntity):
    """Database model for the `projects` table."""

    """NOTE: This entity is a work-in-progress and is minimally viable for the auth feature."""

    # Set the table name for the entity
    __tablename__ = "projects"

    # Unique ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Encrypted private key used for project-specific authentication
    auth_encrypted_private_key: Mapped[str] = mapped_column(String, nullable=False)
    # Public key used for project-specific authentication
    auth_public_key: Mapped[str] = mapped_column(String, nullable=False)
