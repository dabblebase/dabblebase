"""Seed data for testing purposes."""

from server.database import admin_db_engine
from server.entities.course import CourseTermType
from ..entities import (
    UserEntity,
    UserEntityModel,
    UserAuthenticationProvider,
    CourseEntity,
    CourseEntityModel,
    CourseMemberEntityModel,
    CourseMembershipRole,
    AssignmentEntity,
    AssignmentEntityModel,
    AssignmentState,
    ProjectGroupEntity,
    ProjectGroupEntityModel,
    ProjectGroupMemberEntity,
    ProjectGroupMemberEntityModel,
)
from sqlalchemy.orm import Session
import pytest
from datetime import datetime, timedelta
from .reset_table_id_seq import reset_table_id_seq

# Setup
now = datetime.now()

# Sample users
instructor_user = UserEntityModel(
    id=1,
    auth_id="999999999",
    auth_provider=UserAuthenticationProvider.UNC_SSO,
    username="instructor",
    first_name="Ina",
    last_name="Instructor",
    email="instructor@unc.edu",
    is_instructor=True,
)
admin_user = UserEntityModel(
    id=2,
    auth_id="888888888",
    auth_provider=UserAuthenticationProvider.UNC_SSO,
    username="admin",
    first_name="Audrey",
    last_name="Admin",
    email="admin@unc.edu",
    is_instructor=False,
)
ta_user = UserEntityModel(
    id=3,
    auth_id="777777777",
    auth_provider=UserAuthenticationProvider.UNC_SSO,
    username="teddy",
    first_name="Teddy",
    last_name="TA",
    email="ta@unc.edu",
    is_instructor=False,
)
student_1_user = UserEntityModel(
    id=4,
    auth_id="000000001",
    auth_provider=UserAuthenticationProvider.UNC_SSO,
    username="student_1",
    first_name="Sally",
    last_name="Student",
    email="student1@unc.edu",
    is_instructor=False,
)
student_2_user = UserEntityModel(
    id=5,
    auth_id="000000002",
    auth_provider=UserAuthenticationProvider.UNC_SSO,
    username="student_2",
    first_name="Shauna",
    last_name="Student",
    email="student2@unc.edu",
    is_instructor=False,
)
nocourse_student_user = UserEntityModel(
    id=6,
    auth_id="000000003",
    auth_provider=UserAuthenticationProvider.UNC_SSO,
    username="student_nocourse",
    first_name="Norman",
    last_name="Nocourse-Student",
    email="nocoursestudent@unc.edu",
    is_instructor=False,
)

users: list[UserEntityModel] = [
    instructor_user,
    admin_user,
    ta_user,
    student_1_user,
    student_2_user,
    nocourse_student_user,
]

# Sample courses
course = CourseEntityModel(
    id=1,
    code="COMP426",
    name="Modern Web Programming",
    description="A course on modern web programming techniques.",
    term_type=CourseTermType.FALL,
    term_year=datetime.now().year,
    invite_code="ABCDEF",
)
courses = [course]

# Sample course members
course_member_instructor = CourseMemberEntityModel(
    user_id=instructor_user.id, course_id=course.id, role=CourseMembershipRole.OWNER
)
course_member_admin = CourseMemberEntityModel(
    user_id=admin_user.id, course_id=course.id, role=CourseMembershipRole.ADMIN
)
course_member_ta = CourseMemberEntityModel(
    user_id=ta_user.id, course_id=course.id, role=CourseMembershipRole.STAFF
)
course_member_student_1 = CourseMemberEntityModel(
    user_id=student_1_user.id, course_id=course.id, role=CourseMembershipRole.STUDENT
)
course_member_student_2 = CourseMemberEntityModel(
    user_id=student_2_user.id, course_id=course.id, role=CourseMembershipRole.STUDENT
)
course_members: list[CourseMemberEntityModel] = [
    course_member_instructor,
    course_member_admin,
    course_member_ta,
    course_member_student_1,
    course_member_student_2,
]

# Sample assignments
draft_indiv_assignment = AssignmentEntityModel(
    id=1,
    name="Assignment 1",
    state=AssignmentState.DRAFT,
    is_group_assignment=False,
    course_id=course.id,
)

draft_group_assignment = AssignmentEntityModel(
    id=2,
    name="Group Assignment 2",
    state=AssignmentState.DRAFT,
    is_group_assignment=True,
    course_id=course.id,
)

published_assignment = AssignmentEntityModel(
    id=3,
    name="Published Assignment",
    state=AssignmentState.PUBLISHED,
    is_group_assignment=False,
    course_id=course.id,
)

assignments: list[AssignmentEntityModel] = [
    draft_indiv_assignment,
    draft_group_assignment,
    published_assignment,
]

# Sample assignment groups and members
group_assignment_group_1 = ProjectGroupEntityModel(
    id=1,
    name="Group 1",
    assignment_id=draft_group_assignment.id,
)
group_assignment_group_1_member = ProjectGroupMemberEntityModel(
    user_id=student_1_user.id,
    group_id=group_assignment_group_1.id,
)

groups = [group_assignment_group_1]
group_members = [group_assignment_group_1_member]


def insert_seed_data(session: Session = Session(admin_db_engine(echo=False))):

    for user in users:
        session.add(user.to_entity())
    reset_table_id_seq(session, UserEntity, UserEntity.id, len(users) + 1)
    session.commit()

    for course in courses:
        session.add(course.to_entity())
    reset_table_id_seq(session, CourseEntity, CourseEntity.id, len(courses) + 1)
    session.commit()

    for member in course_members:
        session.add(member.to_entity())
    session.commit()

    for assignment in assignments:
        session.add(assignment.to_entity())
    reset_table_id_seq(
        session, AssignmentEntity, AssignmentEntity.id, len(assignments) + 1
    )
    session.commit()

    for group in groups:
        session.add(group.to_entity())
    reset_table_id_seq(
        session, ProjectGroupEntity, ProjectGroupEntity.id, len(groups) + 1
    )

    for member in group_members:
        session.add(member.to_entity())
    session.commit()


@pytest.fixture(autouse=True)
def seed_demo_fixture(admin_db_session: Session):
    insert_seed_data(admin_db_session)
    admin_db_session.commit()
    yield
