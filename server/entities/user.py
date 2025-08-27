"""Definition of the `users` table in the admin database."""

from enum import Enum
from sqlalchemy import Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseAdminEntity
from ..models.auth import Subject
from pydantic import BaseModel


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

    # Username
    username: Mapped[str] = mapped_column(String, nullable=False)

    # Name
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)

    # Email
    email: Mapped[str] = mapped_column(String, nullable=False)

    # Course memberships of the user (relationship with `course_members` table)
    course_memberships: Mapped[list["CourseMemberEntity"]] = relationship(  # type: ignore
        back_populates="user", cascade="all,delete"
    )

    # Project users the user is tied to (project user relates to the db role that gives them access to a project)
    group_project_memberships: Mapped[list["ProjectGroupMemberEntity"]] = relationship(  # type: ignore
        back_populates="user", cascade="all,delete"
    )

    # Individual project the user is tied to (individual project relates to the db role that gives them access to a project)
    individual_projects: Mapped[list["ProjectEntity"]] = relationship(  # type: ignore
        back_populates="user", cascade="all,delete"
    )

    # All of the roles associated with the user.
    roles: Mapped[list["RoleEntity"]] = relationship(
        secondary="user_roles", back_populates="users"
    )

    def to_subject(self) -> Subject:
        """Convert the user entity to a Subject object."""
        return Subject(id=self.id)


class UserEntityModel(BaseModel):
    """Pydantic model for the `UserEntity`."""

    id: int
    auth_id: str
    auth_provider: UserAuthenticationProvider
    username: str
    first_name: str
    last_name: str
    email: str

    def to_entity(self) -> UserEntity:
        """Convert the Pydantic model to a UserEntity."""
        return UserEntity(
            id=self.id,
            auth_id=self.auth_id,
            auth_provider=self.auth_provider,
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
        )

    def to_subject(self) -> Subject:
        """Convert the user entity model to a Subject object."""
        return Subject(id=self.id)
