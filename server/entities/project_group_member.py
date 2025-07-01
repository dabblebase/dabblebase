"""Association table between `project_group` and `user` in the admin database."""

from enum import Enum
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseAdminEntity


class ProjectGroupMemberEntity(BaseAdminEntity):
    """Database model for the `project_group_members` table."""

    """NOTE: This entity is a work-in-progress and is minimally viable for the db feature."""

    # Set the table name for the entity
    __tablename__ = "project_group_members"

    # Group for the membership relation (part of a composite pkey)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("project_groups.id"), primary_key=True
    )
    group: Mapped["ProjectGroupEntity"] = relationship(back_populates="members")  # type: ignore

    # User for the membership relation (part of a composite key)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    user: Mapped["UserEntity"] = relationship(back_populates="project_group_memberships")  # type: ignore

    # Name associated with the schema user that has permissions of the user
    schema_role_name: Mapped[str] = mapped_column(String, nullable=False)
