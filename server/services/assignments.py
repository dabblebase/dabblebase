"""Service used to interface with assignments"""

from fastapi import Depends
from sqlalchemy import select
from ..entities import (
    CourseMembershipRole,
    AssignmentEntity,
    ProjectGroupEntity,
    ProjectGroupMemberEntity,
    AssignmentState,
    ProjectEntity,
    CourseMemberEntity,
    UserEntity,
)
from ..services.courses import CourseService
from ..services.content_db_cluster import (
    ContentDbClusterService,
    ContentDatabaseNamingConventions,
)
from ..services.project import auth_crypto as crypto
from ..models.auth import Subject
from ..models.assignment import (
    GetDropdownRequest,
    GetDropdownResponse_Assignment,
    GetDropdownResponse,
    GetViewResponse,
    GetDraftResponse,
    GetConfigurationSQLResponse,
    CreateDraftRequest,
    CreateDraftResponse,
    RenameRequest,
    TestConfigurationSQLRequest,
    TestConfigurationSQLResponse,
    GetGroupsResponse_User,
    GetGroupsResponse_Group,
    GetGroupsResponse,
    CreateGroupRequest,
    CreateGroupResponse,
    RenameGroupRequest,
    AddGroupMemberRequest,
    RemoveGroupMemberRequest,
    DeleteGroupRequest,
)
from ..database import admin_db_session
from sqlalchemy.orm import Session, joinedload
from .exceptions import (
    ContentDatabaseTransactionException,
    ResourceNotFoundException,
    InputValidationException,
)
from ..env import env


class AssignmentService:

    _admin_db: Session

    def __init__(
        self,
        admin_db: Session = Depends(admin_db_session),
        courses_svc: CourseService = Depends(),
        content_db_cluster_svc: ContentDbClusterService = Depends(),
    ):
        self._admin_db = admin_db
        self._courses_svc = courses_svc
        self._content_db_cluster_svc = content_db_cluster_svc

    def get_dropdown(self, subject: Subject, request: GetDropdownRequest):
        ...
        """Gets the content for the assignments dropdown for a course."""
        # Check for permissions
        role = self._courses_svc.verify_subject_has_permissions_for_course(
            subject,
            request.course_id,
            CourseMembershipRole.STUDENT,
        )

        # Get the selected assignment, if provided
        selected_assignment_query = select(AssignmentEntity).where(
            AssignmentEntity.id == request.selected_assignment_id,
        )
        if role == CourseMembershipRole.STUDENT:
            selected_assignment_query = selected_assignment_query.where(
                AssignmentEntity.state == AssignmentState.PUBLISHED
            )
        selected_assignment: AssignmentEntity | None = self._admin_db.scalars(
            selected_assignment_query
        ).one_or_none()

        self._admin_db.get(AssignmentEntity, request.selected_assignment_id)
        selected_assignment_model = (
            GetDropdownResponse_Assignment(
                id=selected_assignment.id,
                name=selected_assignment.name,
                state=selected_assignment.state,
            )
            if selected_assignment
            else None
        )

        # Get all of the assignments for the course - only published if student
        assignments_query = select(AssignmentEntity).where(
            AssignmentEntity.course_id == request.course_id
        )
        if len(request.search) > 0:
            assignments_query = assignments_query.where(
                AssignmentEntity.name.ilike(f"%{request.search}%")
            )
        if role == CourseMembershipRole.STUDENT:
            assignments_query = assignments_query.where(
                AssignmentEntity.state == AssignmentState.PUBLISHED
            )
        assignments = self._admin_db.scalars(assignments_query).all()

        # Convert the assignments to the response model
        assignments_model = [
            GetDropdownResponse_Assignment(
                id=assignment.id,
                name=assignment.name,
                state=assignment.state,
            )
            for assignment in assignments
        ]

        # Return the response model
        return GetDropdownResponse(
            assignments=assignments_model,
            selected_assignment=selected_assignment_model,
        )

    def get_view(self, subject: Subject, assignment_id: int):
        """Facts to decide which view to show to the user."""
        # Get the assignment
        assignment: AssignmentEntity | None = (
            self._admin_db.query(AssignmentEntity)
            .where(AssignmentEntity.id == assignment_id)
            .one_or_none()
        )

        if not assignment:
            raise ResourceNotFoundException(
                f"Assignment with ID {assignment_id} not found."
            )

        # Check for permission
        role = self._courses_svc.verify_subject_has_permissions_for_course(
            subject, assignment.course_id, CourseMembershipRole.STUDENT
        )

        # Conditions where the user should be redirected to the course page
        should_redirect = (
            role == CourseMembershipRole.STUDENT
            and assignment.state
            in {
                AssignmentState.DRAFT,
                AssignmentState.UNPUBLISHED,
            }
        ) or (
            role == CourseMembershipRole.STAFF
            and assignment.state == AssignmentState.DRAFT
        )

        return GetViewResponse(
            role=role,
            assignment_state=assignment.state,
            should_redirect=should_redirect,
        )

    def get_draft(self, subject: Subject, assignment_id: int) -> GetDraftResponse:
        """Retrieves the details for an assignment draft."""
        # Get the assignment
        assignment: AssignmentEntity | None = (
            self._admin_db.query(AssignmentEntity)
            .where(
                AssignmentEntity.id == assignment_id,
                AssignmentEntity.state == AssignmentState.DRAFT,
            )
            .one_or_none()
        )

        if not assignment:
            raise ResourceNotFoundException(
                f"Draft assignment with ID {assignment_id} not found."
            )

        # Check for permission
        self._courses_svc.verify_subject_has_permissions_for_course(
            subject, assignment.course_id, CourseMembershipRole.ADMIN
        )

        # Return the assignment details
        return GetDraftResponse(
            assignment_id=assignment.id,
            name=assignment.name,
            is_group=assignment.is_group_assignment,
        )

    def get_configuration_sql(
        self, subject: Subject, assignment_id: int
    ) -> GetConfigurationSQLResponse:
        """Gets the configuration SQL for an assignment draft."""
        # Get the assignment
        assignment: AssignmentEntity | None = (
            self._admin_db.query(AssignmentEntity)
            .where(
                AssignmentEntity.id == assignment_id,
                AssignmentEntity.state == AssignmentState.DRAFT,
            )
            .one_or_none()
        )

        if not assignment:
            raise ResourceNotFoundException(
                f"Draft assignment with ID {assignment_id} not found."
            )

        # Check for permission
        self._courses_svc.verify_subject_has_permissions_for_course(
            subject, assignment.course_id, CourseMembershipRole.ADMIN
        )

        # Return the configuration SQL and database URL if available
        db_url = (
            self._content_db_cluster_svc.db_url_for_provisioned_db(
                assignment.test_db_name,
                assignment.test_db_view_role_name,
                self._content_db_cluster_svc.decrypt_role_password(
                    assignment.encrypted_test_db_view_role_password, assignment.id
                ),
            )
            if assignment.test_db_name is not None
            and assignment.test_db_view_role_name is not None
            and assignment.encrypted_test_db_view_role_password is not None
            else None
        )
        return GetConfigurationSQLResponse(
            sql=assignment.project_configuration_sql,
            sql_draft=assignment.draft_project_configuration_sql,
            sql_draft_success=assignment.draft_project_configuration_sql_succeeded,
            sql_draft_error=assignment.draft_project_configuration_sql_error,
            db_url=db_url,
        )

    def create_draft(
        self, subject: Subject, request: CreateDraftRequest
    ) -> CreateDraftResponse:
        """Creates a draft assignment for a course."""
        # Check for admin permissions
        self._courses_svc.verify_subject_has_permissions_for_course(
            subject, request.course_id, CourseMembershipRole.ADMIN
        )

        # Create the draft assignment
        assignment = AssignmentEntity(
            name=request.name,
            course_id=request.course_id,
            is_group_assignment=request.is_group,
        )

        # Commit the assignment to get the ID
        self._admin_db.add(assignment)
        self._admin_db.commit()

        # Create a test database for the assignment
        test_db_name = ContentDatabaseNamingConventions.name_for_assignment_test_db(
            assignment.id
        )

        # Wrap everything in a try / except block so that the creation of the draft
        # assignment can be reverted if operations in the content database fails
        try:

            admin_role_name, admin_role_password = (
                self._content_db_cluster_svc.provision_database(test_db_name)
            )
            # Create a read-only role for the test database
            # Note: The read-only role should be provisioned by the admin role so that items that
            # are created by the admin role are viewable by the read-only role.
            view_role_name = ContentDatabaseNamingConventions.name_for_assignment_test_db_readonly_role(
                assignment.id
            )
            view_role_password = crypto.generate_secure_password()
            self._content_db_cluster_svc.provision_role_for_database(
                test_db_name,
                view_role_name,
                view_role_password,
                readonly=True,
                issuer_role_name=admin_role_name,
                issuer_role_password=admin_role_password,
            )

            # Encrypt the admin and view role passwords
            encrypted_admin_role_password = (
                self._content_db_cluster_svc.encrypt_role_password(
                    admin_role_password, assignment.id
                )
            )
            encrypted_view_role_password = (
                self._content_db_cluster_svc.encrypt_role_password(
                    view_role_password, assignment.id
                )
            )

            # Once all of the operations succeed, update the assignment
            assignment.test_db_name = test_db_name
            assignment.test_db_admin_role_name = admin_role_name
            assignment.encrypted_test_db_admin_role_password = (
                encrypted_admin_role_password
            )
            assignment.test_db_view_role_name = view_role_name
            assignment.encrypted_test_db_view_role_password = (
                encrypted_view_role_password
            )
            # Update the assignment in the database
            self._admin_db.commit()

            return CreateDraftResponse(assignment_id=assignment.id)

        except ContentDatabaseTransactionException as e:
            # If an error occurs, we need to roll back the assignment creation including the
            # database provision, if it succeded.
            self._content_db_cluster_svc.delete_database(test_db_name)
            # Remove the draft assignment from the database
            ...
            raise e

    def rename(self, subject: Subject, request: RenameRequest):
        """Renames an assignment"""
        # Check for admin permissions
        assignment = self._get_assignment_and_verify_permissions(
            subject, request.assignment_id, CourseMembershipRole.ADMIN
        )

        # Validate the input name
        if len(request.name) < 1:
            raise InputValidationException(
                "Assignment name must be at least 1 character long."
            )

        # Update the assignment name
        assignment.name = request.name
        self._admin_db.commit()

    def test_configuration_sql(
        self, subject: Subject, assignment_id: int, request: TestConfigurationSQLRequest
    ) -> TestConfigurationSQLResponse:
        """Tests the configuration SQL for an assignment."""
        # Check for admin permissions
        assignment = self._get_assignment_and_verify_permissions(
            subject, assignment_id, CourseMembershipRole.ADMIN
        )

        # Ensure the assignment has a test database and roles configured
        if (
            assignment.test_db_name is None
            or assignment.test_db_admin_role_name is None
            or assignment.encrypted_test_db_admin_role_password is None
            or assignment.test_db_view_role_name is None
            or assignment.encrypted_test_db_view_role_password is None
        ):
            raise ResourceNotFoundException(
                f"Assignment with ID {assignment_id} does not have a valid configuration."
            )

        # Validate the SQL input
        if not request.sql.strip():
            raise InputValidationException("SQL cannot be empty.")
        ...  # TODO: any other important validation here

        # Get the roles for the assignment
        assignment_owner_role = assignment.test_db_admin_role_name
        assignment_owner_password = self._content_db_cluster_svc.decrypt_role_password(
            assignment.encrypted_test_db_admin_role_password, assignment.id
        )
        assignment_view_role = assignment.test_db_view_role_name
        assignment_view_password = self._content_db_cluster_svc.decrypt_role_password(
            assignment.encrypted_test_db_view_role_password, assignment.id
        )

        # Reset the database
        self._content_db_cluster_svc.reset_database(
            assignment.test_db_name, assignment_owner_role, assignment_owner_password
        )

        # Add the new draft SQL running into the database object
        assignment.draft_project_configuration_sql = request.sql
        assignment.draft_project_configuration_sql_succeeded = None
        assignment.draft_project_configuration_sql_error = None
        self._admin_db.commit()

        # Try to execute the SQL against the test database
        try:
            self._content_db_cluster_svc.run_sql_on_database(
                assignment.test_db_name,
                assignment_owner_role,
                assignment_owner_password,
                request.sql,
            )
            # If successful, update the draft SQL success status
            assignment.draft_project_configuration_sql_succeeded = True
            assignment.draft_project_configuration_sql_error = None

            # Return result
            return TestConfigurationSQLResponse(
                success=True,
                db_url=self._content_db_cluster_svc.db_url_for_provisioned_db(
                    assignment.test_db_name,
                    assignment_view_role,
                    assignment_view_password,
                ),
            )
        except ContentDatabaseTransactionException as e:
            # If an error occurs, update the draft SQL error status
            assignment.draft_project_configuration_sql_succeeded = False
            assignment.draft_project_configuration_sql_error = str(e)

            # Reset the database back to the working SQL if any
            if assignment.project_configuration_sql is not None:
                self._content_db_cluster_svc.reset_database(
                    assignment.test_db_name,
                    assignment_owner_role,
                    assignment_owner_password,
                )
                self._content_db_cluster_svc.run_sql_on_database(
                    assignment.test_db_name,
                    assignment_owner_role,
                    assignment_owner_password,
                    assignment.project_configuration_sql,
                )

            # Return the error response
            return TestConfigurationSQLResponse(
                success=False,
                error_message=str(e),
                db_url=None,
            )
        finally:
            self._admin_db.commit()

    def save_configuration_sql(self, subject: Subject, assignment_id: int):
        """Save configuration SQL for an assignment. Can only be done after testing the SQL."""
        # Check for admin permissions
        assignment = self._get_assignment_and_verify_permissions(
            subject, assignment_id, CourseMembershipRole.ADMIN
        )

        # Saving can only occur if draft SQL is present and it has been tested
        if not (
            assignment.draft_project_configuration_sql is not None
            and assignment.draft_project_configuration_sql_succeeded is True
            and assignment.draft_project_configuration_sql_error is None
        ):
            raise InputValidationException(
                "Draft SQL must be tested successfully before saving."
            )

        # Save the configuration SQL
        assignment.project_configuration_sql = (
            assignment.draft_project_configuration_sql
        )
        assignment.draft_project_configuration_sql = None
        assignment.draft_project_configuration_sql_succeeded = None
        assignment.draft_project_configuration_sql_error = None
        self._admin_db.commit()

    def remove_configuration_sql(self, subject: Subject, assignment_id: int):
        """Removes the configuration SQL for an assignment."""
        # Check for admin permissions
        assignment = self._get_assignment_and_verify_permissions(
            subject, assignment_id, CourseMembershipRole.ADMIN
        )

        if (
            not assignment.test_db_name
            or not assignment.test_db_admin_role_name
            or not assignment.encrypted_test_db_admin_role_password
        ):
            raise ResourceNotFoundException(
                f"Assignment with ID {assignment_id} does not have a valid configuration."
            )

        # Remove the configuration SQL
        assignment_owner_password = self._content_db_cluster_svc.decrypt_role_password(
            assignment.encrypted_test_db_admin_role_password, assignment.id
        )
        self._content_db_cluster_svc.reset_database(
            assignment.test_db_name,
            assignment.test_db_admin_role_name,
            assignment_owner_password,
        )

        assignment.project_configuration_sql = None
        assignment.draft_project_configuration_sql = None
        assignment.draft_project_configuration_sql_succeeded = None
        assignment.draft_project_configuration_sql_error = None
        self._admin_db.commit()

    def reset_configuration_sql(self, subject: Subject, assignment_id: int):
        """Resets the configuration SQL to the previous saved and tested SQL."""
        # Check for admin permissions
        assignment = self._get_assignment_and_verify_permissions(
            subject, assignment_id, CourseMembershipRole.ADMIN
        )

        if (
            not assignment.test_db_name
            or not assignment.test_db_admin_role_name
            or not assignment.encrypted_test_db_admin_role_password
        ):
            raise ResourceNotFoundException(
                f"Assignment with ID {assignment_id} does not have a valid configuration."
            )

        if not assignment.project_configuration_sql:
            raise InputValidationException("No previous configuration SQL to reset to.")

        # Reset the database
        assignment_owner_password = self._content_db_cluster_svc.decrypt_role_password(
            assignment.encrypted_test_db_admin_role_password, assignment.id
        )
        self._content_db_cluster_svc.reset_database(
            assignment.test_db_name,
            assignment.test_db_admin_role_name,
            assignment_owner_password,
        )

        # Run the saved configuration SQL on the database
        self._content_db_cluster_svc.run_sql_on_database(
            assignment.test_db_name,
            assignment.test_db_admin_role_name,
            assignment_owner_password,
            assignment.project_configuration_sql,
        )

        # Remove the draft SQL and its related fields
        assignment.draft_project_configuration_sql = None
        assignment.draft_project_configuration_sql_succeeded = None
        assignment.draft_project_configuration_sql_error = None
        self._admin_db.commit()

    def get_groups(self, subject: Subject, assignment_id: int) -> GetGroupsResponse:
        """Gets the groups for an assignment."""
        # Check for staff permissions"""
        assignment = self._get_assignment_and_verify_permissions(
            subject, assignment_id, CourseMembershipRole.STAFF
        )

        if not assignment.is_group_assignment:
            raise InputValidationException(
                "Cannot get groups for non-group assignments."
            )

        # Get all of the groups and students in each group
        groups_query = (
            select(ProjectGroupEntity)
            .outerjoin(
                ProjectGroupMemberEntity
            )  # Outer join to include groups with no members
            .where(ProjectGroupEntity.assignment_id == assignment_id)
            .order_by(ProjectGroupEntity.name)
            .options(
                joinedload(ProjectGroupEntity.members).joinedload(
                    ProjectGroupMemberEntity.user
                )
            )
        )
        groups = self._admin_db.scalars(groups_query).unique().all()

        # Convert the groups to the response model
        groups_models = [
            GetGroupsResponse_Group(
                group_id=group.id,
                group_name=group.name,
                members=[
                    GetGroupsResponse_User(
                        user_id=member.user.id,
                        user_name=member.user.first_name + " " + member.user.last_name,
                    )
                    for member in group.members
                ],
            )
            for group in groups
        ]

        # Get all of the students in the class that are not in a group
        students_in_groups_ids = set(
            [member.user_id for group in groups for member in group.members]
        )
        students_query = (
            select(UserEntity)
            .join(CourseMemberEntity)
            .where(
                CourseMemberEntity.course_id == assignment.course_id,
                CourseMemberEntity.role == CourseMembershipRole.STUDENT,
                CourseMemberEntity.user_id.not_in(students_in_groups_ids),
            )
        )
        students = self._admin_db.scalars(students_query).all()
        student_models = [
            GetGroupsResponse_User(
                user_id=student.id,
                user_name=student.first_name + " " + student.last_name,
            )
            for student in students
        ]

        return GetGroupsResponse(
            groups=groups_models, unassigned_students=student_models
        )

    def create_group(
        self, subject: Subject, assignment_id: int, request: CreateGroupRequest
    ) -> CreateGroupResponse:
        """Creates a new group for a group assignment."""
        # Check for admin permissions
        assignment = self._get_assignment_and_verify_permissions(
            subject, assignment_id, CourseMembershipRole.ADMIN
        )

        # Ensure the assignment is a group assignment
        if not assignment.is_group_assignment:
            raise InputValidationException(
                "Cannot create groups for non-group assignments."
            )

        # Validate the group name
        if len(request.group_name) < 1:
            raise InputValidationException(
                "Group name must be at least 1 character long."
            )

        # Create the group
        group = ProjectGroupEntity(
            name=request.group_name,
            assignment_id=assignment.id,
        )
        self._admin_db.add(group)
        self._admin_db.commit()

        return CreateGroupResponse(
            group_id=group.id,
            group_name=group.name,
        )

    def rename_group(self, subject: Subject, request: RenameGroupRequest):
        """Renames a group in a group assignment."""
        # Find the group by ID
        group: ProjectGroupEntity | None = self._admin_db.query(ProjectGroupEntity).get(
            request.group_id
        )
        if not group:
            raise ResourceNotFoundException(
                f"Group with ID {request.group_id} not found."
            )

        # Check for admin permissions
        self._get_assignment_and_verify_permissions(
            subject, group.assignment_id, CourseMembershipRole.ADMIN
        )

        # Validate the input name
        if len(request.name) < 1:
            raise InputValidationException(
                "Group name must be at least 1 character long."
            )

        # Update the group name
        group.name = request.name
        self._admin_db.commit()

    def add_group_member(self, subject: Subject, request: AddGroupMemberRequest):
        """Adds a member to a group in a group assignment."""
        # Find the group by ID
        group: ProjectGroupEntity | None = self._admin_db.query(ProjectGroupEntity).get(
            request.group_id
        )
        if not group:
            raise ResourceNotFoundException(
                f"Group with ID {request.group_id} not found."
            )

        # Check for admin permissions
        self._get_assignment_and_verify_permissions(
            subject, group.assignment_id, CourseMembershipRole.ADMIN
        )

        # Add the member to the group
        member = ProjectGroupMemberEntity(group_id=group.id, user_id=request.user_id)
        self._admin_db.add(member)
        self._admin_db.commit()

    def remove_group_member(self, subject: Subject, request: RemoveGroupMemberRequest):
        """Removes a member from a group in a group assignment."""
        # Find the group by ID
        group: ProjectGroupEntity | None = self._admin_db.query(ProjectGroupEntity).get(
            request.group_id
        )
        if not group:
            raise ResourceNotFoundException(
                f"Group with ID {request.group_id} not found."
            )

        # Check for admin permissions
        self._get_assignment_and_verify_permissions(
            subject, group.assignment_id, CourseMembershipRole.ADMIN
        )

        # Remove the member from the group
        member: ProjectGroupMemberEntity | None = (
            self._admin_db.query(ProjectGroupMemberEntity)
            .filter_by(group_id=group.id, user_id=request.user_id)
            .first()
        )
        if not member:
            raise ResourceNotFoundException(
                f"Member with user ID {request.user_id} not found in group {group.id}."
            )
        self._admin_db.delete(member)
        self._admin_db.commit()

    def delete_group(self, subject: Subject, request: DeleteGroupRequest):
        """Deletes a group from a group assignment."""
        # Find the group by ID
        group: ProjectGroupEntity | None = self._admin_db.query(ProjectGroupEntity).get(
            request.group_id
        )
        if not group:
            raise ResourceNotFoundException(
                f"Group with ID {request.group_id} not found."
            )

        # Check for admin permissions
        self._get_assignment_and_verify_permissions(
            subject, group.assignment_id, CourseMembershipRole.ADMIN
        )

        # Delete the group and its members
        self._admin_db.delete(group)
        self._admin_db.commit()

    def publish(self, subject: Subject, assignment_id: int):
        """
        Publishes an assignment, creating all projects for students.

        Note: This is a potentially very expensive operation, since publishing an
        assignment might kick off the creation of hundreds of databases. So,
        this is a celery background task that can be run asynchronously, and a
        separate polling endpoint should be used to check the status of the task.

        The Celery task is defined in the `/tasks` directory.
        """
        # Check for admin permissions
        assignment = self._get_assignment_and_verify_permissions(
            subject, assignment_id, CourseMembershipRole.ADMIN
        )

        # Ensure that the assignment is a draft
        if assignment.state != AssignmentState.DRAFT:
            raise InputValidationException(
                "Assignment is already published and cannot be republished."
            )

        if assignment.is_group_assignment:
            # If the assignment is a group assignment, create a project for each
            # group.
            groups = (
                self._admin_db.query(ProjectGroupEntity)
                .filter_by(assignment_id=assignment.id)
                .all()
            )
            for group in groups:
                # Create a project for each group
                self._create_project(assignment_id=assignment.id, group_id=group.id)
        else:
            # If the assignment is an individual assignment, create a project for each student.
            students = (
                self._admin_db.query(CourseMemberEntity)
                .where(
                    CourseMemberEntity.course_id == assignment.course_id,
                    CourseMemberEntity.role == CourseMembershipRole.STUDENT,
                )
                .all()
            )
            for student in students:
                # Create a project for each student
                self._create_project(
                    assignment_id=assignment.id, user_id=student.user_id
                )

        # Update the assignment details
        assignment.state = AssignmentState.PUBLISHED
        self._admin_db.commit()

    def delete(self, subject: Subject, assignment_id: int):
        """
        Deletes the database and all roles associated with them.

        This could also potentially be a very expensive operation, so like
        publish, delete will be run as a Celery background task. See the
        `/tasks` directory for the Celery task definition.
        """
        # Check for admin permissions
        assignment = self._get_assignment_and_verify_permissions(
            subject, assignment_id, CourseMembershipRole.ADMIN
        )
        # Delete all projects associated with the assignment
        projects = (
            self._admin_db.query(ProjectEntity)
            .filter_by(assignment_id=assignment.id)
            .all()
        )
        for project in projects:
            # Delete the database and roles associated with the project
            self._content_db_cluster_svc.delete_database(project.db_name)
            self._content_db_cluster_svc.delete_role_for_database(
                project.student_role_name
            )
            self._content_db_cluster_svc.delete_role_for_database(
                project.admin_role_name
            )
            self._admin_db.delete(project)

        # Delete the assignment's test db
        if assignment.test_db_name:
            self._content_db_cluster_svc.delete_database(assignment.test_db_name)
        if assignment.test_db_admin_role_name and assignment.test_db_view_role_name:
            self._content_db_cluster_svc.delete_role_for_database(
                assignment.test_db_admin_role_name
            )
            self._content_db_cluster_svc.delete_role_for_database(
                assignment.test_db_view_role_name
            )
        self._admin_db.delete(assignment)
        self._admin_db.commit()

    def unpublish(self, subject: Subject, assignment_id: int):
        """
        Unpublishes an assignment, which means locking the student roles from the database
        to prevent students from accessing their projects, but the database and admin roles
        are still preserved (for grading)
        """
        # Check for admin permissions
        assignment = self._get_assignment_and_verify_permissions(
            subject, assignment_id, CourseMembershipRole.ADMIN
        )

        # Ensure that the assignment is published
        if assignment.state != AssignmentState.PUBLISHED:
            raise InputValidationException(
                "Assignment is not published and cannot be unpublished."
            )

        # Remove student roles from all projects
        projects = (
            self._admin_db.query(ProjectEntity)
            .filter_by(assignment_id=assignment.id)
            .all()
        )
        for project in projects:
            # Delete the student role for the project
            self._content_db_cluster_svc.lock_role_for_database(
                project.student_role_name
            )

        # Update the assignment state
        assignment.state = AssignmentState.UNPUBLISHED
        self._admin_db.commit()

    def republish(self, subject: Subject, assignment_id: int):
        """Republishes an unpublished assignment"""
        # Check for admin permissions
        assignment = self._get_assignment_and_verify_permissions(
            subject, assignment_id, CourseMembershipRole.ADMIN
        )

        # Ensure that the assignment is published
        if assignment.state != AssignmentState.UNPUBLISHED:
            raise InputValidationException(
                "Only unpublished assignments can be republished."
            )

        # Add the student roles back to the database
        projects = (
            self._admin_db.query(ProjectEntity)
            .filter_by(assignment_id=assignment.id)
            .all()
        )
        for project in projects:
            self._content_db_cluster_svc.unlock_role_for_database(
                project.student_role_name
            )

        # Update the assignment state
        assignment.state = AssignmentState.PUBLISHED
        self._admin_db.commit()

    def _get_assignment_and_verify_permissions(
        self, subject: Subject, assignment_id: int, min_role: CourseMembershipRole
    ) -> AssignmentEntity:
        """Fetches an assignment and verifies the user's permissions."""
        assignment: AssignmentEntity | None = self._admin_db.query(
            AssignmentEntity
        ).get(assignment_id)
        if not assignment:
            raise ResourceNotFoundException(
                f"Assignment with ID {assignment_id} not found."
            )
        self._courses_svc.verify_subject_has_permissions_for_course(
            subject, assignment.course_id, min_role
        )
        return assignment

    def _create_project(
        self,
        assignment_id: int,
        group_id: int | None = None,
        user_id: int | None = None,
    ) -> ProjectEntity:
        """Creates a project for an assignment."""
        # Create a new project
        project = ProjectEntity(
            assignment_id=assignment_id,
            group_id=group_id,
            user_id=user_id,
            db_name="",  # Will be set later after database creation
            admin_role_name="",  # Will be set later after database creation
            encrypted_admin_role_password="",  # Will be set later after database creation
            student_role_name="",  # Will be set later after database creation
            encrypted_student_role_password="",  # Will be set later after database creation
            auth_encrypted_private_key="",  # Will be set later after key generation
            auth_public_key="",  # Will be set later after key generation
        )
        self._admin_db.add(project)
        self._admin_db.flush()  # Flush to get the project ID before proceeding

        # Handle creating the authentication private key and public key
        private_key, public_key = crypto.generate_serialied_rsa_keypair()
        encryption_key = crypto.hkdf_derive_encryption_key(
            env.AUTH_MASTER_SECRET, project.id
        )
        encrypted_private_key = crypto.encrypt(private_key, encryption_key)

        # Update the project with the encrypted private key and public key
        project.auth_encrypted_private_key = encrypted_private_key
        project.auth_public_key = public_key

        # Create the database for the project
        db_name = ContentDatabaseNamingConventions.name_for_assignment_db(
            assignment_id=assignment_id, project_id=project.id
        )
        project.db_name = db_name

        # Wrap everything in a try / except block so that the creation of the draft
        # assignment can be reverted if operations in the content database fails
        try:
            admin_role_name, admin_role_password = (
                self._content_db_cluster_svc.provision_database(db_name)
            )
            encrypted_admin_role_password = (
                self._content_db_cluster_svc.encrypt_role_password(
                    admin_role_password, assignment_id
                )
            )

            # Add a student user to the database
            student_role_name = (
                ContentDatabaseNamingConventions.name_for_assignment_db_student_role(
                    assignment_id=assignment_id, project_id=project.id
                )
            )
            student_role_password = crypto.generate_secure_password()
            encrypted_student_role_password = (
                self._content_db_cluster_svc.encrypt_role_password(
                    student_role_password, assignment_id
                )
            )
            self._content_db_cluster_svc.provision_role_for_database(
                db_name, student_role_name, student_role_password
            )

            # Set the credentials for the project
            project.admin_role_name = admin_role_name
            project.encrypted_admin_role_password = encrypted_admin_role_password
            project.student_role_name = student_role_name
            project.encrypted_student_role_password = encrypted_student_role_password

            self._admin_db.commit()

            return project

        except ContentDatabaseTransactionException as e:
            # If an error occurs, we need to roll back the assignment creation including the
            # database provision, if it succeded.
            self._content_db_cluster_svc.delete_database(db_name)
            # Remove the draft project from the database
            ...
            raise e
