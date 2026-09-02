import time
from datetime import datetime, timedelta

from reference.src.database.crud import get_next_session
from reference.src.resources.commands_pipeline import CommandsPipeline

# How long before a session starts we should have commands packed and ready.
PRE_SESSION_LEAD_TIME = timedelta(minutes=5)

# How often to re-check for a scheduled session when none is currently pending.
NO_SESSION_POLL_INTERVAL = timedelta(minutes=1).total_seconds()


def main() -> None:
    while True:
        next_session_start = get_next_session()

        if next_session_start is None:
            time.sleep(NO_SESSION_POLL_INTERVAL)
            continue

        wake_time = next_session_start - PRE_SESSION_LEAD_TIME
        sleep_seconds = (wake_time - datetime.now()).total_seconds()

        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

        pipeline = CommandsPipeline()
        pipeline.build_queue()
        pipeline.queue_to_packet()

        # Uplinking during the session itself is out of scope here. Sleep
        # past the session's start_time so get_next_session() — which only
        # returns sessions with start_time > now() — stops returning this
        # same session on the next loop iteration and moves on to whatever
        # is scheduled next.
        remaining_to_session_start = (
            next_session_start - datetime.now()
        ).total_seconds()
        if remaining_to_session_start > 0:
            time.sleep(remaining_to_session_start)


if __name__ == "__main__":
    main()
