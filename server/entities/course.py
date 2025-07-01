"""Definition of the `courses` table in the admin database."""

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseAdminEntity


class CourseEntity(BaseAdminEntity):
    """Database model for the `courses` table."""

    """NOTE: This entity is a work-in-progress and is minimally viable for the db feature."""

    # Set the table name for the entity
    __tablename__ = "courses"

    # Unique ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Members of the course (relationship with `course_members` table)
    members: Mapped[list["CourseMemberEntity"]] = relationship(  # type: ignore
        back_populates="course", cascade="all,delete"
    )

    # Course assignments (relationship with `assignments` table)
    assignments: Mapped[list["AssignmentEntity"]] = relationship(  # type: ignore
        back_populates="course", cascade="all,delete"
    )
