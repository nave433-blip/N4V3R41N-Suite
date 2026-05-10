# N4V3R41N: The Ultimate Unified iOS Exploit & Bypass Suite

![Version](https://img.shields.io/badge/version-7.0.0--ULTRA-magenta)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-Unlicense-blue)

**N4V3R41N** (pronounced *Never-Rain*) is a professional-grade, unified toolset designed for iOS security research, jailbreaking, and activation bypass. The **v7.0-ULTRA** edition provides three complete, native implementations in **C**, **Go**, and **Swift**, making it the most versatile suite in the community.

## 🚀 Key Features

*   **Universal Implementation**: Complete rewrites in **C** (Low-level), **Go** (Concurrent), and **Swift** (Native Apple) to ensure compatibility across all research environments.
*   **Cinematic Interactive TUI**: The master Python orchestrator provides a high-fidelity dashboard to control all native cores.
*   **Advanced A12+ Bypass (Download28)**: Native implementations of the sandbox escape vector for iPhone XS through iPhone 16+ hardware.
*   **SparseRestore & Path-C**: Cross-platform support for CVE-2024-44258 and advanced restore logic.
*   **Purple Mode (Diagnostic)**: Native DFU-level diagnostic mode access for A10-A11 chips.
*   **Signal Repair & Preservation**: Intelligent cellular capability preservation logic ported to all language cores.

## 📁 Repository Structure

*   `/src`: Master Python Orchestrator and Cinematic TUI.
*   `/src/rust`: High-performance Rust-C-C++ hybrid core.
*   `/c`: Minimalist, native C implementation (Low-level).
*   `/go`: Concurrent, cross-platform Go implementation.
*   `/swift`: Native Apple Swift implementation (macOS/iOS).
*   `/exploits`: Integrated community binaries.

## 📦 Installation & Setup

### Quick Install
```bash
git clone https://github.com/nave433-blip/N4V3R41N-Suite.git
cd N4V3R41N-Suite
./n4v3r41n doctor  # Auto-install dependencies
```

### Building Cores
- **C**: `cd c && make`
- **Go**: `cd go && go build`
- **Swift**: `cd swift && swift build`

## 📜 Credits & Acknowledgments

N4V3R41N is built upon the incredible work of the iOS security research community. We owe a debt of gratitude to the following researchers and projects:

### Core Exploits & Research
- **axi0mX**: Discovery and implementation of the legendary **checkm8** BootROM exploit.
- **Linus Henze**: For the groundbreaking **Fugu14** and **Fugu18** exploits, and ongoing PPL research.
- **opa334**: Lead developer of the **Dopamine** jailbreak and critical kernel exploit research.
- **Pwn20wnd**: Lead developer of **unc0ver** (Undecimus).
- **Nebula**: For the **XinaA15** project and A12+ research.
- **rhcp011235 & rust_505**: For the initial research and implementation of the **Download28** sandbox escape.

## ⚠️ Disclaimer
This tool is intended for **educational and research purposes only**. The authors are not responsible for any misuse or damage caused by this software. Always backup your device before attempting any low-level system modifications.

---
*Developed by Evan Shipley & The N4V3R41N Team.*
