"""Definition of the `project_groups` table in the admin database."""

from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseAdminEntity
from typing import Optional


class ProjectGroupEntity(BaseAdminEntity):
    """Database model for the `project_groups` table."""

    """NOTE: This entity is a work-in-progress and is minimally viable for the db feature."""

    # Set the table name for the entity
    __tablename__ = "project_groups"

    # Unique ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Name of the group
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Assignment the group is for
    assignment_id: Mapped[int] = mapped_column(ForeignKey("assignments.id"))
    assignment: Mapped["AssignmentEntity"] = relationship(back_populates="project_groups")  # type: ignore

    # Members of the group (relationship with `project_group_members` table)
    members: Mapped[list["ProjectGroupMemberEntity"]] = relationship(  # type: ignore
        back_populates="group", cascade="all,delete"
    )

    # Project the group is for (relationship with `projects` table)
    project: Mapped[Optional["ProjectEntity"]] = relationship(back_populates="group")  # type: ignore
