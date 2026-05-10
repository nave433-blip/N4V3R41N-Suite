package main

import (
	"flag"
	"fmt"
	"os"

	"github.com/nave433-blip/N4V3R41N-Suite/go/exploits"
	"github.com/nave433-blip/N4V3R41N-Suite/go/server"
	"github.com/nave433-blip/N4V3R41N-Suite/go/ssh"
	"github.com/nave433-blip/N4V3R41N-Suite/go/utils"
)

func main() {
	flag.Usage = func() {
		fmt.Printf("N4V3R41N v7.0 - The Ultimate iOS Exploitation Suite (Go)\n")
		fmt.Printf("Usage: %s <command> [args]\n\n", os.Args[0])
		fmt.Printf("Commands:\n")
		fmt.Printf("  list-devices          List connected iOS devices\n")
		fmt.Printf("  bypass <chip>         Bypass activation lock for chip (e.g., A11)\n")
		fmt.Printf("  jailbreak <chip>     Jailbreak for chip (e.g., A12)\n")
		fmt.Printf("  checkm8              Run Checkm8 exploit (A5–A11)\n")
		fmt.Printf("  gesalt               Start Gesalt activation server\n")
		fmt.Printf("  ssh-sideload <ip> <payload>  Sideload a payload via SSH\n")
	}

	if len(os.Args) < 2 {
		flag.Usage()
		os.Exit(1)
	}

	command := os.Args[1]
	args := os.Args[2:]

	switch command {
	case "list-devices":
		devices, err := utils.ListDevices()
		if err != nil {
			utils.LogError("Failed to list devices: %v", err)
			os.Exit(1)
		}
		utils.PrintDevices(devices)

	case "bypass":
		if len(args) < 1 {
			utils.LogError("Usage: %s bypass <chip>", os.Args[0])
			os.Exit(1)
		}
		// Logic to call bypass...
		fmt.Println("Bypass command initiated for chip:", args[0])

	case "checkm8":
		if !exploits.Checkm8() {
			utils.LogError("Checkm8 exploit failed.")
			os.Exit(1)
		}

	case "gesalt":
		server.StartGesaltServer()

	case "ssh-sideload":
		if len(args) < 2 {
			utils.LogError("Usage: %s ssh-sideload <ip> <payload>", os.Args[0])
			os.Exit(1)
		}
		if !ssh.SSHSideload(args[0], args[1]) {
			utils.LogError("SSH sideload failed.")
			os.Exit(1)
		}

	default:
		utils.LogError("Unknown command: %s", command)
		flag.Usage()
		os.Exit(1)
	}
}
