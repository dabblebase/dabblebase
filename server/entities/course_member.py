"""Association table between `course` and `user` in the admin database."""

from enum import Enum
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseAdminEntity
from pydantic import BaseModel


class CourseMembershipRole(Enum):
    """Enum identifying the level of permissions for a course member."""

    OWNER = "owner"
    ADMIN = "admin"
    STAFF = "staff"
    STUDENT = "student"


class CourseMemberEntity(BaseAdminEntity):
    """Database model for the `course_members` table."""

    """NOTE: This entity is a work-in-progress and is minimally viable for the db feature."""

    # Set the table name for the entity
    __tablename__ = "course_members"

    # Course for the membership relation (part of a composite pkey)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    course: Mapped["CourseEntity"] = relationship(back_populates="members")  # type: ignore

    # User for the membership relation (part of a composite key)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    user: Mapped["UserEntity"] = relationship(back_populates="course_memberships")  # type: ignore

    # Auth provider used for the user
    role: Mapped[CourseMembershipRole] = mapped_column(
        SQLAlchemyEnum(CourseMembershipRole), nullable=False
    )


class CourseMemberEntityModel(BaseModel):
    """Pydantic model for the `CourseMemberEntity`."""

    course_id: int
    user_id: int
    role: CourseMembershipRole

    def to_entity(self) -> CourseMemberEntity:
        """Convert the Pydantic model to a CourseMemberEntity."""
        return CourseMemberEntity(
            course_id=self.course_id,
            user_id=self.user_id,
            role=self.role,
        )
