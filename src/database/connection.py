import os
import psycopg2
from contextlib import contextmanager
from typing import Callable
from dotenv import load_dotenv
from functools import wraps

Cursor = psycopg2.extensions.cursor

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

    @wraps(func)
    def wrapper(*args, **kwargs):
        with db_session() as conn:
            with conn.cursor() as cur:
                return func(cur, *args, **kwargs)

    return wrapper
