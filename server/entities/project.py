"""Definition of the `projects` table in the admin database."""

from sqlalchemy import Integer, String, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseAdminEntity
from typing import Optional


class ProjectEntity(BaseAdminEntity):
    """Database model for the `projects` table."""

    """NOTE: This entity is a work-in-progress and is minimally viable for the auth feature."""

    # Set the table name for the entity
    __tablename__ = "projects"

    # Unique ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Assignment the project is for
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("assignments.id"), nullable=False
    )
    assignment: Mapped["AssignmentEntity"] = relationship(back_populates="projects")  # type: ignore

    # Group for the project if the assignment is a group project - otherwise, this is null
    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("project_groups.id"), nullable=True
    )
    group: Mapped[Optional["ProjectGroupEntity"]] = relationship(back_populates="project")  # type: ignore

    # User for the project if the assignment is an individual project - otherwise, this is null
    project_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("project_users.id"), nullable=True
    )
    project_user: Mapped[Optional["ProjectUserEntity"]] = relationship(back_populates="individual_project")  # type: ignore

    # Name of the schema associated to the project
    schema_name: Mapped[str] = mapped_column(String, nullable=False)

    # Role generated with the schema that has permissions over the schema
    # This role can then be granted to project users so that their roles
    # have access to operations on the schema.
    schema_role_name: Mapped[str] = mapped_column(String, nullable=False)

    # Encrypted private key used for project-specific authentication
    auth_encrypted_private_key: Mapped[str] = mapped_column(String, nullable=True)

    # Public key used for project-specific authentication
    auth_public_key: Mapped[str] = mapped_column(String, nullable=True)
