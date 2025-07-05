"""Service used to interface with assignments"""

from fastapi import Depends
from ..entities import CourseMembershipRole, AssignmentEntity
from ..services.courses import CourseService
from ..services.content_db_cluster import (
    ContentDbClusterService,
    ContentDatabaseNamingConventions,
)
from ..services.project import auth_crypto as crypto
from ..models.auth import Subject
from ..models.assignment import CreateDraftRequest, CreateDraftResponse
from ..database import admin_db_session
from sqlalchemy.orm import Session
from .exceptions import ContentDatabaseTransactionException


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

        # Wrap everything in a try / except block so that the creation of the draft
        # assignment can be reverted if operations in the content database fails
        try:
            # Create a test database for the assignment
            test_db_name = ContentDatabaseNamingConventions.name_for_assignment_test_db(
                assignment.id
            )
            admin_role_name, admin_role_password = (
                self._content_db_cluster_svc.provision_database(test_db_name)
            )
            # Create a read-only role for the test database
            view_role_name = ContentDatabaseNamingConventions.name_for_assignment_test_db_readonly_role(
                assignment.id
            )
            view_role_password = crypto.generate_secure_password()
            self._content_db_cluster_svc.provision_role_for_database(
                test_db_name, view_role_name, view_role_password, readonly=True
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

            return CreateDraftResponse(id=assignment.id)

        except ContentDatabaseTransactionException as e:
            # If an error occurs, we need to roll back the assignment creation including the
            # database provision, if it succeded.
            self._content_db_cluster_svc.delete_database(test_db_name)
            # Remove the draft assignment from the database
            ...
            raise e
