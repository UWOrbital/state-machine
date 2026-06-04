from src.database.connection import db_connection


@db_connection
def get_latest_session(db): ...
