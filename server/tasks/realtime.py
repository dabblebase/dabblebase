"""Celery tasks related to realtime functionality."""

from fastapi import Depends
from ..celery import celery_app
from .di_generators import get_assignment_service
from sqlalchemy.orm import Session
from ..database import admin_db_session
from ..entities import ProjectEntity


@celery_app.task(name="realtime.update_tracking_databases")
def update_tracking_databases():
    """Celery task to publish an assignment."""
    assignment_svc = get_assignment_service()
    BATCH_SIZE = 100
    try:
        session: Session = next(admin_db_session(echo=False))
        projects = session.query(ProjectEntity).all()
        session.close()

        for i in range(0, len(projects), BATCH_SIZE):
            batch = projects[i : i + BATCH_SIZE]
            # Transform the batch into a list of tuples
            batch = [
                (
                    project.id,
                    project.db_name,
                    project.admin_role_name,
                    assignment_svc._content_db_cluster_svc.decrypt_role_password(
                        project.encrypted_admin_role_password, project.assignment_id
                    ),
                    project.table_hash,
                )
                for project in batch
            ]
            update_tracking_databases_batch.delay(batch)

    except Exception as e:
        print(f"Error dispatching batch patch tasks: {e}")


@celery_app.task(name="realtime.update_tracking_databases_batch")
def update_tracking_databases_batch(projects: list[tuple[str, str, str, str, str]]):
    for project_id, db_name, db_role, db_password, existing_table_hash in projects:
        update_tracking_databases_triggers.delay(
            project_id, db_name, db_role, db_password, existing_table_hash
        )


@celery_app.task(name="realtime.update_tracking_databases_triggers")
def update_tracking_databases_triggers(
    project_id: int,
    db_name: str,
    db_role: str,
    db_password: str,
    existing_table_hash: str,
):
    assignment_svc = get_assignment_service()
    try:
        # Generate a hash of all of the tables in a student database
        tables, table_hash = (
            assignment_svc._content_db_cluster_svc.get_hash_of_tables_in_database(
                db_name, db_role, db_password
            )
        )

        # If the table hash has not changed, no new tables have been added, so we can
        # skip applying new triggers to the student database
        if existing_table_hash == table_hash:
            return

        # Otherwise, Attach the trigger function to each table in the student database
        for table in tables:
            assignment_svc._content_db_cluster_svc.add_realtime_trigger_to_database(
                db_name, db_role, db_password, table
            )

        # Finally, update the table hash in the admin database
        admin_db: Session = next(admin_db_session())
        project = admin_db.get(ProjectEntity, project_id)
        if project:
            project.table_hash = table_hash
            admin_db.commit()
        admin_db.close()

    except Exception as e:
        print(f"Error patching triggers for {project_id}: {e}")
