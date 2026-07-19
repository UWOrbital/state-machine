from state_machine_class import StateMachine
from database.crud import get_next_session, update_current_session_status, get_all_commands_next_session, update_command_response, get_main_command_by_id, update_command_status, create_telemetry, clear_telemetry_by_type
from enums.command_enums import SessionStatus, CommandStatus
from uart_connection import UartConnection
from sys import argv
from interfaces.utils.command_utils import (
    LOG_PATH,
    send_command,
    send_conn_request,
)
from interfaces.obc_gs_interface.commands.python import CmdCallbackId 
from interfaces.obc_gs_interface.commands.python.command_response_classes import CmdRes

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import time

# Times from Postgres, times used in Python are UTC, we convert to EST when printing
def print_time_local(t: datetime):
    print(t.astimezone(ZoneInfo("America/Toronto")))

def main():
    if len(argv) != 2:
        print("Usage: python state_mgr_run.py <COM_PORT>")
        return
    uart_conn = UartConnection(argv[1])
    uart_conn.connect_uart()
    print("UART Successfully Created")
    sent_conn_request = False 
    while (1):
        # Get next session time, only gets pending sessions so no chance of sending the same commands twice in the same session
        next_session = get_next_session()
        if next_session is None:
            print("Error getting session, re-run the program")
            return
        print_time_local(next_session)

        # Get all commands for next session, store as an array of names 
        # TODO: Integrate command pipeline to store multiple commands into packets
        # TODO: Update get_all_commands_next_session to take an id
        next_session_commands = get_all_commands_next_session(CommandStatus.PENDING)

        # Wait for session
        time_next_session_sec = (next_session - datetime.now(timezone.utc)).total_seconds()
        print(f"Sleeping until next session {time_next_session_sec}s")
        
        #time.sleep(time_next_session_sec)
        time.sleep(10)
        current_session = next_session
        update_current_session_status(SessionStatus.ONGOING, current_session)
         
        # Send connection request for session
        if not sent_conn_request:
            try:
                send_conn_request(uart_conn.com_port, 1)
                sent_conn_request = True
            except IndexError:
                print("Connection request was not successful. Try resetting the board")
    
        # Send each command in sequence
        #ping_command = "--command CMD_PING"
        #for i in range(5):
        #   response = send_command(ping_command, uart_conn.com_port, 1)
        #    print(response)
        for command in next_session_commands:
            if command is None:
                print("Error processing command, command is None")
                continue
            # TODO Make command.type not able to be None in Postgres
            main_command= get_main_command_by_id(command.type_)
            if main_command is None: 
                print("Command could not be found in main.commands")
                continue
            if main_command.name is None:
                print("Command name could not be found in main.commands entry")
                continue
            command_string = f"--command {main_command.name}"
            #TODO Edit interfaces/utils/obc_gs_command_utils to have a send_command that bypasses specific CLI formatting
            print(f"Sending {main_command.name}")
            response = send_command(command_string, uart_conn.com_port, 1)
               
            # We do additional handling for CMD_DOWNLINK_TELEM
            if main_command.name == "CMD_DOWNLINK_TELEM":
                if response is None:
                    print("No telemetry response received")
                    continue

                if isinstance(response, CmdRes):
                    print(
                    "Expected telemetry data, but send_command returned CmdRes:",
                    response,
                    )
                    continue

                # If valid telemetry packet, clear previous telemetry of the same id. All telemetry is downlinked every time the command is sent - FIX THIS
                # Offset by 100 as DB is offset by 100 compared to CmdCallbackId.
                clear_telemetry_by_type(response[0].id+100)
                for telem in response:
                    create_telemetry(
                    telem.id + 100,
                    telem.obcTemp,
                    datetime.fromtimestamp(
                    telem.timestamp,
                    tz=timezone.utc,
                        ),
                    )
 
            print(response)
            # Update response and status for each sent command
            update_command_status(command.id, CommandStatus.COMPLETED)
            update_command_response(command.id, str(response))

        # Send reset command, as we can't send another send_conn_request until the board is reset (Don't know why)
        # We don't want to use this for the actual demo, as it will reset after we send the GNC command or image command. Rev4 seems to be able to work as long as we replug in the USB.
        reset_command = "--command CMD_EXEC_OBC_RESET"
        #response = send_command(reset_command, uart_conn.com_port, 1) 

        # Mark the current session as done
        
        past_session = current_session
        update_current_session_status(SessionStatus.COMPLETED, past_session)
if __name__ == "__main__":
    main()



