import os
import psycopg2
from contextlib import contextmanager
from typing import Callable
from dotenv import load_dotenv
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar

Cursor = psycopg2.extensions.cursor

P = ParamSpec("P")

R = TypeVar("R")

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


def db_connection(func: Callable[Concatenate[Cursor, P], R]) -> Callable[P, R]:
    """Decorator that injects a db connection as first argument."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        with db_session() as conn:
            with conn.cursor() as cur:
                return func(cur, *args, **kwargs)

    return wrapper
