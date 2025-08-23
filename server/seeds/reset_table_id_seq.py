"""
Helper function to reset the ID sequence of a db table for seeding the
databse with pre-defined IDs so that insertions do not conflict with
existing IDs.
"""

from sqlalchemy import text
from sqlalchemy.orm import Session, DeclarativeBase, InstrumentedAttribute


def reset_table_id_seq(
    session: Session,
    entity: type[DeclarativeBase],
    entity_id_column: InstrumentedAttribute[int],
    next_id: int,
) -> None:
    """Reset the ID sequence of a table"""
    table = entity.__table__
    id_column_name = entity_id_column.name
    sql = text(f"ALTER SEQUENCE {table}_{id_column_name}_seq RESTART WITH {next_id}")
    session.execute(sql)
