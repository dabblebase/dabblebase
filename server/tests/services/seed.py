"""Seed data for testing purposes."""

from entities import *
from sqlalchemy.orm import Session
import pytest
from datetime import datetime, timedelta

# Setup
now = datetime.now()

# Sample users
instructor_user = UserEntity(
    id=1, auth_id="999999999", auth_provider=UserAuthenticationProvider.UNC_SSO
)
admin_user = UserEntity(
    id=2, auth_id="888888888", auth_provider=UserAuthenticationProvider.UNC_SSO
)
ta_user = UserEntity(
    id=3, auth_id="777777777", auth_provider=UserAuthenticationProvider.UNC_SSO
)
student_1_user = UserEntity(
    id=4, auth_id="000000001", auth_provider=UserAuthenticationProvider.UNC_SSO
)
student_2_user = UserEntity(
    id=5, auth_id="000000002", auth_provider=UserAuthenticationProvider.UNC_SSO
)
users: list[UserEntity] = [
    instructor_user,
    admin_user,
    ta_user,
    student_1_user,
    student_2_user,
]

# Sample courses
course = CourseEntity(
    id=1,
    code="COMP426",
    name="Modern Web Programming",
    description="A course on modern web programming techniques.",
    start_date=now - timedelta(days=30),
    end_date=now + timedelta(days=30),
)
courses = [course]

# Sample course members
course_member_instructor = CourseMemberEntity(
    user_id=instructor_user.id, course_id=course.id, role=CourseMembershipRole.OWNER
)
course_member_admin = CourseMemberEntity(
    user_id=admin_user.id, course_id=course.id, role=CourseMembershipRole.ADMIN
)
course_member_ta = CourseMemberEntity(
    user_id=ta_user.id, course_id=course.id, role=CourseMembershipRole.STAFF
)
course_member_student_1 = CourseMemberEntity(
    user_id=student_1_user.id, course_id=course.id, role=CourseMembershipRole.STUDENT
)
course_member_student_2 = CourseMemberEntity(
    user_id=student_2_user.id, course_id=course.id, role=CourseMembershipRole.STUDENT
)
course_members: list[CourseMemberEntity] = [
    course_member_instructor,
    course_member_admin,
    course_member_ta,
    course_member_student_1,
    course_member_student_2,
]


def insert_seed_data(session: Session):
    for user in users:
        session.add(user)
    session.flush()
    for course in courses:
        session.add(course)
    for member in course_members:
        session.add(member)
    session.flush()


@pytest.fixture(autouse=True)
def seed_database(admin_db_session: Session):
    insert_seed_data(admin_db_session)
    admin_db_session.commit()
