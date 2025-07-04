"""Seed data for testing purposes."""

from ...entities import (
    UserEntity,
    UserEntityModel,
    UserAuthenticationProvider,
    CourseEntity,
    CourseEntityModel,
    CourseMemberEntityModel,
    CourseMembershipRole,
)
from sqlalchemy.orm import Session
import pytest
from datetime import datetime, timedelta
from .reset_table_id_seq import reset_table_id_seq

# Setup
now = datetime.now()

# Sample users
instructor_user = UserEntityModel(
    id=1, auth_id="999999999", auth_provider=UserAuthenticationProvider.UNC_SSO
)
admin_user = UserEntityModel(
    id=2, auth_id="888888888", auth_provider=UserAuthenticationProvider.UNC_SSO
)
ta_user = UserEntityModel(
    id=3, auth_id="777777777", auth_provider=UserAuthenticationProvider.UNC_SSO
)
student_1_user = UserEntityModel(
    id=4, auth_id="000000001", auth_provider=UserAuthenticationProvider.UNC_SSO
)
student_2_user = UserEntityModel(
    id=5, auth_id="000000002", auth_provider=UserAuthenticationProvider.UNC_SSO
)
nocourse_student_user = UserEntityModel(
    id=6, auth_id="000000003", auth_provider=UserAuthenticationProvider.UNC_SSO
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
    start_date=now - timedelta(days=30),
    end_date=now + timedelta(days=30),
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


def insert_seed_data(session: Session):

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


@pytest.fixture(autouse=True)
def seed_database(admin_db_session: Session):
    insert_seed_data(admin_db_session)
    admin_db_session.commit()
    yield
