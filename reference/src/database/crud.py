from datetime import datetime, timezone
from uuid import UUID, uuid4
from reference.src.database.connection import Cursor, db_connection
from reference.src.enums.command_enums import CommandStatus, SessionStatus
from reference.src.resources.commands import DatabaseCommand, MainCommand


@db_connection
def get_next_session(cur: Cursor) -> datetime | None:
    """
    Returns the start_time of the next upcoming session — the soonest
    PENDING session with a start_time still in the future. Returns None
    if no such session exists.
    """
    cur.execute(
        """
        SELECT start_time
        FROM transactional.sessions
        WHERE status = %s AND start_time > now()
        ORDER BY start_time ASC
        LIMIT 1
        """,
        (SessionStatus.PENDING.value,),
    )
    row = cur.fetchone()
    return row[0] if row is not None else None


@db_connection
def get_next_session_id(cur: Cursor) -> UUID | None:
    """
    Returns the ID of the next upcoming pending session.
    """
    cur.execute(
        """
        SELECT id
        FROM transactional.sessions
        WHERE status = %s
          AND start_time > NOW()
        ORDER BY start_time ASC
        LIMIT 1
        """,
        (SessionStatus.PENDING.value,),
    )

    row = cur.fetchone()
    return row[0] if row is not None else None


# TODO: add error handling if start_time is None
@db_connection
def update_current_session_status(
    cur: Cursor,
    status: SessionStatus,
    start_time: datetime | None,
) -> None:
    cur.execute(
        """
        UPDATE transactional.sessions
        SET status = %s
        WHERE id = (
            SELECT id
            FROM transactional.sessions
            WHERE start_time = %s
            ORDER BY start_time ASC
            LIMIT 1
        )
        """,
        (status.value, start_time),
    )


@db_connection
def get_main_command_by_id(cur: Cursor, command_id: int | None) -> MainCommand | None:
    """
    Replacement for MainCommandWrapper().get_by_id(command.type_).
    Fetches a single row from main.commands.
    """
    if command_id is None:
        return None
    cur.execute(
        """
        SELECT id, name, params, format, data_size, total_size, priority
        FROM main.commands
        WHERE id = %s
        """,
        (command_id,),
    )
    row = cur.fetchone()
    if not row:
        return None
    return MainCommand.from_row(row)


@db_connection
def get_all_commands_by_status(
    cur: Cursor, status: CommandStatus
) -> list[DatabaseCommand]:
    """
    Replacement for CommandsWrapper().get_all_by(status=CommandStatus.PENDING).
    Fetches all rows from transactional.commands matching a given status.
    """
    cur.execute(
        """
        SELECT id, user_id, status, type_, params, created_at, packet_id, sequence_index
        FROM transactional.commands
        WHERE status = %s
        """,
        (status.value,),
    )
    rows = cur.fetchall()
    return [DatabaseCommand.from_row(row) for row in rows]


@db_connection
def get_all_commands_next_session(
    cur: Cursor,
    status: CommandStatus,
) -> list[DatabaseCommand]:
    session_id = get_next_session_id()

    if session_id is None:
        return []

    cur.execute(
        """
        SELECT
            id,
            user_id,
            status,
            type_,
            params,
            created_at,
            packet_id,
            sequence_index,
            session_id
        FROM transactional.commands
        WHERE session_id = %s
          AND status = %s
        """,
        (
            session_id,
            status.value,
        ),
    )

    return [DatabaseCommand.from_row(row) for row in cur.fetchall()]


@db_connection
def update_command_status(cur: Cursor, command_id: UUID, status: CommandStatus) -> None:
    """
    Replacement for CommandsWrapper().update(command_id, {"status": ...}).
    Used in build_queue() (-> SCHEDULED), queue_to_packet() (-> ONGOING),
    and clear_queue() (-> COMPLETED).
    """
    cur.execute(
        """
        UPDATE transactional.commands
        SET status = %s
        WHERE id = %s
        """,
        (status.value, command_id),
    )


@db_connection
def update_command_response(cur: Cursor, command_id: UUID, response: str) -> None:
    cur.execute(
        """
    UPDATE transactional.commands
    SET response = %s
    WHERE id = %s
    """,
        (response, command_id),
    )


@db_connection
def create_telemetry(
    cur: Cursor,
    type_: int,
    value: object,
    timestamp: datetime,
) -> None:
    """
    Insert one telemetry value into transactional.telemetry.

    timestamp must be timezone-aware. It is normalized to UTC before insertion.
    """

    if timestamp.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")

    timestamp_utc = timestamp.astimezone(timezone.utc)

    cur.execute(
        """
        INSERT INTO transactional.telemetry (
            id,
            type_,
            value,
            timestamp
        )
        VALUES (%s, %s, %s, %s);
        """,
        (
            str(uuid4()),
            type_,
            str(value),
            timestamp_utc,
        ),
    )


@db_connection
def clear_telemetry_by_type(cur: Cursor, telemetry_type: int) -> int:
    """
    Deletes every telemetry row whose type_ matches telemetry_type.

    Returns the number of rows deleted.
    """
    cur.execute(
        """
        DELETE FROM transactional.telemetry
        WHERE type_ = %s
        """,
        (telemetry_type,),
    )

    deleted_count = cur.rowcount

    return deleted_count
