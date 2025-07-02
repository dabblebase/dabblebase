"""Table storing information about users attached to a project."""

from enum import Enum
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseAdminEntity
from typing import Optional


class ProjectUserEntity(BaseAdminEntity):
    """Database model for the `project_users` table."""

    """NOTE: This entity is a work-in-progress and is minimally viable for the db feature."""

    # Set the table name for the entity
    __tablename__ = "project_users"

    # Unique ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # User for the membership relation (part of a composite key)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserEntity"] = relationship(back_populates="project_users")  # type: ignore

    # Name associated with the schema user that has permissions of the user
    schema_role_name: Mapped[str] = mapped_column(String, nullable=False)

    # Encrypted password of the schema user role for accessing the schema
    # Encrypted using a key generated via key expansion of the auth secret + assignment ID
    encrypted_schema_role_password: Mapped[str] = mapped_column(String, nullable=False)

    # Project group memberships of the user (relationship with `project_group_members` table)
    project_group_membership: Mapped[Optional["ProjectGroupMemberEntity"]] = relationship(  # type: ignore
        back_populates="project_user"
    )

    # Invididual projects the member is part of (relationship with `projects` table)
    individual_project: Mapped[Optional["ProjectEntity"]] = relationship(  # type: ignore
        back_populates="project_user"
    )
