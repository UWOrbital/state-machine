from uuid import UUID

from src.database.connection import Cursor, db_connection
from src.enums.command_enums import CommandStatus
from src.resources.commands import DatabaseCommand, MainCommand


@db_connection
def get_main_command_by_id(cur: Cursor, command_id: int) -> MainCommand | None:
    """
    Replacement for MainCommandWrapper().get_by_id(command.type_).
    Fetches a single row from main.commands.
    """
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
