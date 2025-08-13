"""
Base entities for the admin database for which the other
entities inherit from.
"""

from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, Session


class BaseAdminEntity(DeclarativeBase):
    """
    Base class for all entities of the admin database.
    """

    pass

    @classmethod
    def setup_functions(cls, session: Session):
        """Sets up the functions and triggers for the admin database."""

        # Create a function that notifies when a new project is created
        # This function is used to notify the realtime server when new projects
        # are created so that it can begin listening to the project for
        # changes and updates.
        notify_new_project_sql = """
        CREATE FUNCTION notify_new_project() RETURNS trigger AS $$
        BEGIN
          PERFORM pg_notify('new_project', row_to_json(NEW)::text);
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trg_new_project
        AFTER INSERT ON projects
        FOR EACH ROW EXECUTE FUNCTION notify_new_project();
        """

        session.execute(text(notify_new_project_sql))
        session.commit()
