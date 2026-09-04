import contextlib
import warnings

from reference.src.database.crud import (
    get_all_commands_by_status,
    get_main_command_by_id,
    update_command_status,
)
from reference.src.resources.commands import Command, DatabaseCommand
from interfaces import PADDING_REQUIRED
from interfaces.obc_gs_interface.commands.python import CmdMsg
from interfaces.obc_gs_interface.commands.python.command_framing import (
    command_multi_pack,
)
from interfaces.utils.command_packaging import CommandPackaging
from reference.src.enums.command_enums import CommandStatus


class CommandsPipeline:
    """
    Recieves, sorts, and packets commands such that they may be sent to the
    satellite.

    This is basically another abstraction layer for the database.
    """

    def __init__(self) -> None:
        """
        Lockout should be set at some arbitrary time before session begins.
        Once lockout is True, commands will no longer be received
        """
        self.lockout: bool = False
        self.commands_queue: list[Command] = []
        self.packet_list: list[bytes] = []

    def queue_to_packet(self) -> list[bytes]:
        """
        Converts all commands in the queue into packets.
        """

        if len(self.commands_queue) == 0:
            warnings.warn(
                "No commands in queue. Packeting will succeed but have no effect.",
                stacklevel=1,
            )
            return [b"\x00"]

        command_messages: list[CmdMsg] = []
        command_bytes: list[bytes] = []
        comms = CommandPackaging()

        for command in self.commands_queue:
            command_messages.append(command.cmd_msg)

        command_bytes = command_multi_pack(command_messages)

        for byte_string in command_bytes:
            self.packet_list.append(
                comms.encode_frame(byte_string).ljust(PADDING_REQUIRED, b"\x00")
            )

        for command in self.commands_queue:
            if command.db_command:
                update_command_status(command.db_command.id, CommandStatus.ONGOING)

        return self.packet_list

    def build_queue(self) -> list[DatabaseCommand]:
        """
        Builds the queue from the database based on status.
        """

        db_commands = get_all_commands_by_status(CommandStatus.PENDING)

        for db_command in db_commands:
            param_list = db_command.params.split(",") if db_command.params else []
            processed_param: dict[str, str | int | bool | float] = {}

            for i in range(0, len(param_list) - 1, 2):
                val_str = param_list[i + 1]
                val: str | int | bool | float = val_str

                if val_str.lower() in ["true", "false"]:
                    val = val_str.lower() == "true"
                else:
                    with contextlib.suppress(ValueError):
                        val = int(val_str)

                    if isinstance(val, str):
                        with contextlib.suppress(ValueError):
                            val = float(val_str)

                processed_param[param_list[i]] = val

            main_cmd = get_main_command_by_id(db_command.type_)
            priority = main_cmd.priority if main_cmd else 0

            command = Command(
                params=processed_param, cmd_id=db_command.type_, prio=priority
            )
            command.db_command = db_command
            command.time = db_command.created_at
            self.commands_queue.append(command)

            update_command_status(db_command.id, CommandStatus.SCHEDULED)

        self.sort_queue()
        return db_commands

    def sort_queue(self) -> list[Command]:
        """
        This function sorts the queue 2 times. We first sort by time to ensure time descending,
        then we sort by priority to ensure that the highest priority is at the top of the
        queue.
        """
        self.commands_queue.sort(key=lambda x: x.time)
        self.commands_queue.sort(key=lambda x: x.prio)
        return self.commands_queue

    def clear_queue(self) -> None:
        """
        Sets all command status to completed and clears queue (please note that we should have a separate
        enum for aborted)
        """
        for command in self.commands_queue:
            if command.db_command:
                update_command_status(command.db_command.id, CommandStatus.COMPLETED)

        self.commands_queue = []

    def clear_packets(self) -> None:
        """
        Clears the packet list so that a new set of commands can be queued.
        """
        self.packet_list = []
