# usbliter8-kernel-patchfinder (vendored)

**Origin:** https://github.com/bunnyciaa/usbliter8-kernel-patchfinder
**License:** MIT License, Copyright (c) 2026 (see LICENSE in this dir).
**What it is:** Pure-Python arm64e kernelcache patchfinder for A12/A13
research (ADRP + BL indexes, string-xref target discovery).
Usage: `kernel_patchfinder.py <kernelcache.raw> [--apply <out>] [-q]`.
Python deps (see requirements.txt): capstone, pyusb, pyserial, pyimg4.

**How N4V3R41N uses it:** wrapper/invoke only. The
`n4v3r41n-cli kernel-patchfinder` subcommand (see
`src/rust/src/exploits/kernel_patchfinder.rs`) execs the script with
CLI args passed through. **No upstream code is copied into Rust.**

MIT attribution retained via the vendored LICENSE file.
