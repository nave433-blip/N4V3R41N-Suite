package utils

import (
	"fmt"
)

type DeviceInfo struct {
	UDID        string
	ProductType string
	Chip        string
	IOSVersion  string
	Serial      string
}

func ListDevices() ([]DeviceInfo, error) {
	// Simulated for now, in real it uses libimobiledevice bindings
	return []DeviceInfo{}, nil
}

func PrintDevices(devices []DeviceInfo) {
	fmt.Println("No devices detected (simulated).")
}

func LogInfo(format string, args ...interface{}) {
	fmt.Printf("[v7-GO] [INFO] "+format+"\n", args...)
}

func LogError(format string, args ...interface{}) {
	fmt.Printf("[v7-GO] [ERROR] "+format+"\n", args...)
}

func LogWarn(format string, args ...interface{}) {
	fmt.Printf("[v7-GO] [WARN] "+format+"\n", args...)
}
