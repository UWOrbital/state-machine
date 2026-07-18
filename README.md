# state-machine
Ground Station State Machine

Currently, the ground station state machine can pull commands for the immediate next session through the GS database (hosted locally or through azure).
Limitations include (as of 7/18/2026)
- Commands with params are NOT supported!
- Can only send one command per packet currently (fixable)
- Can not send more than one conn_request without resetting the board (probably fixable)

# to run
connect obc board through usb
go to Github to see instructions for attaching windows USB to wsl
make sure to have the uv.lock packages downloaded (ask AI if need help w this)
Run `git submodule init`
cd interfaces
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=GS
cmake --build . -j16
navigate to root repo,
run
`PYTHONPATH=src python -m state_mgr_run /dev/ttyACM0`
go to /dev to see which ttyUSB* or ttyACM* you have, try those if this one doesn't work
whenever you stop the program, make sure to replug in the board or press the reset button on the board.
If confused about any of these instructions, ask AI for guidance

# extra
there is also a file that can populate the next session with 3 pings (accesses the DB) for testing (stand in for altering the DB in another way - like the GS frontend/backend) 
to run,
`PYTHONPATH=src python -m database.helpers.populate_next_session`
