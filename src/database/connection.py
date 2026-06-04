import os
import psycopg2
from contextlib import contextmanager
from typing import Callable
from dotenv import load_dotenv

load_dotenv()


def getenv(key: str):
    value = os.getenv(key)
    if not value:
        raise ValueError(f"{key} not found in .env.")
    return value


def get_conn():
    return psycopg2.connect(
        host=getenv("DB_HOST"),
        port=getenv("DB_PORT"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
    )


@contextmanager
def db_session():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def db_connection(func: Callable) -> Callable:
    """Decorator that injects a db connection as first argument."""

    def wrapper(*args, **kwargs):
        with db_session() as db:
            return func(db, *args, **kwargs)

    return wrapper
