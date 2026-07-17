from state_machine_class import StateMachine
from database.crud import get_next_session
from uart_connection import UartConnection
from interfaces.utils.command_utils import (
    LOG_PATH,
    send_command,
    send_conn_request,
)
from interfaces.obc_gs_interface.commands.python import CmdCallbackId

def main():
    if len(argv) != 2:
        print("Usage: python state_mgr_run.py <COM_PORT>")
        return
    uart_conn = UartConnection(argv[1])
    uart_conn.connect_uart()
    print("UART Successfully Created")
    
    # Get next session time

    # Get all commands for next session, store as an array of names 
    # TODO: Integrate command pipeline to store multiple commands into packets

    # Wait for session

    # Send connection request for session
    try:
        send_conn_request(uart_conn.com_port, 1)
    except IndexError:
        print("Connection request was not successful. Try resetting the board")
        return
    
    # Send each command in sequence, saving the response for each one into the database.
    ping_command = "OBC_PING"
    response = send_command(ping_command, uart_conn.com_port, 1)
    print(response)

    

if __name__ == "__main__":
    main()
