from __future__ import annotations

from serial import Serial, SerialException

class UartConnection:
    """Non-interactive UART interface for the MCU board."""
    def __init__(
        self,
        com_port: str,
        baud_rate: int = 115200,
        timeout: float = 1.0,
    ) -> None:
        self.com_port = com_port
        self.baud_rate = baud_rate
        self.timeout = timeout

        self.serial: Serial | None = None
        self.connection_request_sent = False
    
    def connect_uart(self) -> None:
        """Open the UART port and verify that it is usable."""

        if self.serial is not None and self.serial.is_open:
            print(f"UART already connected on {self.serial.name}")
            return

        try:
            self.serial = Serial(
                port=self.com_port,
                baudrate=self.baud_rate,
                timeout=self.timeout,
                write_timeout=self.timeout,
            )

            print(f"UART connected on {self.serial.name}")

        except SerialException as error:
            self.serial = None
            raise RuntimeError(
                f"Could not open UART port {self.com_port}: {error}"
            ) from error

    def disconnect_uart(self) -> None:
        """Close the UART port."""

        if self.serial is not None and self.serial.is_open:
            self.serial.close()
            print(f"UART disconnected from {self.com_port}")

        self.serial = None
        self.connection_request_sent = False

    @property
    def is_connected(self):
        return (
            self.serial is not None
            and self.serial.is_open
        )
