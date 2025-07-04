"""All entities must be imported to be included with resetting the db."""

from .base import BaseAdminEntity
from .project import ProjectEntity, ProjectEntityModel
from .user import UserEntity, UserAuthenticationProvider, UserEntityModel
from .course import CourseEntity, CourseEntityModel
from .course_member import (
    CourseMemberEntity,
    CourseMembershipRole,
    CourseMemberEntityModel,
)
from .project_group import ProjectGroupEntity, ProjectGroupEntityModel
from .project_group_member import (
    ProjectGroupMemberEntity,
    ProjectGroupMemberEntityModel,
)
from .project_users import ProjectUserEntity, ProjectUserEntityModel
from .assignment import AssignmentEntity, AssignmentState, AssignmentEntityModel
