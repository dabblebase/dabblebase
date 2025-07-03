"""Service used to interface with assignments"""

from fastapi import Depends
from ..entities import CourseMembershipRole, AssignmentEntity
from ..services.courses import CourseService
from ..services.content_database import (
    ContentDatabaseService,
    ContentDatabaseNamingConventions,
)
from ..services.content_db_cluster import ContentDbClusterService
from ..services.project import auth_crypto as crypto
from ..models.auth import Subject
from ..models.assignment import CreateDraftRequest
from ..database import admin_db_session
from sqlalchemy.orm import Session
from .exceptions import ContentDatabaseTransactionException


class AssignmentService:

    _admin_db: Session

    def __init__(
        self,
        admin_db: Session = Depends(admin_db_session),
        courses_svc: CourseService = Depends(),
        content_db_svc: ContentDatabaseService = Depends(),
        content_db_cluster_svc: ContentDbClusterService = Depends(),
    ):
        self._admin_db = admin_db
        self._courses_svc = courses_svc
        self._content_db_svc = content_db_svc
        self._content_db_cluster_svc = content_db_cluster_svc

    def create_draft(self, subject: Subject, request: CreateDraftRequest):
        ...
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
            test_db_name = (
                ContentDatabaseNamingConventions.name_for_assignment_test_schema(
                    assignment.id
                )
            )
            self._content_db_cluster_svc._provision_database(test_db_name)
            with self._content_db_cluster_svc._content_db.begin():
                # Create an admin role for the test database
                admin_role_name = ContentDatabaseNamingConventions.name_for_assignment_test_schema_admin_role(
                    assignment.id
                )
                admin_role_password = crypto.generate_secure_password()
                encrypted_admin_role_password = (
                    self._content_db_svc.encrypt_role_password(
                        admin_role_password, assignment.id
                    )
                )
                self._content_db_cluster_svc._provision_role_for_database(
                    test_db_name,
                    admin_role_name,
                    admin_role_password,
                )

            # with self._content_db_svc._content_db.begin():
            #     # Create a test project schema for the assignment
            #     test_schema_name = (
            #         ContentDatabaseNamingConventions.name_for_assignment_test_schema(
            #             assignment.id
            #         )
            #     )
            #     self._content_db_svc.create_schema(test_schema_name)

            #     # Create an admin role for the test schema
            #     admin_role_name = ContentDatabaseNamingConventions.name_for_assignment_test_schema_admin_role(
            #         assignment.id
            #     )
            #     admin_role_password = crypto.generate_secure_password()
            #     encrypted_admin_role_password = (
            #         self._content_db_svc.encrypt_role_password(
            #             admin_role_password, assignment.id
            #         )
            #     )
            #     self._content_db_svc.create_role_scoped_to_schema(
            #         admin_role_name, admin_role_password, test_schema_name
            #     )

            #     # Create a view (readonly) role for the test schema
            #     view_role_name = ContentDatabaseNamingConventions.name_for_assignment_test_schema_readonly_role(
            #         assignment.id
            #     )
            #     view_role_password = crypto.generate_secure_password()
            #     encrypted_view_role_password = (
            #         self._content_db_svc.encrypt_role_password(
            #             view_role_password, assignment.id
            #         )
            #     )
            #     self._content_db_svc.create_role_scoped_to_schema(
            #         view_role_name, view_role_password, test_schema_name, readonly=True
            #     )

            # Once all of the operations succeed, update the assignment
            assignment.test_schema_name = test_db_name
            assignment.test_schema_admin_role_name = admin_role_name
            assignment.encrypted_test_schema_admin_role_password = (
                encrypted_admin_role_password
            )
            # assignment.test_schema_view_role_name = view_role_name
            # assignment.encrypted_test_schema_view_role_password = (
            #     encrypted_view_role_password
            # )

            # Update the assignment in the database
            self._admin_db.commit()

            return assignment

        except ContentDatabaseTransactionException as e:
            # Remove the draft assignment from the database
            ...
            raise e
