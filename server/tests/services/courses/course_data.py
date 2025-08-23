"""Data models specific to course testing"""

from ....seeds.demo import (
    course,
    nocourse_student_user,
    student_1_user,
    admin_user,
    ta_user,
    instructor_user,
)
from ....models.course import *
from datetime import datetime, timedelta

get_dropdown_request = GetDropdownRequest(search="")

create_course_request = CreateCourseRequest(
    code="TEST123",
    name="Test Course",
    description="This is a test course.",
    term_type=CourseTermType.FALL,
    term_year=datetime.now().year,
)

create_course_request_invalid_code = CreateCourseRequest(
    code="TEST 123",
    name="Test Course",
    description="This is a test course.",
    term_type=CourseTermType.FALL,
    term_year=datetime.now().year,
)


update_course_request = UpdateCourseRequest(
    code="NEW1234",
    name="Updated Test Course",
    description="This is an updated test course.",
    term_type=CourseTermType.FALL,
    term_year=datetime.now().year,
)

update_course_request_invalid_code = UpdateCourseRequest(
    code="TEST 123",
    name="Updated Test Course",
    description="This is an updated test course.",
    term_type=CourseTermType.FALL,
    term_year=datetime.now().year,
)

update_course_request_not_found = UpdateCourseRequest(
    code="NEW1234",
    name="Updated Test Course",
    description="This is an updated test course.",
    term_type=CourseTermType.FALL,
    term_year=datetime.now().year,
)

add_user_to_course_request = AddUserToCourseRequest(
    user_id=nocourse_student_user.id, course_id=course.id
)

add_user_to_course_request_already_member = AddUserToCourseRequest(
    user_id=student_1_user.id, course_id=course.id
)

change_user_role_request_owner_upgrades_staff = ChangeUserRoleInCourseRequest(
    course_id=course.id,
    user_id=student_1_user.id,
    role=CourseMembershipRole.STAFF,
)

change_user_role_request_owner_demotes_staff = ChangeUserRoleInCourseRequest(
    course_id=course.id,
    user_id=ta_user.id,
    role=CourseMembershipRole.STUDENT,
)

change_user_role_admin_upgrades_student = ChangeUserRoleInCourseRequest(
    course_id=course.id,
    user_id=student_1_user.id,
    role=CourseMembershipRole.STAFF,
)

change_user_role_admin_upgrades_student = ChangeUserRoleInCourseRequest(
    course_id=course.id,
    user_id=student_1_user.id,
    role=CourseMembershipRole.STAFF,
)

change_user_role_admin_upgrades_staff = ChangeUserRoleInCourseRequest(
    course_id=course.id,
    user_id=student_1_user.id,
    role=CourseMembershipRole.ADMIN,
)

change_user_role_admin_upgrades_self = ChangeUserRoleInCourseRequest(
    course_id=course.id,
    user_id=admin_user.id,
    role=CourseMembershipRole.OWNER,
)

change_user_role_admin_demotes_owner = ChangeUserRoleInCourseRequest(
    course_id=course.id,
    user_id=instructor_user.id,
    role=CourseMembershipRole.ADMIN,
)

change_user_role_not_found = ChangeUserRoleInCourseRequest(
    course_id=course.id,
    user_id=nocourse_student_user.id,
    role=CourseMembershipRole.STAFF,
)

remove_user_from_course_request = RemoveUserFromCourseRequest(
    course_id=course.id, user_id=student_1_user.id
)

remove_user_from_course_request_not_found = RemoveUserFromCourseRequest(
    course_id=course.id, user_id=nocourse_student_user.id
)
