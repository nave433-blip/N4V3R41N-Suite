# N4V3R41N: The Ultimate Unified iOS Exploit & Bypass Suite

![Version](https://img.shields.io/badge/version-5.0.0-cyan)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-Unlicense-blue)

**N4V3R41N** (pronounced *Never-Rain*) is a professional-grade, unified toolset designed for iOS security research, jailbreaking, and activation bypass. It bridges the gap between legacy A5 devices and the latest A16+ hardware by consolidating industry-leading exploit vectors into a single, cinematic CLI experience.

## 🚀 Key Features

*   **Cinematic Interactive TUI**: A high-fidelity, hacker-style dashboard for real-time device diagnostics and command execution.
*   **Advanced A12+ Bypass (Download28)**: Integrated sandbox escape vector for iPhone XS through iPhone 15+ models, featuring automated GUID extraction.
*   **SparseRestore Integration**: Leverages CVE-2024-44258 to deliver malicious backup payloads via `MobileBackup2`.
*   **Signal Repair & Preservation**: Intelligent cellular capability classification (GSM/MEID/Dual) and baseband patching to maintain signal post-bypass.
*   **Native Rust Core**: A high-performance Rust-based orchestrator (`n4v3r41n-core`) for low-level USB and DFU operations.
*   **N4V3R41N Doctor**: Automated system integrity check and dependency repair module.
*   **Full Auto Mode**: Intelligent hardware detection that automatically chains the most stable exploit for your specific device.

## 🛠 Integrated Tools

N4V3R41N acts as a master wrapper for the most powerful tools in the community:
- **Exploits**: Checkra1n, Palera1n, XinaA15, Dopamine, Fugu14/18.
- **Engines**: Tr4mPass, iRecovery, Gaster, PongoOS.
- **Research**: Metasploit Framework integration and local Gesalt/C2 servers.

## 📦 Installation & Setup

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Homebrew (macOS)
- libimobiledevice, libirecovery, libusb, libplist

### Quick Install
```bash
git clone https://github.com/nave433-blip/N4V3R41N-Suite.git
cd N4V3R41N-Suite
./n4v3r41n doctor  # This will auto-install missing dependencies
```

## 📖 Usage

Run the main suite to enter the interactive menu:
```bash
./n4v3r41n
```

### Core Commands
- `list-devices`: Detailed view of connected iOS hardware.
- `bypass-a12`: Trigger the advanced A12+ software bypass.
- `jailbreak`: Automates the jailbreak process based on detected chip.
- `help`: Access the full internal documentation.

## ⚠️ Disclaimer
This tool is intended for **educational and research purposes only**. The authors are not responsible for any misuse or damage caused by this software. Always backup your device before attempting any low-level system modifications.

---
*Developed by Evan Shipley & The N4V3R41N Team.*
