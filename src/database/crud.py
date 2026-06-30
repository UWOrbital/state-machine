from src.database.connection import db_connection, Cursor


@db_connection
def get_latest_session(db: Cursor): ...
