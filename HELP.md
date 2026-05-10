# N4V3R41N Suite v5.0 - Help & Documentation

Welcome to the **N4V3R41N** Unified iOS Exploit and Bypass Suite.

## NEW in v5.0
- **Cinematic Interactive TUI**: High-fidelity dashboard for device tracking.
- **Advanced A12+ Bypass**: Integrated "download28" sandbox escape for iPhone XS–15+.
- **SparseRestore (CVE-2024-44258)**: Integrated latest low-level restore exploit.
- **Signal Repair**: Advanced cellular capability preservation logic.
- **N4V3R41N Doctor**: Automated dependency check and repair.

## Core Commands

- `n4v3r41n`: Enter the Interactive Cinematic Menu.
- `n4v3r41n list-devices`: Detailed view of connected devices.
- `n4v3r41n bypass-a12`: Run the advanced A12+ bypass directly.
- `n4v3r41n intel`: Display Apple activation server IPs and bypass domains.
- `n4v3r41n spoof`: Automatically redirect Apple activation traffic to your local server.
- `n4v3r41n doctor`: Check for missing tools and auto-install them.
- `n4v3r41n help`: Show this help documentation.

## Network Intelligence & Spoofing
- **Intelligence (Option 8)**: Provides a real-time list of Apple's activation endpoints and known community bypass servers (including Tor onions).
- **DNS Spoof (Option 9)**: Modifies your system's `/etc/hosts` to redirect domains like `activation.apple.com` to `127.0.0.1`. This is required for MITM-style software bypasses.

## Advanced A12+ Bypass (download28)
This vector targets newer devices (iPhone XS and later).
1. Connect device in **Normal Mode**.
2. Select **Option 2** in the menu or run `bypass-a12`.
3. The tool will automatically extract the **SystemGroup GUID**.
4. Follow the on-screen instructions for manual reboots and plist relocation.

## SparseRestore & Signal Fixes
- **Option 3**: Delivers a malicious backup payload to bypass activation checks.
- **Option 4**: Analyzes IMEI/MEID and applies patches to keep signal functional after bypass.

## Troubleshooting

- **USB Issues?** Run `n4v3r41n doctor` to ensure your drivers are correct.
- **GUID Detection failed?** Ensure `pymobiledevice3` is installed and the device is trusted.
- **Permission Denied?** Use `sudo` if USB access is restricted.

## Directory Structure
- `n4v3r41n`: Main v5.0 executable.
- `n4v3r41n-core`: High-performance Rust backend.
- `exploits/`: Integrated third-party binaries.
- `payloads/`: IPA and configuration storage.
