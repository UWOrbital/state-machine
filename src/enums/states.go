package enums

type MachineState int

const (
	// UPLINK STATES
	Disconnected MachineState = iota
	AttemptingConnection
	AwaitingAck
	Uplinking
	Downlinking

	// DISCONNECT STATES
	AwaitingDisconnect
	SendDisconnectAck

	// EMERGENCY STATES
	EnteringEmergency
	AwaitingConnection
	SendConnectionAck
	EmergencyUplink
	ServerSideError
)

var machineStateStrs = [...]string{
	// UPLINK STATES
	"DISCONNECTED",
	"ATTEMPTING_CONNECTION",
	"AWAITING_ACK",
	"UPLINKING",
	"DOWNLINKING",

	// DISCONNECT STATES
	"AWAITING_DISCONNECT",
	"SEND_DISCONNECT_ACK",

	// EMERGENCY STATES
	"ENTERING_EMERGENCY",
	"AWAITING_CONNECTION",
	"SEND_CONNECTION_ACK",
	"EMERGENCY_UPLINK",
	"SERVER_SIDE_ERROR",
}

var machineStateMap = make(map[string]MachineState)

func init() {
	for i, str := range machineStateStrs {
		machineStateMap[str] = MachineState(i)
	}
}

func (ms MachineState) String() string {
	if ms < 0 || int(ms) >= len(machineStateStrs) {
		ms = ServerSideError
	}
	return machineStateStrs[ms]
}

func ParseMachineState(str string) MachineState {
	ms, ok := machineStateMap[str]
	if !ok {
		return ServerSideError
	}
	return ms
}
