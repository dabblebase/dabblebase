"""Service used to interface with courses"""

from .base import BaseService
from ..entities import CourseMembershipRole
from ..models.auth import Subject
from ..entities import CourseMemberEntity
from .exceptions import ResourceNotFoundException, UserPermissionException
from sqlalchemy import select


class CourseService(BaseService):

    def verify_subject_has_permissions_for_course(
        self, subject: Subject, course_id: int, min_role: CourseMembershipRole
    ):
        """
        Ensures that the subject has a certain permission or higher for a course.
        If the subject meets the permission requirements, this function silently
        succeeds, otherwise it raises an exception.
        """
        # Determine which roles are allowed to access a resource based on min requirement.
        allowed_roles_for_min_role = {
            CourseMembershipRole.ADMIN: [CourseMembershipRole.ADMIN],
            CourseMembershipRole.STAFF: [
                CourseMembershipRole.ADMIN,
                CourseMembershipRole.STAFF,
            ],
            CourseMembershipRole.STUDENT: [
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
