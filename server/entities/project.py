"""Definition of the `projects` table in the admin database."""

from sqlalchemy import Integer, String, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseAdminEntity
from typing import Optional
from pydantic import BaseModel


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
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped[Optional["UserEntity"]] = relationship(back_populates="individual_projects")  # type: ignore

    # Name of the schema associated to the project
    db_name: Mapped[str] = mapped_column(String, nullable=False)

    # Encrypted private key used for project-specific authentication
    auth_encrypted_private_key: Mapped[str] = mapped_column(String, nullable=False)

    # Public key used for project-specific authentication
    auth_public_key: Mapped[str] = mapped_column(String, nullable=False)


class ProjectEntityModel(BaseModel):
    """Pydantic model for the `ProjectEntity`."""

    id: int
    assignment_id: int
    group_id: Optional[int]
    project_user_id: Optional[int]
    db_name: str
    auth_encrypted_private_key: str
    auth_public_key: str

    def to_entity(self) -> ProjectEntity:
        """Convert the Pydantic model to a ProjectEntity."""
        return ProjectEntity(
            id=self.id,
            assignment_id=self.assignment_id,
            group_id=self.group_id,
            project_user_id=self.project_user_id,
            db_name=self.db_name,
            auth_encrypted_private_key=self.auth_encrypted_private_key,
            auth_public_key=self.auth_public_key,
        )
