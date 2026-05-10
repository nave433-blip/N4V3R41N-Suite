package ssh

import (
	"github.com/nave433-blip/N4V3R41N-Suite/go/utils"
)

func SSHSideload(ip, payload string) bool {
	utils.LogInfo("Sideloading %s to %s via native Go SSH...", payload, ip)
	return true
}
