"""Definition of the `courses` table in the admin database."""

from sqlalchemy import Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseAdminEntity
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum


class CourseTermType(Enum):
    """Enum identifying the type of term for a course."""

    FALL = "Fall"
    SPRING = "Spring"
    SUMMER = "Summer"
    WINTER = "Winter"

    def order(self):
        """Return the order of the terms for a given year."""
        ordering = {
            CourseTermType.SPRING: 1,
            CourseTermType.SUMMER: 2,
            CourseTermType.FALL: 3,
            CourseTermType.WINTER: 4,
        }
        return ordering[self]


class CourseEntity(BaseAdminEntity):
    """Database model for the `courses` table."""

    """NOTE: This entity is a work-in-progress and is minimally viable for the db feature."""

    # Set the table name for the entity
    __tablename__ = "courses"

    # Unique ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Course code
    code: Mapped[str] = mapped_column(String, nullable=False)

    # Name of the course
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Description of the course
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    # Term type of the course (e.g., Fall, Spring, etc.)
    term_type: Mapped[CourseTermType] = mapped_column(
        SQLAlchemyEnum(CourseTermType), nullable=False
    )

    # Term year
    term_year: Mapped[int] = mapped_column(Integer, nullable=False)

    # Invite code for students to join the course
    invite_code: Mapped[str] = mapped_column(
        String, nullable=False, unique=True, index=True
    )

    # Members of the course (relationship with `course_members` table)
    members: Mapped[list["CourseMemberEntity"]] = relationship(  # type: ignore
        back_populates="course", cascade="all,delete"
    )

    # Course assignments (relationship with `assignments` table)
    assignments: Mapped[list["AssignmentEntity"]] = relationship(  # type: ignore
        back_populates="course", cascade="all,delete"
    )


class CourseEntityModel(BaseModel):
    """Pydantic model for the `CourseEntity`."""

    id: int
    code: str
    name: str
    description: str | None = None
    term_type: CourseTermType
    term_year: int
    invite_code: str

    def to_entity(self) -> CourseEntity:
        """Convert the Pydantic model to a CourseEntity."""
        return CourseEntity(
            id=self.id,
            code=self.code,
            name=self.name,
            description=self.description,
            term_type=self.term_type,
            term_year=self.term_year,
            invite_code=self.invite_code,
        )
