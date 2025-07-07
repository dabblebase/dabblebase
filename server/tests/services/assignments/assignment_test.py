"""Testing suite for the assignments service."""

import pytest
from ....env import env
from ....entities import (
    AssignmentEntity,
    AssignmentState,
    ProjectGroupEntity,
    ProjectGroupMemberEntity,
    ProjectEntity,
)
from ....models.assignment import *
from ....services import AssignmentService
from ..fixtures import assignment_svc
from ..seed import (
    seed_database,
    instructor_user,
    admin_user,
    ta_user,
    student_1_user,
    course,
    nocourse_student_user,
    draft_indiv_assignment,
    draft_group_assignment,
    published_assignment,
    group_assignment_group_1,
)

from .assignment_data import (
    create_draft_request,
    rename_request,
    rename_request_name_empty,
    rename_request_not_found,
    create_group_request,
    create_group_request_for_indiv,
    create_group_request_for_noname,
    add_group_member_request,
    add_member_request_not_found,
    remove_group_member_request,
    remove_member_request_not_found,
    remove_member_request_not_found_user,
    delete_group_request,
    delete_group_request_not_found,
)
from ....services.exceptions import (
    InputValidationException,
    UserPermissionException,
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
)
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text


def test__create_project(assignment_svc: AssignmentService):
    """Tests that a project is created when an assignment is created."""
    project = assignment_svc._create_project(
        assignment_id=draft_group_assignment.id, group_id=group_assignment_group_1.id
    )
    assert project is not None
    admin_role_password = assignment_svc._content_db_cluster_svc.decrypt_role_password(
        project.encrypted_admin_role_password,
        project.assignment_id,
    )
    db_url = f"postgresql+psycopg2://{project.admin_role_name}:{admin_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{project.db_name}"
    engine = create_engine(db_url, echo=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

    student_role_password = (
        assignment_svc._content_db_cluster_svc.decrypt_role_password(
            project.encrypted_student_role_password,
            project.assignment_id,
        )
    )
    db_url = f"postgresql+psycopg2://{project.student_role_name}:{student_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{project.db_name}"
    engine = create_engine(db_url, echo=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_create_draft(admin_db_session: Session, assignment_svc: AssignmentService):
    """Tests creating a draft assignment."""
    # Test the creation of the assignment object
    response = assignment_svc.create_draft(
        instructor_user.to_subject(), create_draft_request
    )
    draft_assignment: AssignmentEntity | None = admin_db_session.query(
        AssignmentEntity
    ).get(response.assignment_id)
    assert draft_assignment is not None
    assert draft_assignment.state == AssignmentState.DRAFT
    assert draft_assignment.test_db_name is not None
    assert draft_assignment.test_db_admin_role_name is not None
    assert draft_assignment.encrypted_test_db_admin_role_password is not None
    assert draft_assignment.test_db_view_role_name is not None
    assert draft_assignment.encrypted_test_db_view_role_password is not None

    # Attempt to connect to the admin database using the admin role
    admin_role_password = assignment_svc._content_db_cluster_svc.decrypt_role_password(
        draft_assignment.encrypted_test_db_admin_role_password, draft_assignment.id
    )
    db_url = f"postgresql+psycopg2://{draft_assignment.test_db_admin_role_name}:{admin_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{draft_assignment.test_db_name}"
    engine = create_engine(db_url, echo=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

    # Attempt to connect to the admin database using the view role
    view_role_password = assignment_svc._content_db_cluster_svc.decrypt_role_password(
        draft_assignment.encrypted_test_db_view_role_password, draft_assignment.id
    )
    db_url = f"postgresql+psycopg2://{draft_assignment.test_db_view_role_name}:{view_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{draft_assignment.test_db_name}"
    engine = create_engine(db_url, echo=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_create_draft_no_permissions(assignment_svc: AssignmentService):
    """Ensures that a user without permissions cannot create a draft assignment."""
    with pytest.raises(UserPermissionException):
        assignment_svc.create_draft(ta_user.to_subject(), create_draft_request)
    with pytest.raises(UserPermissionException):
        assignment_svc.create_draft(student_1_user.to_subject(), create_draft_request)


def test_rename(admin_db_session: Session, assignment_svc: AssignmentService):
    """Ensures that an assignment can be renamed."""
    assignment_svc.rename(instructor_user.to_subject(), rename_request)
    renamed_assignment = admin_db_session.query(AssignmentEntity).get(
        rename_request.assignment_id
    )
    assert renamed_assignment is not None
    assert renamed_assignment.name == rename_request.name


def test_rename_no_permissions(assignment_svc: AssignmentService):
    """Ensures that a user without permissions cannot rename an assignment."""
    with pytest.raises(UserPermissionException):
        assignment_svc.rename(ta_user.to_subject(), rename_request)
    with pytest.raises(UserPermissionException):
        assignment_svc.rename(student_1_user.to_subject(), rename_request)


def test_rename_name_empty(assignment_svc: AssignmentService):
    """Ensures that renaming an assignment to an empty name raises an exception."""
    with pytest.raises(InputValidationException):
        assignment_svc.rename(instructor_user.to_subject(), rename_request_name_empty)


def test_rename_not_found(assignment_svc: AssignmentService):
    """Ensures that renaming a non-existent assignment raises an exception."""
    with pytest.raises(ResourceNotFoundException):
        assignment_svc.rename(instructor_user.to_subject(), rename_request_not_found)


def test_test_configuration_sql_success(assignment_svc: AssignmentService):
    """Tests that the configuration SQL can be tested."""
    # TODO: Remove reliance on setup here
    # First, create a draft assignment, which spins up the database.
    response = assignment_svc.create_draft(
        instructor_user.to_subject(), create_draft_request
    )
    draft_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(response.assignment_id)
    assert draft_assignment is not None

    # Now, test the configuration SQL
    test_configuration_sql_request_success = TestConfigurationSQLRequest(
        assignment_id=draft_assignment.id,
        sql="""
        CREATE TABLE test_table (id INT PRIMARY KEY, name VARCHAR(100));
        INSERT INTO test_table (id, name) VALUES (1, 'Test Name');
        """,
    )
    response = assignment_svc.test_configuration_sql(
        instructor_user.to_subject(), test_configuration_sql_request_success
    )

    assert response.success is True
    assert response.error_message is None
    assert response.db_url is not None

    engine = create_engine(response.db_url, echo=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM test_table WHERE id = 1;"))
        assert result.scalar() == 1

    assert draft_assignment.draft_project_configuration_sql is not None
    assert (
        draft_assignment.draft_project_configuration_sql
        == test_configuration_sql_request_success.sql
    )
    assert draft_assignment.draft_project_configuration_sql_succeeded is True
    assert draft_assignment.draft_project_configuration_sql_error is None


def test_test_configuration_sql_failure_syntax_error(assignment_svc: AssignmentService):
    """Tests that the configuration SQL fails gracefully with a syntax error."""
    # TODO: Remove reliance on setup here
    # First, create a draft assignment, which spins up the database.
    response = assignment_svc.create_draft(
        instructor_user.to_subject(), create_draft_request
    )
    draft_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(response.assignment_id)
    assert draft_assignment is not None

    # Now, test the configuration SQL with a syntax error
    test_configuration_sql_request_syntax_error = TestConfigurationSQLRequest(
        assignment_id=draft_assignment.id,
        sql="""
        CREATEEE TABLE test_table (id INT PRIMARY KEY, name VARCHAR(100));
        """,
    )
    response = assignment_svc.test_configuration_sql(
        instructor_user.to_subject(), test_configuration_sql_request_syntax_error
    )

    assert response.success is False
    assert response.error_message is not None
    assert response.db_url is None

    assert draft_assignment.draft_project_configuration_sql is not None
    assert (
        draft_assignment.draft_project_configuration_sql
        == test_configuration_sql_request_syntax_error.sql
    )
    assert draft_assignment.draft_project_configuration_sql_succeeded is False
    assert draft_assignment.draft_project_configuration_sql_error is not None


def test_test_configuration_sql_failure_naughty_request(
    assignment_svc: AssignmentService,
):
    """Tests that the configuration SQL fails gracefully with a naughty request."""
    # TODO: Remove reliance on setup here
    # First, create a draft assignment, which spins up the database.
    response = assignment_svc.create_draft(
        instructor_user.to_subject(), create_draft_request
    )
    draft_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(response.assignment_id)
    assert draft_assignment is not None

    # Now, test the configuration SQL with a create database request
    test_configuration_sql_request_create_db = TestConfigurationSQLRequest(
        assignment_id=draft_assignment.id, sql="CREATE DATABASE naughty_db;"
    )
    response = assignment_svc.test_configuration_sql(
        instructor_user.to_subject(), test_configuration_sql_request_create_db
    )

    assert response.success is False
    assert response.error_message is not None
    assert response.error_message.startswith("(psycopg2.errors.InsufficientPrivilege)")
    assert response.db_url is None

    assert draft_assignment.draft_project_configuration_sql is not None
    assert (
        draft_assignment.draft_project_configuration_sql
        == test_configuration_sql_request_create_db.sql
    )
    assert draft_assignment.draft_project_configuration_sql_succeeded is False
    assert draft_assignment.draft_project_configuration_sql_error is not None

    # Now, test the configuration SQL with a create role request
    test_configuration_sql_request_create_role = TestConfigurationSQLRequest(
        assignment_id=draft_assignment.id,
        sql="CREATE ROLE naughty_role LOGIN PASSWORD '1234'",
    )
    response = assignment_svc.test_configuration_sql(
        instructor_user.to_subject(), test_configuration_sql_request_create_role
    )

    assert response.success is False
    assert response.error_message is not None
    assert response.error_message.startswith("(psycopg2.errors.InsufficientPrivilege)")
    assert response.db_url is None

    assert draft_assignment.draft_project_configuration_sql is not None
    assert (
        draft_assignment.draft_project_configuration_sql
        == test_configuration_sql_request_create_role.sql
    )
    assert draft_assignment.draft_project_configuration_sql_succeeded is False
    assert draft_assignment.draft_project_configuration_sql_error is not None


def test_save_configuration_sql(assignment_svc: AssignmentService):
    """Tests that the configuration SQL can be saved."""
    # TODO: Remove reliance on setup here
    # First, create a draft assignment, which spins up the database, and test SQL.
    response = assignment_svc.create_draft(
        instructor_user.to_subject(), create_draft_request
    )
    draft_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(response.assignment_id)
    assert draft_assignment is not None
    test_configuration_sql_request_success = TestConfigurationSQLRequest(
        assignment_id=draft_assignment.id,
        sql="""
        CREATE TABLE test_table (id INT PRIMARY KEY, name VARCHAR(100));
        INSERT INTO test_table (id, name) VALUES (1, 'Test Name');
        """,
    )
    response = assignment_svc.test_configuration_sql(
        instructor_user.to_subject(), test_configuration_sql_request_success
    )

    # Now, test saving the configuration SQL
    save_configuration_sql_request = SaveConfigurationSQLRequest(
        assignment_id=draft_assignment.id
    )
    assignment_svc.save_configuration_sql(
        subject=instructor_user.to_subject(), request=save_configuration_sql_request
    )
    saved_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(draft_assignment.id)
    assert saved_assignment is not None
    assert saved_assignment.project_configuration_sql is not None
    assert (
        saved_assignment.project_configuration_sql
        == test_configuration_sql_request_success.sql
    )
    assert saved_assignment.draft_project_configuration_sql is None
    assert saved_assignment.draft_project_configuration_sql_succeeded is None
    assert saved_assignment.draft_project_configuration_sql_error is None


def test_save_configuration_sql_not_tested(assignment_svc: AssignmentService):
    """Ensures that saving configuration SQL without testing it raises an exception."""
    # TODO: Remove reliance on setup here
    # First, create a draft assignment, which spins up the database, and test SQL.
    response = assignment_svc.create_draft(
        instructor_user.to_subject(), create_draft_request
    )
    draft_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(response.assignment_id)
    assert draft_assignment is not None
    request = SaveConfigurationSQLRequest(assignment_id=draft_assignment.id)

    # Now, test that an exception is raised
    with pytest.raises(InputValidationException):
        assignment_svc.save_configuration_sql(instructor_user.to_subject(), request)


def test_save_configuration_sql_tested_but_failed(assignment_svc: AssignmentService):
    """Ensures that saving configuration SQL without testing it raises an exception."""
    # TODO: Remove reliance on setup here
    # First, create a draft assignment, which spins up the database, and test SQL.
    response = assignment_svc.create_draft(
        instructor_user.to_subject(), create_draft_request
    )
    draft_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(response.assignment_id)
    assert draft_assignment is not None
    test_configuration_sql_request = TestConfigurationSQLRequest(
        assignment_id=draft_assignment.id,
        sql="""
        CREATE DATABASE naughty_db;
        """,
    )
    assignment_svc.test_configuration_sql(
        instructor_user.to_subject(), test_configuration_sql_request
    )
    request = SaveConfigurationSQLRequest(assignment_id=draft_assignment.id)

    # Now, test that an exception is raised
    with pytest.raises(InputValidationException):
        assignment_svc.save_configuration_sql(instructor_user.to_subject(), request)


def test_create_group(admin_db_session: Session, assignment_svc: AssignmentService):
    """Tests that a group can be created for an assignment."""
    response = assignment_svc.create_group(
        instructor_user.to_subject(), create_group_request
    )
    group = admin_db_session.get(ProjectGroupEntity, response.group_id)
    assert group is not None
    assert group.name == create_group_request.group_name


def test_create_group_for_indiv(
    admin_db_session: Session, assignment_svc: AssignmentService
):
    """Ensures that a group cannot be created for a group assignment."""
    with pytest.raises(InputValidationException):
        assignment_svc.create_group(
            instructor_user.to_subject(), create_group_request_for_indiv
        )


def test_create_group_for_noname(
    assignment_svc: AssignmentService,
):
    """Ensures that a group cannot be created with an empty name."""
    with pytest.raises(InputValidationException):
        assignment_svc.create_group(
            instructor_user.to_subject(), create_group_request_for_noname
        )


def test_add_group_member(admin_db_session: Session, assignment_svc: AssignmentService):
    """Tests adding a member to a group."""
    assignment_svc.add_group_member(
        instructor_user.to_subject(), add_group_member_request
    )
    member = (
        admin_db_session.query(ProjectGroupMemberEntity)
        .filter(
            ProjectGroupMemberEntity.user_id == add_group_member_request.user_id,
            ProjectGroupMemberEntity.group_id == add_group_member_request.group_id,
        )
        .first()
    )
    assert member is not None


def test_add_group_member_not_found(
    assignment_svc: AssignmentService,
):
    """Ensures that adding a member to a non-existent group raises an exception."""
    with pytest.raises(ResourceNotFoundException):
        assignment_svc.add_group_member(
            instructor_user.to_subject(), add_member_request_not_found
        )


def test_remove_group_member(
    admin_db_session: Session, assignment_svc: AssignmentService
):
    """Tests removing a member from a group."""
    assignment_svc.remove_group_member(
        instructor_user.to_subject(), remove_group_member_request
    )
    member = (
        admin_db_session.query(ProjectGroupMemberEntity)
        .filter(
            ProjectGroupMemberEntity.user_id == remove_group_member_request.user_id,
            ProjectGroupMemberEntity.group_id == remove_group_member_request.group_id,
        )
        .first()
    )
    assert member is None


def test_remove_group_member_not_found(
    assignment_svc: AssignmentService,
):
    """Ensures that removing a member from a non-existent group raises an exception."""
    with pytest.raises(ResourceNotFoundException):
        assignment_svc.remove_group_member(
            instructor_user.to_subject(), remove_member_request_not_found
        )


def test_remove_group_member_not_found_user(
    assignment_svc: AssignmentService,
):
    """Ensures that removing a non-existent user from a group raises an exception."""
    with pytest.raises(ResourceNotFoundException):
        assignment_svc.remove_group_member(
            instructor_user.to_subject(), remove_member_request_not_found_user
        )


def test_delete_group(admin_db_session: Session, assignment_svc: AssignmentService):
    """Tests deleting a group from an assignment."""
    response = assignment_svc.create_group(
        instructor_user.to_subject(), create_group_request
    )
    delete_group_request.group_id = response.group_id
    assignment_svc.delete_group(instructor_user.to_subject(), delete_group_request)
    group = admin_db_session.get(ProjectGroupEntity, delete_group_request.group_id)
    assert group is None
    members = (
        admin_db_session.query(ProjectGroupMemberEntity)
        .filter(ProjectGroupMemberEntity.group_id == delete_group_request.group_id)
        .all()
    )
    assert len(members) == 0


def test_delete_group_not_found(
    assignment_svc: AssignmentService,
):
    """Ensures that deleting a non-existent group raises an exception."""
    with pytest.raises(ResourceNotFoundException):
        assignment_svc.delete_group(
            instructor_user.to_subject(), delete_group_request_not_found
        )


def test_publish_individual(
    assignment_svc: AssignmentService,
):
    """Tests that publishing an assignment works correctly for an indiv assignment."""
    assignment_svc.publish(instructor_user.to_subject(), draft_indiv_assignment.id)
    published_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(draft_indiv_assignment.id)
    assert published_assignment is not None
    assert published_assignment.state == AssignmentState.PUBLISHED

    projects = (
        assignment_svc._admin_db.query(ProjectEntity)
        .filter(ProjectEntity.assignment_id == draft_indiv_assignment.id)
        .all()
    )
    assert len(projects) == 2

    for project in projects:
        admin_role_password = (
            assignment_svc._content_db_cluster_svc.decrypt_role_password(
                project.encrypted_admin_role_password, project.assignment_id
            )
        )
        db_url = f"postgresql+psycopg2://{project.admin_role_name}:{admin_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{project.db_name}"
        engine = create_engine(db_url, echo=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

        student_role_password = (
            assignment_svc._content_db_cluster_svc.decrypt_role_password(
                project.encrypted_student_role_password, project.assignment_id
            )
        )
        db_url = f"postgresql+psycopg2://{project.student_role_name}:{student_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{project.db_name}"
        engine = create_engine(db_url, echo=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1


def test_publish_group(
    assignment_svc: AssignmentService,
):
    """Tests that publishing an assignment works correctly for a group assignment."""
    assignment_svc.publish(instructor_user.to_subject(), draft_group_assignment.id)
    published_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(draft_group_assignment.id)
    assert published_assignment is not None
    assert published_assignment.state == AssignmentState.PUBLISHED

    projects = (
        assignment_svc._admin_db.query(ProjectEntity)
        .filter(ProjectEntity.assignment_id == draft_group_assignment.id)
        .all()
    )
    assert len(projects) == 1

    project = projects[0]
    assert project.group_id is not None

    admin_role_password = assignment_svc._content_db_cluster_svc.decrypt_role_password(
        project.encrypted_admin_role_password, project.assignment_id
    )
    db_url = f"postgresql+psycopg2://{project.admin_role_name}:{admin_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{project.db_name}"
    engine = create_engine(db_url, echo=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

    student_role_password = (
        assignment_svc._content_db_cluster_svc.decrypt_role_password(
            project.encrypted_student_role_password, project.assignment_id
        )
    )
    db_url = f"postgresql+psycopg2://{project.student_role_name}:{student_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{project.db_name}"
    engine = create_engine(db_url, echo=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_publish_already_published(
    assignment_svc: AssignmentService,
):
    """Tests that publishing an already published assignment raises an exception."""
    with pytest.raises(InputValidationException):
        assignment_svc.publish(instructor_user.to_subject(), published_assignment.id)


def test_delete(assignment_svc: AssignmentService):
    """Tests that an assignment can be deleted."""
    # Load all of the data for checking that the deletion worked
    assignment_svc.publish(instructor_user.to_subject(), draft_group_assignment.id)
    published_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(draft_group_assignment.id)
    assert published_assignment is not None

    projects = (
        assignment_svc._admin_db.query(ProjectEntity)
        .filter(ProjectEntity.assignment_id == draft_group_assignment.id)
        .all()
    )
    project_db_credentials = [
        (
            project.db_name,
            project.admin_role_name,
            assignment_svc._content_db_cluster_svc.decrypt_role_password(
                project.encrypted_admin_role_password, published_assignment.id
            ),
            project.student_role_name,
            assignment_svc._content_db_cluster_svc.decrypt_role_password(
                project.encrypted_student_role_password, published_assignment.id
            ),
        )
        for project in projects
    ]

    # Delete the assignment and check that it was deleted
    assignment_svc.delete(instructor_user.to_subject(), draft_group_assignment.id)

    deleted_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(draft_group_assignment.id)
    assert deleted_assignment is None

    for (
        db_name,
        admin_role_name,
        admin_role_password,
        student_role_name,
        student_role_password,
    ) in project_db_credentials:
        db_url = f"postgresql+psycopg2://{admin_role_name}:{admin_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{db_name}"
        engine = create_engine(db_url, echo=True)
        with pytest.raises(Exception):
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        db_url = f"postgresql+psycopg2://{student_role_name}:{student_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{db_name}"
        engine = create_engine(db_url, echo=True)
        with pytest.raises(Exception):
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))


def test_unpublish(
    assignment_svc: AssignmentService,
):
    """Tests that an assignment can be unpublished."""
    # Collect all of the data needed for checking that the unpublish worked
    assignment_svc.publish(instructor_user.to_subject(), draft_indiv_assignment.id)
    published_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(draft_indiv_assignment.id)
    assert published_assignment is not None
    projects = (
        assignment_svc._admin_db.query(ProjectEntity)
        .filter(ProjectEntity.assignment_id == draft_group_assignment.id)
        .all()
    )
    project_db_credentials = [
        (
            project.db_name,
            project.admin_role_name,
            assignment_svc._content_db_cluster_svc.decrypt_role_password(
                project.encrypted_admin_role_password, published_assignment.id
            ),
            project.student_role_name,
            assignment_svc._content_db_cluster_svc.decrypt_role_password(
                project.encrypted_student_role_password, published_assignment.id
            ),
        )
        for project in projects
    ]

    # Unpublish the assignment
    assignment_svc.unpublish(instructor_user.to_subject(), draft_indiv_assignment.id)
    unpublished_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(draft_indiv_assignment.id)
    assert unpublished_assignment is not None
    assert unpublished_assignment.state == AssignmentState.UNPUBLISHED

    for (
        db_name,
        admin_role_name,
        admin_role_password,
        student_role_name,
        student_role_password,
    ) in project_db_credentials:
        db_url = f"postgresql+psycopg2://{admin_role_name}:{admin_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{db_name}"
        engine = create_engine(db_url, echo=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

        db_url = f"postgresql+psycopg2://{student_role_name}:{student_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{db_name}"
        engine = create_engine(db_url, echo=True)
        with pytest.raises(Exception):
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.scalar() == 1


def test_unpublish_not_published(
    assignment_svc: AssignmentService,
):
    """Tests that unpublishing an assignment that is not published raises an exception."""
    with pytest.raises(InputValidationException):
        assignment_svc.unpublish(
            instructor_user.to_subject(), draft_indiv_assignment.id
        )


def test_republish(
    assignment_svc: AssignmentService,
):
    """Tests that an assignment can be republished."""
    # Get all of the data needed for checking that the republish worked
    assignment_svc.publish(instructor_user.to_subject(), draft_indiv_assignment.id)
    published_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(draft_indiv_assignment.id)
    assert published_assignment is not None
    assignment_svc.unpublish(instructor_user.to_subject(), published_assignment.id)
    projects = (
        assignment_svc._admin_db.query(ProjectEntity)
        .filter(ProjectEntity.assignment_id == draft_indiv_assignment.id)
        .all()
    )

    # Republish the assignment and check that it was republished
    assignment_svc.republish(instructor_user.to_subject(), published_assignment.id)

    republished_assignment: AssignmentEntity | None = assignment_svc._admin_db.query(
        AssignmentEntity
    ).get(draft_indiv_assignment.id)
    assert republished_assignment is not None
    assert republished_assignment.state == AssignmentState.PUBLISHED

    for project in projects:
        admin_role_password = (
            assignment_svc._content_db_cluster_svc.decrypt_role_password(
                project.encrypted_admin_role_password, project.assignment_id
            )
        )
        db_url = f"postgresql+psycopg2://{project.admin_role_name}:{admin_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{project.db_name}"
        engine = create_engine(db_url, echo=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

        student_role_password = (
            assignment_svc._content_db_cluster_svc.decrypt_role_password(
                project.encrypted_student_role_password, project.assignment_id
            )
        )
        db_url = f"postgresql+psycopg2://{project.student_role_name}:{student_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{project.db_name}"
        engine = create_engine(db_url, echo=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1


def test_republish_not_unpublished(
    assignment_svc: AssignmentService,
):
    """Tests that republishing an assignment that is not unpublished raises an exception."""
    with pytest.raises(InputValidationException):
        assignment_svc.republish(
            instructor_user.to_subject(), draft_indiv_assignment.id
        )
