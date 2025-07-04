"""Service used to interface with courses"""

from .base import BaseService
from ..entities import (
    CourseMembershipRole,
    CourseEntity,
    ProjectEntity,
    AssignmentEntity,
)
from fastapi import Depends
from ..models.auth import Subject
from ..models.course import (
    CreateCourseRequest,
    CreateCourseResponse,
    UpdateCourseRequest,
    AddUserToCourseRequest,
    JoinCourseRequest,
    JoinCourseResponse,
    ChangeUserRoleInCourseRequest,
    RemoveUserFromCourseRequest,
)
from ..entities import CourseMemberEntity
from .exceptions import (
    ResourceNotFoundException,
    UserPermissionException,
    ResourceAlreadyExistsException,
    InputValidationException,
)
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
import string
import random
from ..services.content_db_cluster import ContentDbClusterService
from ..database import admin_db_session


class CourseService:

    _admin_db: Session

    def __init__(
        self,
        admin_db: Session = Depends(admin_db_session),
        content_db_cluster_svc: ContentDbClusterService = Depends(),
    ):
        self._admin_db = admin_db
        self._content_db_cluster_svc = content_db_cluster_svc

    def create_course(
        self, subject: Subject, request: CreateCourseRequest
    ) -> CreateCourseResponse:
        """Creates a course based on the required data"""
        # TODO: Validate on permission for course creation
        ...
        # Validate that the course code does not have spaces or special characters
        if not request.code.isalnum():
            raise InputValidationException(
                "Course code must be alphanumeric and cannot contain spaces or special characters."
            )

        # Validate that the inputted date range is valid
        if request.start_date >= request.end_date:
            raise InputValidationException(
                "The start date must be before the end date."
            )

        # Generate a random 6-digit invite code for a course
        invite_code = self._generate_invite_code()
        invite_code_query = select(CourseEntity).where(
            CourseEntity.invite_code == invite_code
        )
        # Check if the invite code already exists, and if it does, generate
        # a new one
        existing_course = self._admin_db.scalars(invite_code_query).one_or_none()
        while existing_course:
            invite_code = self._generate_invite_code()
            existing_course = self._admin_db.scalars(invite_code_query).one_or_none()

        # Create the course entity with the provided data
        course = CourseEntity(
            code=request.code,
            name=request.name,
            description=request.description,
            start_date=request.start_date,
            end_date=request.end_date,
            invite_code=invite_code,
        )

        # Add the course to the database
        self._admin_db.add(course)
        self._admin_db.commit()

        # Add the creator as the owner member of the course
        course_member = CourseMemberEntity(
            user_id=subject.id,
            course_id=course.id,
            role=CourseMembershipRole.OWNER,
        )
        self._admin_db.add(course_member)
        self._admin_db.commit()

        # Return the created course
        return CreateCourseResponse(
            id=course.id,
            code=course.code,
            name=course.name,
            invite_code=course.invite_code,
        )

    def update_course(self, subject: Subject, request: UpdateCourseRequest):
        """Updates a course based on the provided data"""
        # Check permissions
        self.verify_subject_has_permissions_for_course(
            subject, request.id, CourseMembershipRole.ADMIN
        )

        # Validate that the course code does not have spaces or special characters
        if not request.code.isalnum():
            raise InputValidationException(
                "Course code must be alphanumeric and cannot contain spaces or special characters."
            )

        # Validate that the inputted date range is valid
        if request.start_date >= request.end_date:
            raise InputValidationException(
                "The start date must be before the end date."
            )

        # Query the course from the database
        query = select(CourseEntity).where(CourseEntity.id == request.id)
        course = self._admin_db.scalars(query).one_or_none()
        if not course:
            raise ResourceNotFoundException(f"Course with ID {request.id} not found.")

        # Update the course attributes
        course.code = request.code
        course.name = request.name
        course.description = request.description
        course.start_date = request.start_date
        course.end_date = request.end_date
        self._admin_db.commit()

    def delete_course(self, subject: Subject, course_id: int):
        """Deletes a course and all associated databases"""
        # Check permissions
        self.verify_subject_has_permissions_for_course(
            subject, course_id, CourseMembershipRole.OWNER
        )

        # Query all assignments (and projects) associated with the course so that all related
        # databases can be deleted after the course is removed
        assignments_query = (
            select(AssignmentEntity)
            .where(AssignmentEntity.course_id == course_id)
            .options(joinedload(AssignmentEntity.projects))
        )
        assignments = self._admin_db.scalars(assignments_query).all()

        # Query and delete the course from the database
        query = select(CourseEntity).where(CourseEntity.id == course_id)
        course = self._admin_db.scalars(query).one_or_none()
        if not course:
            raise ResourceNotFoundException(f"Course with ID {course_id} not found.")
        self._admin_db.delete(course)
        self._admin_db.commit()

        # In order to delete the course, all databases for the course must be deleted
        for assignment in assignments:
            # Delete the test database
            if assignment.test_db_name is not None:
                self._content_db_cluster_svc.delete_database(assignment.test_db_name)
            # Delete the project databases for the assignment
            for project in assignment.projects:
                if project.db_name is not None:
                    self._content_db_cluster_svc.delete_database(project.db_name)

    def add_user_to_course(self, subject: Subject, request: AddUserToCourseRequest):
        """Adds a user to a course - requires admin permissions"""
        # Check permissions
        self.verify_subject_has_permissions_for_course(
            subject, request.course_id, CourseMembershipRole.ADMIN
        )

        # Check if the user is already a member of the course
        query = select(CourseMemberEntity).where(
            CourseMemberEntity.user_id == request.user_id,
            CourseMemberEntity.course_id == request.course_id,
        )
        existing_member = self._admin_db.scalars(query).one_or_none()
        if existing_member:
            raise ResourceAlreadyExistsException(
                f"User {request.user_id} is already a member of course {request.course_id}."
            )

        # Add the user to the course
        course_member = CourseMemberEntity(
            user_id=request.user_id,
            course_id=request.course_id,
            role=CourseMembershipRole.STUDENT,
        )
        self._admin_db.add(course_member)
        self._admin_db.commit()

    def join_course(
        self, subject: Subject, request: JoinCourseRequest
    ) -> JoinCourseResponse:
        """Allows a user to join a course"""
        # Check if there is a course with the invite code
        query = select(CourseEntity).where(
            CourseEntity.invite_code == request.invite_code
        )
        course = self._admin_db.scalars(query).one_or_none()
        if not course:
            raise ResourceNotFoundException(
                f"No course found with invite code {request.invite_code}."
            )

        # Check if the user is already a member of the course
        query = select(CourseMemberEntity).where(
            CourseMemberEntity.user_id == subject.id,
            CourseMemberEntity.course_id == course.id,
        )
        existing_member = self._admin_db.scalars(query).one_or_none()
        if existing_member:
            raise ResourceAlreadyExistsException(
                f"You are already a member of course {course.id}."
            )

        # Add the user as a student member of the course
        course_member = CourseMemberEntity(
            user_id=subject.id,
            course_id=course.id,
            role=CourseMembershipRole.STUDENT,
        )
        self._admin_db.add(course_member)
        self._admin_db.commit()

        # Return information about the course that the user joined
        return JoinCourseResponse(
            course_id=course.id,
            course_code=course.code,
            course_name=course.name,
        )

    def change_user_role_in_course(
        self, subject: Subject, request: ChangeUserRoleInCourseRequest
    ):
        """Changes the role of a user in a course"""
        # Check permissions
        subject_role = self.verify_subject_has_permissions_for_course(
            subject, request.course_id, CourseMembershipRole.ADMIN
        )

        # Query the course member from the database
        query = select(CourseMemberEntity).where(
            CourseMemberEntity.user_id == request.user_id,
            CourseMemberEntity.course_id == request.course_id,
        )
        member = self._admin_db.scalars(query).one_or_none()
        if not member:
            raise ResourceNotFoundException(
                f"User {request.user_id} is not a member of course {request.course_id}."
            )

        # Handle change user role restrictions
        if (
            request.role == CourseMembershipRole.OWNER
            or member.role == CourseMembershipRole.OWNER
        ):
            raise UserPermissionException("Cannot change the role of the course owner.")
        if (
            request.role == CourseMembershipRole.ADMIN
            or member.role == CourseMembershipRole.ADMIN
        ) and subject_role != CourseMembershipRole.OWNER:
            raise UserPermissionException(
                "Only the course owner can assign or remove admin roles."
            )

        # Update the member's role
        member.role = request.role
        self._admin_db.commit()

    def remove_user_from_course(
        self, subject: Subject, request: RemoveUserFromCourseRequest
    ):
        """Removes a user from a course"""
        # Check permissions
        self.verify_subject_has_permissions_for_course(
            subject, request.course_id, CourseMembershipRole.ADMIN
        )

        # Query the course member from the database
        query = select(CourseMemberEntity).where(
            CourseMemberEntity.user_id == request.user_id,
            CourseMemberEntity.course_id == request.course_id,
        )
        member = self._admin_db.scalars(query).one_or_none()
        if not member:
            raise ResourceNotFoundException(
                f"User {request.user_id} is not a member of course {request.course_id}."
            )

        # Remove the user from the course
        self._admin_db.delete(member)
        self._admin_db.commit()

    def verify_subject_has_permissions_for_course(
        self, subject: Subject, course_id: int, min_role: CourseMembershipRole
    ) -> CourseMembershipRole:
        """
        Ensures that the subject has a certain permission or higher for a course.
        If the subject meets the permission requirements, this function silently
        succeeds, otherwise it raises an exception.
        """
        # Determine which roles are allowed to access a resource based on min requirement.
        allowed_roles_for_min_role = {
            CourseMembershipRole.OWNER: [
                CourseMembershipRole.OWNER,
            ],
            CourseMembershipRole.ADMIN: [
                CourseMembershipRole.OWNER,
                CourseMembershipRole.ADMIN,
            ],
            CourseMembershipRole.STAFF: [
                CourseMembershipRole.OWNER,
                CourseMembershipRole.ADMIN,
                CourseMembershipRole.STAFF,
            ],
            CourseMembershipRole.STUDENT: [
                CourseMembershipRole.OWNER,
                CourseMembershipRole.ADMIN,
                CourseMembershipRole.STAFF,
                CourseMembershipRole.STUDENT,
            ],
        }

        # Query the course member from the database
        query = select(CourseMemberEntity).where(
            CourseMemberEntity.user_id == subject.id,
            CourseMemberEntity.course_id == course_id,
        )
        member = self._admin_db.scalars(query).one_or_none()

        if not member:
            raise ResourceNotFoundException(
                f"User {subject.id} is not a member of course {course_id}"
            )

        # Raise an exception if the user does not have permissions
        if member.role not in allowed_roles_for_min_role[min_role]:
            raise UserPermissionException(
                f"The user does not have sufficient permissions."
            )

        # Return the member's role
        return member.role

    def _generate_invite_code(self) -> str:
        """Generates a random 6-character invite code for a course."""
        character_pool = string.ascii_uppercase + string.digits
        invite_code = "".join(random.choices(character_pool, k=6))
        return invite_code
