"""Definition of the `assignments` table in the admin database."""

from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Integer, ForeignKey, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseAdminEntity
from pydantic import BaseModel


class AssignmentState(Enum):
    """Enum identifying the various states an assignment can be in."""

    DRAFT = "draft"
    UNPUBLISHED = "unpublished"
    PUBLISHED = "published"


class AssignmentEntity(BaseAdminEntity):
    """Database model for the `assignments` table."""

    """NOTE: This entity is a work-in-progress and is minimally viable for the db feature."""

    # Set the table name for the entity
    __tablename__ = "assignments"

    # Unique ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Name of the assignment
    name: Mapped[str] = mapped_column(String, nullable=False)

    # State of the assignment
    state: Mapped[AssignmentState] = mapped_column(
        SQLAlchemyEnum(AssignmentState), nullable=False, default=AssignmentState.DRAFT
    )

    # Course the assignment is for
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    course: Mapped["CourseEntity"] = relationship(back_populates="assignments")  # type: ignore

    # Whether or not the assignment is a group assignment - if false, the assignment is individual
    is_group_assignment: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Custom configuration SQL to run when creating projects for this assignment
    project_configuration_sql: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Draft configuration SQL used when edting the SQL configuration
    draft_project_configuration_sql: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # Whether or not the draft project configuration SQL successfully ran on the DB cluster
    draft_project_configuration_sql_succeeded: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )

    # Error message if the draft project configuration SQL did not run successfully
    draft_project_configuration_sql_error: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # Name of the test db generated with the project
    test_db_name: Mapped[str | None] = mapped_column(String, nullable=True)

    # Name of the test db user admin role for accessing the test db
    # This role is used internally by Dabblebase to apply the configuration SQL.
    test_db_admin_role_name: Mapped[str | None] = mapped_column(String, nullable=True)

    # Encrypted password of the test db user admin role for accessing the test db
    # Encrypted using a key generated via key expansion of the auth secret + assignment ID
    encrypted_test_db_admin_role_password: Mapped[str | None] = mapped_column(
        String, nullable=True
    )

    # Name of the test db user admin role for accessing the test db
    # This role and password is ultimately shared with the instructor so that they can view
    # their test db after sql has been applied. The db role has been separated from
    # the test db admin role so that this role can function as a read-only role that
    # is exposed to the instructor
    test_db_view_role_name: Mapped[str | None] = mapped_column(String, nullable=True)

    # Encrypted password of the test db user role for accessing the test db
    # Encrypted using a key generated via key expansion of the auth secret + assignment ID
    encrypted_test_db_view_role_password: Mapped[str | None] = mapped_column(
        String, nullable=True
    )

    # Projects (relationship with `project_groups` table)
    projects: Mapped[list["ProjectEntity"]] = relationship(  # type: ignore
        back_populates="assignment", cascade="all,delete"
    )

    # Project groups (relationship with `project_groups` table) - len only >1 if is_group_assignment is true
    project_groups: Mapped[list["ProjectGroupEntity"]] = relationship(  # type: ignore
        back_populates="assignment", cascade="all,delete"
    )


class AssignmentEntityModel(BaseModel):
    """Pydantic model for the `AssignmentEntity`"""

    id: int
    name: str
    state: AssignmentState
    course_id: int
    is_group_assignment: bool
    project_configuration_sql: str | None = None
    draft_project_configuration_sql: str | None = None
    draft_project_configuration_sql_succeeded: bool | None = None
    draft_project_configuration_sql_error: str | None = None
    test_db_name: str | None = None
    test_db_admin_role_name: str | None = None
    encrypted_test_db_admin_role_password: str | None = None
    test_db_view_role_name: str | None = None
    encrypted_test_db_view_role_password: str | None = None

    def to_entity(self) -> AssignmentEntity:
        """Convert the Pydantic model to an `AssignmentEntity`."""
        return AssignmentEntity(
            id=self.id,
            name=self.name,
            state=self.state,
            course_id=self.course_id,
            is_group_assignment=self.is_group_assignment,
            project_configuration_sql=self.project_configuration_sql,
            draft_project_configuration_sql=self.draft_project_configuration_sql,
            draft_project_configuration_sql_succeeded=self.draft_project_configuration_sql_succeeded,
            draft_project_configuration_sql_error=self.draft_project_configuration_sql_error,
            test_db_name=self.test_db_name,
            test_db_admin_role_name=self.test_db_admin_role_name,
            encrypted_test_db_admin_role_password=self.encrypted_test_db_admin_role_password,
            test_db_view_role_name=self.test_db_view_role_name,
            encrypted_test_db_view_role_password=self.encrypted_test_db_view_role_password,
        )
