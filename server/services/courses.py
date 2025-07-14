"""Service used to interface with courses"""

from typing import Set
from .base import BaseService
from ..entities import (
    CourseMembershipRole,
    CourseEntity,
    UserEntity,
    AssignmentEntity,
    ProjectGroupMemberEntity,
    ProjectGroupEntity,
    AssignmentState,
)
from ..entities.course import CourseTermType
from fastapi import Depends
from ..models.auth import Subject
from ..models.course import (
    GetDashboardResponse_Course,
    GetDashboardResponse,
    GetDropdownRequest,
    GetDropdownResponse_Course,
    GetDropdownResponse,
    GetAssignmentsResponse_Assignment,
    GetAssignmentsResponse,
    GetRoleForCourseResponse,
    GetStudentsForCourseResponse_Student,
    GetStudentsForCourseResponse,
    GetRosterResponse_Member,
    GetRosterResponse,
    GetStaffSettingsViewResponse,
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
from sqlalchemy import or_, select, func, not_, exists
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

    def get_dashboard(self, subject: Subject) -> GetDashboardResponse:
        """Returns the dashboard for the user"""
        # Query for courses where the user is a staff member
        staff_courses_query = (
            select(CourseEntity)
            .join(CourseMemberEntity)
            .where(
                CourseMemberEntity.user_id == subject.id,
                CourseMemberEntity.role.in_(CourseMembershipRole.staff()),
            )
            .options(
                joinedload(CourseEntity.members).load_only(CourseMemberEntity.user_id),
                joinedload(CourseEntity.assignments).load_only(
                    AssignmentEntity.id, AssignmentEntity.state
                ),
            )
        )
        staff_courses = self._admin_db.scalars(staff_courses_query).unique().all()

        # Query for courses where the user is a student
        student_courses_query = (
            select(CourseEntity)
            .join(CourseMemberEntity)
            .join(AssignmentEntity)
            .where(
                CourseMemberEntity.user_id == subject.id,
                CourseMemberEntity.role == CourseMembershipRole.STUDENT,
            )
            .options(
                joinedload(CourseEntity.assignments),
            )
        )
        student_courses = self._admin_db.scalars(student_courses_query).unique().all()

        # Separate by terms and order terms by year and type
        staff_courses_terms: Set[tuple[int, CourseTermType]] = set()
        staff_courses_by_term: dict[str, list[GetDashboardResponse_Course]] = {}
        student_courses_terms: Set[tuple[int, CourseTermType]] = set()
        student_courses_by_term: dict[str, list[GetDashboardResponse_Course]] = {}

        # Group courses by term and convert to response objects
        for course in staff_courses:
            term = f"{course.term_type.value} {course.term_year}"
            staff_courses_terms.add((course.term_year, course.term_type))
            staff_courses_by_term[term] = staff_courses_by_term.get(term, []) + [
                GetDashboardResponse_Course(
                    id=course.id,
                    code=course.code,
                    name=course.name,
                    num_students=len(course.members),
                    num_assignments=len(course.assignments),
                )
            ]
        for course in student_courses:
            term = f"{course.term_type.value} {course.term_year}"
            student_courses_terms.add((course.term_year, course.term_type))
            student_courses_by_term[term] = student_courses_by_term.get(term, []) + [
                GetDashboardResponse_Course(
                    id=course.id,
                    code=course.code,
                    name=course.name,
                    num_assignments=len(
                        [
                            assignment
                            for assignment in course.assignments
                            if assignment.state == AssignmentState.PUBLISHED
                        ]
                    ),
                )
            ]

        # Sort terms by year, then type
        staff_courses_terms_sorted = sorted(
            staff_courses_terms, key=lambda x: (x[0], x[1].order()), reverse=True
        )
        student_courses_terms_sorted = sorted(
            student_courses_terms, key=lambda x: (x[0], x[1].order()), reverse=True
        )
        staff_courses_terms_list = [
            f"{term_type.value} {term_year}"
            for term_year, term_type in staff_courses_terms_sorted
        ]
        student_courses_terms_list = [
            f"{term_type.value} {term_year}"
            for term_year, term_type in student_courses_terms_sorted
        ]

        # Return the dashboard response
        return GetDashboardResponse(
            most_recent_staff_course_term=(
                staff_courses_terms_list[0] if staff_courses_terms_list else None
            ),
            most_recent_student_course_term=(
                student_courses_terms_list[0] if student_courses_terms_list else None
            ),
            other_staff_course_terms=staff_courses_terms_list[1:],
            other_student_course_terms=student_courses_terms_list[1:],
            staff_courses=staff_courses_by_term,
            student_courses=student_courses_by_term,
        )

    def get_dropdown(
        self, subject: Subject, request: GetDropdownRequest
    ) -> GetDropdownResponse:
        """Returns a list of courses for dropdowns"""
        # Selected course
        selected_course: GetDropdownResponse_Course | None = None
        if request.selected_course_id:
            self.verify_subject_has_permissions_for_course(
                subject, request.selected_course_id, CourseMembershipRole.STUDENT
            )
            query = (
                select(CourseMemberEntity)
                .join(CourseEntity)
                .where(
                    CourseMemberEntity.user_id == subject.id,
                    CourseMemberEntity.course_id == request.selected_course_id,
                )
                .options(joinedload(CourseMemberEntity.course))
            )
            membership = self._admin_db.scalars(query).one_or_none()
            if membership:
                course: CourseEntity = membership.course
                selected_course = GetDropdownResponse_Course(
                    id=course.id,
                    code=course.code,
                    name=course.name,
                    is_staff=(membership.role in CourseMembershipRole.staff()),
                )

        # Query for courses where the user is a staff member
        query = (
            select(CourseMemberEntity)
            .join(CourseEntity)
            .options(joinedload(CourseMemberEntity.course))
            .where(CourseMemberEntity.user_id == subject.id)
        )
        if len(request.search) > 0:
            query = query.where(
                or_(
                    CourseEntity.code.ilike(f"%{request.search}%"),
                    CourseEntity.name.ilike(f"%{request.search}%"),
                ),
            )
        memberships = self._admin_db.scalars(query).unique().all()

        # Get the terms and create course model response
        terms: Set[tuple[int, CourseTermType]] = set()
        dropdown_response_courses: dict[str, list[GetDropdownResponse_Course]] = {}

        for membership in memberships:
            course: CourseEntity = membership.course
            term = f"{course.term_type.value} {course.term_year}"
            terms.add((course.term_year, course.term_type))
            course_response = GetDropdownResponse_Course(
                id=course.id,
                code=course.code,
                name=course.name,
                is_staff=(
                    membership.role
                    in [
                        CourseMembershipRole.OWNER,
                        CourseMembershipRole.ADMIN,
                        CourseMembershipRole.STAFF,
                    ]
                ),
            )
            dropdown_response_courses[term] = dropdown_response_courses.get(
                term, []
            ) + [course_response]

        # Sort terms by year, then type
        terms_sorted = sorted(terms, key=lambda x: (x[0], x[1].order()), reverse=True)
        terms_list = [
            f"{term_type.value} {term_year}" for term_year, term_type in terms_sorted
        ]

        # Sort courses within each term by role, where instructor and student roles are first, then by name.
        for term, courses in dropdown_response_courses.items():
            courses.sort(key=lambda c: (not c.is_staff, c.code.lower()))

        return GetDropdownResponse(
            terms=terms_list,
            selected_course=selected_course,
            courses=dropdown_response_courses,
        )

    def get_assignments(
        self, subject: Subject, course_id: int
    ) -> GetAssignmentsResponse:
        """Returns a list of assignments for a course"""
        # Check permissions
        user_role = self.verify_subject_has_permissions_for_course(
            subject, course_id, CourseMembershipRole.STUDENT
        )
        is_staff = user_role in CourseMembershipRole.staff()

        # Query the assignments for the course
        query = select(AssignmentEntity).where(AssignmentEntity.course_id == course_id)
        # If the user is just a student, filter only for published assignments
        if user_role == CourseMembershipRole.STUDENT:
            query = query.where(AssignmentEntity.state == AssignmentState.PUBLISHED)
        assignments = self._admin_db.scalars(query).all()

        # Build response model and return
        assignment_models = [
            GetAssignmentsResponse_Assignment(
                id=assignment.id,
                name=assignment.name,
                is_group=assignment.is_group_assignment,
                state=assignment.state,
            )
            for assignment in assignments
        ]

        return GetAssignmentsResponse(assignments=assignment_models, is_staff=is_staff)

    def get_role_for_course(
        self, subject: Subject, course_id: int
    ) -> GetRoleForCourseResponse:
        """Returns the role of the subject in the course"""
        # Query the course member from the database
        query = select(CourseMemberEntity).where(
            CourseMemberEntity.user_id == subject.id,
            CourseMemberEntity.course_id == course_id,
        )
        member = self._admin_db.scalars(query).one_or_none()
        return GetRoleForCourseResponse(
            role=member.role if member else None,
            is_staff=member.role in CourseMembershipRole.staff() if member else False,
            can_modify_assignments=(
                member.role in {CourseMembershipRole.OWNER, CourseMembershipRole.ADMIN}
                if member
                else False
            ),
        )

    def get_students_for_course(
        self, subject: Subject, course_id: int, assignment_id: int | None, search: str
    ) -> GetStudentsForCourseResponse:
        """
        Returns a list of students for a course

        Note: If an assignment ID is provided, it will only return students that are not
        already in a group for that assignment.
        """
        # Check permissions
        self.verify_subject_has_permissions_for_course(
            subject, course_id, CourseMembershipRole.STAFF
        )

        # Query the course members where the role is STUDENT
        query = (
            select(UserEntity)
            .join(CourseMemberEntity)
            .where(
                CourseMemberEntity.course_id == course_id,
                CourseMemberEntity.role == CourseMembershipRole.STUDENT,
            )
        )
        # If search is provided, filter by name
        if search:
            query = query.where(
                or_(
                    UserEntity.first_name.ilike(f"%{search}%"),
                    UserEntity.last_name.ilike(f"%{search}%"),
                    func.concat(UserEntity.first_name, " ", UserEntity.last_name).ilike(
                        f"%{search}%"
                    ),
                )
            )
        # If an assignment ID is provided, filter out students that are already in a group
        if assignment_id:
            query = query.where(
                not_(
                    exists(
                        select(ProjectGroupMemberEntity.user_id)
                        .join(ProjectGroupEntity)
                        .where(
                            ProjectGroupMemberEntity.user_id == UserEntity.id,
                            ProjectGroupEntity.assignment_id == assignment_id,
                        )
                    )
                )
            )

        users = self._admin_db.scalars(query).unique().all()

        # Convert to models and return
        students = [
            GetStudentsForCourseResponse_Student(
                user_id=user.id,
                user_name=f"{user.first_name} {user.last_name}",
                user_email=user.email,
            )
            for user in users
        ]
        return GetStudentsForCourseResponse(students=students)

    def get_roster(self, subject: Subject, course_id: int) -> GetRosterResponse:
        """Returns the roster for a course"""
        # Check permissions
        self.verify_subject_has_permissions_for_course(
            subject, course_id, CourseMembershipRole.STAFF
        )

        # Query the course members
        query = (
            select(CourseMemberEntity)
            .where(CourseMemberEntity.course_id == course_id)
            .options(joinedload(CourseMemberEntity.user))
        )
        members = self._admin_db.scalars(query).all()

        # Convert to models and return
        roster_members = [
            GetRosterResponse_Member(
                user_id=member.user.id,
                user_name=f"{member.user.first_name} {member.user.last_name}",
                user_email=member.user.email,
                role=member.role,
            )
            for member in members
        ]
        return GetRosterResponse(members=roster_members)

    def get_staff_settings_view(
        self, subject: Subject, course_id: int
    ) -> GetStaffSettingsViewResponse:
        """Gets the information that is displayed on the staff settings view."""
        # Check permissions
        self.verify_subject_has_permissions_for_course(
            subject, course_id, CourseMembershipRole.STAFF
        )

        # Query the course from the database
        query = select(CourseEntity).where(CourseEntity.id == course_id)
        course = self._admin_db.scalars(query).one_or_none()
        if not course:
            raise ResourceNotFoundException(f"Course with ID {course_id} not found.")

        # Return the course information
        return GetStaffSettingsViewResponse(
            id=course.id,
            code=course.code,
            name=course.name,
            description=course.description,
            invite_code=course.invite_code,
            term_type=course.term_type,
            term_year=course.term_year,
        )

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
            term_type=request.term_type,
            term_year=request.term_year,
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

    def update_course(
        self, subject: Subject, course_id: int, request: UpdateCourseRequest
    ):
        """Updates a course based on the provided data"""
        # Check permissions
        self.verify_subject_has_permissions_for_course(
            subject, course_id, CourseMembershipRole.ADMIN
        )

        # Validate that the course code does not have spaces or special characters
        if not request.code.isalnum():
            raise InputValidationException(
                "Course code must be alphanumeric and cannot contain spaces or special characters."
            )

        # Query the course from the database
        query = select(CourseEntity).where(CourseEntity.id == course_id)
        course = self._admin_db.scalars(query).one_or_none()
        if not course:
            raise ResourceNotFoundException(f"Course with ID {course_id} not found.")

        # Update the course attributes
        course.code = request.code
        course.name = request.name
        course.description = request.description
        course.term_type = request.term_type
        course.term_year = request.term_year
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
        assignments = self._admin_db.scalars(assignments_query).unique().all()

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
