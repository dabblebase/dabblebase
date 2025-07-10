"""Testing suite for the courses service."""

import pytest
from ....entities import CourseEntity, CourseMemberEntity
from ....models.course import *
from ....services import CourseService
from ..fixtures import course_svc
from ..seed import (
    seed_database,
    instructor_user,
    admin_user,
    ta_user,
    student_1_user,
    course,
    nocourse_student_user,
)
from .course_data import (
    get_dropdown_request,
    create_course_request,
    create_course_request_invalid_code,
    update_course_request,
    update_course_request_invalid_code,
    update_course_request_not_found,
    add_user_to_course_request,
    add_user_to_course_request_already_member,
    change_user_role_request_owner_upgrades_staff,
    change_user_role_request_owner_demotes_staff,
    change_user_role_admin_upgrades_student,
    change_user_role_admin_upgrades_staff,
    change_user_role_admin_upgrades_self,
    change_user_role_admin_demotes_owner,
    change_user_role_not_found,
    remove_user_from_course_request,
    remove_user_from_course_request_not_found,
)
from ....services.exceptions import (
    InputValidationException,
    UserPermissionException,
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
)
from datetime import datetime, timedelta
from sqlalchemy.orm import Session


def test_get_dashboard(course_svc: CourseService):
    """Test getting the dashboard."""
    # Test for a staff member
    response = course_svc.get_dashboard(instructor_user.to_subject())
    assert response is not None
    assert len(response.staff_courses) == 1
    assert len(response.student_courses) == 0
    # Test for a student
    response = course_svc.get_dashboard(student_1_user.to_subject())
    assert response is not None
    assert len(response.staff_courses) == 0
    assert len(response.student_courses) == 1


def test_get_dropdown(course_svc: CourseService):
    """Test getting the dropdown."""
    response = course_svc.get_dropdown(
        instructor_user.to_subject(), get_dropdown_request
    )
    assert response is not None
    assert len(response.terms) == 1
    assert len(response.courses) == 1

    # Test for a student
    response = course_svc.get_dropdown(
        student_1_user.to_subject(), get_dropdown_request
    )
    assert response is not None
    assert len(response.terms) == 1
    assert len(response.courses) == 1


def test_create_course(admin_db_session: Session, course_svc: CourseService):
    """Tests creating a course."""
    response = course_svc.create_course(
        instructor_user.to_subject(), create_course_request
    )
    created_course = admin_db_session.get(CourseEntity, response.id)

    assert response is not None and created_course is not None
    assert response.id is not None and created_course is not None
    assert response.name == created_course.name == "Test Course"
    assert response.invite_code is not None and created_course.invite_code is not None


def test_create_course_invalid_code(course_svc: CourseService):
    """Ensure that creating a course with an invalid code raises an error."""
    with pytest.raises(InputValidationException):
        course_svc.create_course(
            instructor_user.to_subject(), create_course_request_invalid_code
        )


def test_update_course(admin_db_session: Session, course_svc: CourseService):
    """Test updating a course."""
    course_svc.update_course(instructor_user.to_subject(), update_course_request)
    updated_course = admin_db_session.get(CourseEntity, update_course_request.id)
    assert updated_course is not None
    assert updated_course.code == update_course_request.code


def test_updating_course_no_permission(course_svc: CourseService):
    """Ensure that updating a course without permission raises an error."""
    with pytest.raises(UserPermissionException):
        course_svc.update_course(student_1_user.to_subject(), update_course_request)


def test_updating_course_invalid_code(course_svc: CourseService):
    """Ensure that updating a course with an invalid code raises an error."""
    with pytest.raises(InputValidationException):
        course_svc.update_course(
            instructor_user.to_subject(),
            update_course_request_invalid_code,
        )


def test_updating_course_not_found(course_svc: CourseService):
    """Ensure that updating a course that does not exist raises an error."""
    with pytest.raises(ResourceNotFoundException):
        course_svc.update_course(
            instructor_user.to_subject(), update_course_request_not_found
        )


def test_delete_course(admin_db_session: Session, course_svc: CourseService):
    """Test deleting a course."""
    course_svc.delete_course(instructor_user.to_subject(), course.id)
    deleted_course = admin_db_session.get(CourseEntity, course.id)
    assert deleted_course is None


def test_delete_course_no_permission(course_svc: CourseService):
    """Ensure that deleting a course without permission raises an error."""
    with pytest.raises(UserPermissionException):
        course_svc.delete_course(admin_user.to_subject(), course.id)
    # TODO: Ensure that all assignment databases are deleted


def test_delete_course_not_found(course_svc: CourseService):
    """Ensure that deleting a course that does not exist raises an error."""
    with pytest.raises(ResourceNotFoundException):
        course_svc.delete_course(instructor_user.to_subject(), 404)


def test_add_user_to_course_instructor(
    admin_db_session: Session, course_svc: CourseService
):
    """Test adding a user to a course."""
    course_svc.add_user_to_course(
        instructor_user.to_subject(), add_user_to_course_request
    )
    added_user = (
        admin_db_session.query(CourseMemberEntity)
        .where(
            CourseMemberEntity.user_id == add_user_to_course_request.user_id,
            CourseMemberEntity.course_id == add_user_to_course_request.course_id,
        )
        .first()
    )
    assert added_user is not None
    assert added_user.user_id == nocourse_student_user.id
    assert added_user.course_id == course.id
    assert added_user.role == CourseMembershipRole.STUDENT


def test_add_user_to_course_admin(admin_db_session: Session, course_svc: CourseService):
    """Test adding a user to a course."""
    course_svc.add_user_to_course(admin_user.to_subject(), add_user_to_course_request)
    added_user = (
        admin_db_session.query(CourseMemberEntity)
        .where(
            CourseMemberEntity.user_id == add_user_to_course_request.user_id,
            CourseMemberEntity.course_id == add_user_to_course_request.course_id,
        )
        .first()
    )
    assert added_user is not None
    assert added_user.user_id == nocourse_student_user.id
    assert added_user.course_id == course.id
    assert added_user.role == CourseMembershipRole.STUDENT


def test_add_user_to_course_no_permission(course_svc: CourseService):
    """Ensure that adding a user to a course without permission raises an error."""
    with pytest.raises(UserPermissionException):
        course_svc.add_user_to_course(
            student_1_user.to_subject(), add_user_to_course_request
        )


def test_add_user_to_course_already_member(course_svc: CourseService):
    """Ensure that adding a user to a course that is already a member raises an error."""
    with pytest.raises(ResourceAlreadyExistsException):
        course_svc.add_user_to_course(
            instructor_user.to_subject(), add_user_to_course_request_already_member
        )


def test_join_course(admin_db_session: Session, course_svc: CourseService):
    """Test joining a course with an invite code."""
    course_from_db = admin_db_session.get(CourseEntity, course.id)
    if course_from_db is None:
        pytest.fail("Course not found in the database.")
    join_course_request = JoinCourseRequest(invite_code=course_from_db.invite_code)
    course_svc.join_course(nocourse_student_user.to_subject(), join_course_request)
    added_user = (
        admin_db_session.query(CourseMemberEntity)
        .where(
            CourseMemberEntity.user_id == nocourse_student_user.id,
            CourseMemberEntity.course_id == course_from_db.id,
        )
        .first()
    )
    assert added_user is not None
    assert added_user.user_id == nocourse_student_user.id
    assert added_user.course_id == course_from_db.id


def test_join_course_invalid_invite_code(course_svc: CourseService):
    """Ensure that joining a course with an invalid invite code raises an error."""
    join_course_request = JoinCourseRequest(invite_code="INVALID_CODE")
    with pytest.raises(ResourceNotFoundException):
        course_svc.join_course(nocourse_student_user.to_subject(), join_course_request)


def test_join_course_already_member(
    admin_db_session: Session, course_svc: CourseService
):
    """Ensure that joining a course that the user is already a member of raises an error."""
    course_from_db = admin_db_session.get(CourseEntity, course.id)
    if course_from_db is None:
        pytest.fail("Course not found in the database.")
    join_course_request = JoinCourseRequest(invite_code=course_from_db.invite_code)
    with pytest.raises(ResourceAlreadyExistsException):
        course_svc.join_course(student_1_user.to_subject(), join_course_request)


def test_change_user_role_owner_upgrades_student(
    admin_db_session: Session, course_svc: CourseService
):
    """Test owner upgrading a student's role in a course to staff."""
    course_svc.change_user_role_in_course(
        instructor_user.to_subject(), change_user_role_request_owner_upgrades_staff
    )
    updated_member = (
        admin_db_session.query(CourseMemberEntity)
        .where(
            CourseMemberEntity.user_id == student_1_user.id,
            CourseMemberEntity.course_id == course.id,
        )
        .first()
    )
    assert updated_member is not None
    assert updated_member.role == change_user_role_request_owner_upgrades_staff.role


def test_change_user_role_request_owner_demotes_staff(
    admin_db_session: Session, course_svc: CourseService
):
    """Test owner demoting a staff member's role in a course."""
    course_svc.change_user_role_in_course(
        instructor_user.to_subject(), change_user_role_request_owner_demotes_staff
    )
    updated_member = (
        admin_db_session.query(CourseMemberEntity)
        .where(
            CourseMemberEntity.user_id == student_1_user.id,
            CourseMemberEntity.course_id == course.id,
        )
        .first()
    )
    assert updated_member is not None
    assert updated_member.role == change_user_role_request_owner_demotes_staff.role


def test_change_user_role_admin_upgrades_student(
    admin_db_session: Session, course_svc: CourseService
):
    """Test owner upgrading a student's role in a course to staff."""
    course_svc.change_user_role_in_course(
        admin_user.to_subject(), change_user_role_admin_upgrades_student
    )
    updated_member = (
        admin_db_session.query(CourseMemberEntity)
        .where(
            CourseMemberEntity.user_id == student_1_user.id,
            CourseMemberEntity.course_id == course.id,
        )
        .first()
    )
    assert updated_member is not None
    assert updated_member.role == change_user_role_admin_upgrades_student.role


def test_change_user_role_admin_upgrades_staff(course_svc: CourseService):
    """Ensure that an admin cannot create another admin"""
    with pytest.raises(UserPermissionException):
        course_svc.change_user_role_in_course(
            admin_user.to_subject(), change_user_role_admin_upgrades_staff
        )


def test_change_user_role_admin_upgrades_self(course_svc: CourseService):
    """Ensure that an admin cannot upgrade themselves to owner."""
    with pytest.raises(UserPermissionException):
        course_svc.change_user_role_in_course(
            admin_user.to_subject(), change_user_role_admin_upgrades_self
        )


def test_change_user_role_admin_demotes_owner(course_svc: CourseService):
    """Ensures that an admin cannot demote an owner."""
    with pytest.raises(UserPermissionException):
        course_svc.change_user_role_in_course(
            admin_user.to_subject(), change_user_role_admin_demotes_owner
        )


def test_change_user_role_not_found(course_svc: CourseService):
    """Ensure that changing a user's role in a course that does not exist raises an error."""
    with pytest.raises(ResourceNotFoundException):
        course_svc.change_user_role_in_course(
            instructor_user.to_subject(), change_user_role_not_found
        )


def test_remove_user_from_course(admin_db_session: Session, course_svc: CourseService):
    """Test removing a user from a course."""
    course_svc.remove_user_from_course(
        instructor_user.to_subject(), remove_user_from_course_request
    )
    removed_member = (
        admin_db_session.query(CourseMemberEntity)
        .where(
            CourseMemberEntity.user_id == student_1_user.id,
            CourseMemberEntity.course_id == course.id,
        )
        .first()
    )
    assert removed_member is None


def test_remove_user_from_course_no_permission(course_svc: CourseService):
    """Ensure that removing a user from a course without permission raises an error."""
    with pytest.raises(UserPermissionException):
        course_svc.remove_user_from_course(
            student_1_user.to_subject(), remove_user_from_course_request
        )


def test_remove_user_from_course_not_found(course_svc: CourseService):
    """Ensure that removing a user from a course that does not exist raises an error."""
    with pytest.raises(ResourceNotFoundException):
        course_svc.remove_user_from_course(
            instructor_user.to_subject(), remove_user_from_course_request_not_found
        )


def test_verify_subject_has_permissions_for_course(course_svc: CourseService):
    """Test combinations of user roles and permissions."""
    # Owner tests
    course_svc.verify_subject_has_permissions_for_course(
        instructor_user.to_subject(), course.id, CourseMembershipRole.OWNER
    )
    course_svc.verify_subject_has_permissions_for_course(
        instructor_user.to_subject(), course.id, CourseMembershipRole.ADMIN
    )
    course_svc.verify_subject_has_permissions_for_course(
        instructor_user.to_subject(), course.id, CourseMembershipRole.STAFF
    )
    course_svc.verify_subject_has_permissions_for_course(
        instructor_user.to_subject(), course.id, CourseMembershipRole.STUDENT
    )
    # Admin tests
    with pytest.raises(UserPermissionException):
        course_svc.verify_subject_has_permissions_for_course(
            admin_user.to_subject(), course.id, CourseMembershipRole.OWNER
        )
    course_svc.verify_subject_has_permissions_for_course(
        admin_user.to_subject(), course.id, CourseMembershipRole.ADMIN
    )
    course_svc.verify_subject_has_permissions_for_course(
        admin_user.to_subject(), course.id, CourseMembershipRole.STAFF
    )
    course_svc.verify_subject_has_permissions_for_course(
        admin_user.to_subject(), course.id, CourseMembershipRole.STUDENT
    )
    # Staff tests
    with pytest.raises(UserPermissionException):
        course_svc.verify_subject_has_permissions_for_course(
            ta_user.to_subject(), course.id, CourseMembershipRole.OWNER
        )
    with pytest.raises(UserPermissionException):
        course_svc.verify_subject_has_permissions_for_course(
            ta_user.to_subject(), course.id, CourseMembershipRole.ADMIN
        )
    course_svc.verify_subject_has_permissions_for_course(
        ta_user.to_subject(), course.id, CourseMembershipRole.STAFF
    )
    course_svc.verify_subject_has_permissions_for_course(
        ta_user.to_subject(), course.id, CourseMembershipRole.STUDENT
    )
    # Student tests
    with pytest.raises(UserPermissionException):
        course_svc.verify_subject_has_permissions_for_course(
            student_1_user.to_subject(), course.id, CourseMembershipRole.OWNER
        )
    with pytest.raises(UserPermissionException):
        course_svc.verify_subject_has_permissions_for_course(
            student_1_user.to_subject(), course.id, CourseMembershipRole.ADMIN
        )
    with pytest.raises(UserPermissionException):
        course_svc.verify_subject_has_permissions_for_course(
            student_1_user.to_subject(), course.id, CourseMembershipRole.STAFF
        )
    course_svc.verify_subject_has_permissions_for_course(
        student_1_user.to_subject(), course.id, CourseMembershipRole.STUDENT
    )


def test_generate_invite_code(course_svc: CourseService):
    """Test generating an invite code for a course."""
    invite_code = course_svc._generate_invite_code()
    assert len(invite_code) == 6
    assert invite_code.isalnum()
