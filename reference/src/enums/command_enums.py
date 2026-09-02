from enum import StrEnum


# TODO: Change the name of this file, since its not just for command enums
class SessionStatus(StrEnum):
    """
    Represents the possible states that a session can be in
    """

    PENDING = "PENDING"  # Initial state of a session. Optional or can start at SCHEDULED status
    SCHEDULED = "SCHEDULED"  # Session has been scheduled. GS has not received any data yet but the start time is known
    ONGOING = "ONGOING"  # Session has been started. GS is receiving data
    COMPLETED = "COMPLETED"  # Session is complete. GS has received all the data for the session. Final state of session


class CommandStatus(StrEnum):
    """
    Represents the possible states that a command can be in
    """

    PENDING = "PENDING"  # Command was created in the db but not yet sent to the OBC
    SCHEDULED = "SCHEDULED"  # Command was sent to the OBC
    ONGOING = "ONGOING"  # Command is executing on the OBC
    CANCELLED = (
        "CANCELLED"  # Command was cancelled by MCC. This is a final state of a command
    )
    FAILED = "FAILED"  # Command failed to complete. This is a final state of a command
    COMPLETED = "COMPLETED"  # Command executed successfully. this should be the final state of a command if all was successful
