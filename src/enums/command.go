package enums

type CommandStatus int

const (
	CommandPending CommandStatus = iota
	CommandScheduled
	CommandOngoing
	Cancelled
	Failed
	CommandCompleted
	CommandEnumError
)

var commandStatusStrs = [...]string{
	"PENDING",
	"SCHEDULED",
	"ONGOING",
	"CANCELLED",
	"FAILED",
	"COMPLETED",
	"ENUM_ERROR",
}

var commandStatusMap = make(map[string]CommandStatus)

func init() {
	for i, str := range commandStatusStrs {
		commandStatusMap[str] = CommandStatus(i)
	}
}

func (cs CommandStatus) String() string {
	if cs < 0 || int(cs) >= len(sessionStatusStrs) {
		cs = CommandEnumError
	}
	return commandStatusStrs[cs]
}

func ParseCommandStatus(str string) CommandStatus {
	cs, ok := commandStatusMap[str]
	if !ok {
		return CommandEnumError
	}
	return cs
}
