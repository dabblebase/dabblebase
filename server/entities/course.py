"""Definition of the `courses` table in the admin database."""

from sqlalchemy import Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseAdminEntity
from datetime import datetime
from pydantic import BaseModel


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

    # Start time of the event
    start_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    # End time of the event
    end_date: Mapped[datetime] = mapped_column(Date, nullable=False)

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
    start_date: datetime
    end_date: datetime
    invite_code: str

    def to_entity(self) -> CourseEntity:
        """Convert the Pydantic model to a CourseEntity."""
        return CourseEntity(
            id=self.id,
            code=self.code,
            name=self.name,
            description=self.description,
            start_date=self.start_date,
            end_date=self.end_date,
            invite_code=self.invite_code,
        )
