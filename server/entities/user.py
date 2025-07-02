"""Definition of the `users` table in the admin database."""

from enum import Enum
from sqlalchemy import Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseAdminEntity


class UserAuthenticationProvider(Enum):
    """Enum identifying the authentication provider used for a user."""

    UNC_SSO = "unc-sso"
    GOOGLE = "google"


class UserEntity(BaseAdminEntity):
    """Database model for the `users` table."""

    """NOTE: This entity is a work-in-progress and is minimally viable for the auth feature."""

    # Set the table name for the entity
    __tablename__ = "users"

    # Unique ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Unique identifier for the user according to their chosen authentication provider
    auth_id: Mapped[str] = mapped_column(String, nullable=False)

    # Auth provider used for the user
    auth_provider: Mapped[UserAuthenticationProvider] = mapped_column(
        SQLAlchemyEnum(UserAuthenticationProvider), nullable=False
    )

    # Course memberships of the user (relationship with `course_members` table)
    course_memberships: Mapped[list["CourseMemberEntity"]] = relationship(  # type: ignore
        back_populates="user", cascade="all,delete"
    )

    # Project users the user is tied to (project user relates to the db role that gives them access to a project)
    project_users: Mapped[list["ProjectUserEntity"]] = relationship(  # type: ignore
        back_populates="user", cascade="all,delete"
    )
