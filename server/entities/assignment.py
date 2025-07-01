"""Definition of the `assignments` table in the admin database."""

from sqlalchemy import Integer, ForeignKey, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseAdminEntity


class AssignmentEntity(BaseAdminEntity):
    """Database model for the `assignments` table."""

    """NOTE: This entity is a work-in-progress and is minimally viable for the db feature."""

    # Set the table name for the entity
    __tablename__ = "assignments"

    # Unique ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Name of the assignment
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Course the assignment is for
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    course: Mapped["CourseEntity"] = relationship(back_populates="assignments")  # type: ignore

    # Whether or not the assignment is a group assignment - if false, the assignment is individual
    is_group_assignment: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Projects (relationship with `project_groups` table)
    projects: Mapped[list["ProjectEntity"]] = relationship(  # type: ignore
        back_populates="assignment", cascade="all,delete"
    )

    # Project groups (relationship with `project_groups` table) - len only >1 if is_group_assignment is true
    project_groups: Mapped[list["ProjectGroupEntity"]] = relationship(  # type: ignore
        back_populates="assignment", cascade="all,delete"
    )
