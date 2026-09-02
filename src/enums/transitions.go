package enums

type TransitionState int

const (
	// TODO: rename / clarify the specific transition states
	Error TransitionState = iota

	// UPLINK TRANSITION STATES
	BeginUplink
	ConnectionEstablished
	AckReceived

	// UPLINK / DOWNLINK TRANSITION STATES
	UplinkFinished
	DownlinkingFinished

	// DISCONNECT TRANSITION STATES
	Disconnecting
	DisconnectCMDReceived
	DisconnectComplete

	// EMERGENCY TRANSITION STATES
	EnterEmergency
	EmergencyInitiated
	ConnectionReceived
	ConnectionAckSent
	EmergencyUplinkFinished
	NoTransitionTriggered // NOT USED IN STATE MACHINE
)

var transitionStateStrs = [...]string{
	// TODO: rename / clarify the specific transition states
	"ERROR",

	// UPLINK TRANSITION STATES
	"BEGIN_UPLINK",
	"CONNECTION_ESTABLISHED",
	"ACK_RECEIVED",

	// UPLINK / DOWNLINK TRANSITION STATES
	"UPLINK_FINISHED",
	"DOWNLINKING_FINISHED",

	// DISCONNECT TRANSITION STATES
	"DISCONNECTING",
	"DISCONNECT_CMD_RECEIVED",
	"DISCONNECT_COMPLETE",

	// EMERGENCY TRANSITION STATES
	"ENTER_EMERGENCY",
	"EMERGENCY_INITIATED",
	"CONNECTION_RECEIVED",
	"CONNECTION_ACK_SENT",
	"EMERGENCY_UPLINK_FINISHED",
	"NO_TRANSITION_TRIGGERED", // NOT USED IN STATE MACHINE
}

var transitionStateMap = make(map[string]TransitionState)

func init() {
	for i, str := range machineStateStrs {
		transitionStateMap[str] = TransitionState(i)
	}
}

func (ts TransitionState) String() string {
	if ts < 0 || int(ts) >= len(machineStateStrs) {
		ts = Error
	}
	return machineStateStrs[ts]
}

func ParseTransitionState(str string) TransitionState {
	ts, ok := transitionStateMap[str]
	if !ok {
		return Error
	}
	return ts
}
