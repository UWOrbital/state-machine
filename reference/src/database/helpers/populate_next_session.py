from reference.src.database.connection import Cursor, db_connection
from uuid import uuid4
from reference.src.database.crud import get_all_commands_next_session
from reference.src.enums.command_enums import CommandStatus


@db_connection
def create_pings_next_session(cur: Cursor) -> None:
    cur.execute(
        """
                SELECT id
                FROM transactional.sessions
                WHERE status = 'PENDING'
                  AND start_time > now()
                ORDER BY start_time ASC
                LIMIT 1
                """
    )

    session = cur.fetchone()

    if session is None:
        raise RuntimeError("No pending future session was found")

    session_id = session[0]
    cur.execute(
        """
                SELECT id
                FROM main.commands
                WHERE name = 'CMD_PING'
                LIMIT 1
                """
    )

    command_type = cur.fetchone()

    if command_type is None:
        raise RuntimeError("CMD_PING was not found in main.command")

    command_type_id = command_type[0]

    rows = [
        (
            str(uuid4()),  # id
            "PENDING",  # status
            command_type_id,  # type_
            sequence_index,  # sequence_index
            str(session_id),  # session_id
        )
        for sequence_index in range(3)
    ]

    cur.executemany(
        """
    INSERT INTO transactional.commands (
        id,
        status,
        type_,
        sequence_index,
        session_id
    )
    VALUES (%s, %s, %s, %s, %s);
    """,
        rows,
    )


@db_connection
def create_downlink_command_next_session(cur: Cursor) -> None:
    cur.execute(
        """
                SELECT id
                FROM transactional.sessions
                WHERE status = 'PENDING'
                  AND start_time > now()
                ORDER BY start_time ASC
                LIMIT 1
                """
    )

    session = cur.fetchone()

    if session is None:
        raise RuntimeError("No pending future session was found")

    session_id = session[0]
    cur.execute(
        """
                SELECT id
                FROM main.commands
                WHERE name = 'CMD_DOWNLINK_TELEM'
                LIMIT 1
                """
    )

    command_type = cur.fetchone()

    if command_type is None:
        raise RuntimeError("CMD_DOWNLINK_TELEM was not found in main.command")

    command_type_id = command_type[0]

    rows = [
        (
            str(uuid4()),  # id
            "PENDING",  # status
            command_type_id,  # type_
            sequence_index,  # sequence_index
            str(session_id),  # session_id
        )
        for sequence_index in range(1)
    ]

    cur.executemany(
        """
    INSERT INTO transactional.commands (
        id,
        status,
        type_,
        sequence_index,
        session_id
    )
    VALUES (%s, %s, %s, %s, %s);
    """,
        rows,
    )


def main() -> None:
    create_pings_next_session()
    create_downlink_command_next_session()
    print(get_all_commands_next_session(CommandStatus.PENDING))


if __name__ == "__main__":
    main()
