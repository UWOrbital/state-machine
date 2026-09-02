package main

import "time"

// How long before a session starts we should have commands packed and ready.
const PreSessionLeadTime = 5 * time.Minute

// How often to re-check for a scheduled session when none is currently pending.
const NoSessionPollInterval = 60 * time.Second

func main() {
	for {

		time.Sleep(NoSessionPollInterval)
	}
}
