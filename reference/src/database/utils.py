class DatabaseError(Exception):
    """Raised when a row fails a data-integrity check that would normally be enforced by the ORM/DB layer."""
