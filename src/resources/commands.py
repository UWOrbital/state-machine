from datetime import datetime
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from src.interfaces.obc_gs_interface.commands.python import CmdCallbackId
from src.interfaces.obc_gs_interface.commands.python.command_factories import (
    COMMAND_FACTORIES,
)
from src.enums.command_enums import CommandStatus
from src.database.utils import DatabaseError

MainTableID = int


@dataclass
class MainCommand:
    """
    Main command model.
    Represents all possible commands that can be issued to the OBC.

    Mirrors the `main.main_command` table. Row container for raw SQL query
    results — no ORM/session semantics.

    List of commands: https://docs.google.com/spreadsheets/d/1XWXgp3--NHZ4XlxOyBYPS-M_LOU_ai-I6TcvotKhR1s/edit?gid=564815068#gid=564815068
    """

    id: "MainTableID"  # NOTE: must stay synced with obc_gs_command_id
    name: str
    data_size: int
    total_size: int
    params: str | None = None
    format: str | None = None
    priority: int = 0

    def __post_init__(self) -> None:
        if self.data_size < 0:
            raise DatabaseError("data_size must be >= 0")
        if self.total_size <= 0:
            raise DatabaseError("total_size must be > 0")
        if self.priority < 0:
            raise DatabaseError("priority must be >= 0")

        self._validate_params_format()

    def _validate_params_format(self) -> None:
        """
        Passes if params and format are both None, or both present with the
        same number of comma-separated values. Raises DatabaseError otherwise.
        """
        if self.format is None and self.params is None:
            return

        if self.params is not None and self.format is not None:
            # TODO: Check if the params have valid types
            if self.params.count(",") == self.format.count(","):
                return
            raise DatabaseError(
                "Params and format do not have the same number of values"
            )

        if self.params is None:
            raise DatabaseError("Missing params")
        else:  # self.format is None
            raise DatabaseError("Missing format")

    @classmethod
    def from_row(cls, row: tuple) -> "MainCommand":
        """
        Build a MainCommand from a raw psycopg2 fetchone/fetchall row.
        Assumes column order: id, name, params, format, data_size, total_size, priority
        """
        return cls(
            id=row[0],
            name=row[1],
            params=row[2],
            format=row[3],
            data_size=row[4],
            total_size=row[5],
            priority=row[6],
        )


@dataclass
class DatabaseCommand:
    """
    An instance of a MainCommand.
    Holds data related to actual commands sent from the ground station up to the OBC.

    Mirrors the `transactional.commands` table. No ORM/session semantics —
    this is just a row container for raw SQL query results.
    """
    session_id: UUID
    id: UUID = field(default_factory=uuid4)
    user_id: UUID | None = None
    status: CommandStatus = CommandStatus.PENDING
    type_: int | None = (
        None  # FK -> main_command.id (MainTableID); no ForeignKey enforcement here
    )
    params: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    packet_id: UUID | None = None
    sequence_index: int | None = None

    @classmethod
    def from_row(cls, row: tuple) -> "DatabaseCommand":
        """
        Build a Commands instance from a raw psycopg2 fetchone/fetchall row.
        Assumes column order: id, user_id, status, type_, params, created_at, packet_id, sequence_index, session_id
        """
        return cls(
            id=row[0],
            user_id=row[1],
            status=CommandStatus(row[2]),
            type_=row[3],
            params=row[4],
            created_at=row[5],
            packet_id=row[6],
            sequence_index=row[7],
            session_id=row[8],
        )


class Command:
    """
    An abstraction of the CLI commands so that adapting the comms pipeline packet logic
    into GS will be easier.
    """

    def __init__(
        self, params: dict[str, str | int | bool | float], cmd_id: int, prio: int
    ) -> None:
        """
        This abstracts the commands in a way which makes it accessible for GS.
        The reason this is created is so that we are able to have a 1:1 clone of the
        commands which allow for easier adoption of pre-existing pipelines built for CLI.

        :name: name which matches the command name
        :id: id which matches the id in the satelite
        :params: list of command as a string, matches command param options
        :prio: command priority. integer which goes from 1 to n where n is the number of
               priorities we have. 1 is the highest priority
        :time: tracks the time at which a command has been created
        """
        self.db_command: DatabaseCommand | None = None
        self.command_id: CmdCallbackId | None = None
        self.factory_args: list[str | int | bool | float] = []

        try:
            self.command_id = CmdCallbackId(cmd_id)
        except KeyError:
            # TODO: Find a better way of logging this
            print("Invalid Command Id", cmd_id)

        # We need to ensure that these are given in the right order
        # TODO: these are dummy param names, they need to be updated
        for param_name, param in params.items():
            if param_name == "time_of_execution":
                self.factory_args.append(param)
            if param_name == "log_level" or param_name == "rtc_time":
                self.factory_args.insert(0, param)

        if self.command_id is not None:
            self.cmd_msg = COMMAND_FACTORIES[self.command_id](*self.factory_args)
        else:
            # TODO: Better error handling
            print("Command ID unbound")

        self.prio = prio
        self.time = datetime.now()
