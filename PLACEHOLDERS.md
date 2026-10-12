# PLACEHOLDERS.md — N4V3R41N-Suite

Things that need Evan's hands (logins, installs, paid services, his-only decisions).
Agents build around these and never stall on them.

## Hardware / device testing
- [ ] **Real iOS device testing**: checkm8 DFU exploit, SparseRestore, and bypass paths can only be verified against a physical checkm8-vulnerable device (A5–A11) in DFU mode. No device is attached to this build machine — all device flows are code-complete but hardware-unverified.

## Windows build machine (optional)
- [ ] A real Windows 10/11 machine is the gold standard for testing the Windows port (USB driver behavior via Zadig/WinUSB can't be fully verified cross-compiled). Cross-compiled binaries are provided; see `docs/WINDOWS.md`.

## macOS (for C backend)
- [ ] The C checkm8 backend (`src/rust/exploits/c`) currently compiles on Apple targets only (needs Xcode CLT, Homebrew `libusb`, `openssl@3`, `libimobiledevice`). Porting it to Linux/Windows is future work.

## Credentials / services
- None required. No credentials are used or stored by this project.
