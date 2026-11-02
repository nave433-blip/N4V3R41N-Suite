# A12-A13-Hello-Screen-Bypass-with-SN-change-2 (vendored)

**Origin:** https://github.com/bunnyciaa/A12-A13-Hello-Screen-Bypass-with-SN-change-2
**License:** NONE DECLARED — no LICENSE file, copyright headers, or SPDX
identifiers were found in the vendored tree (checked 2026-11-02).
**What it is:** Python toolkit for A12/A13 Hello-screen bypass via
serial-number change technique (FE00 activation record + MobileGestalt
CacheData patch). Requires a pwned-DFU device with SSH ramdisk up.

**Note:** the scripts import a `core.py` from the BUNNY RAMDISK Mac app
bundle, overridable via the `BUNNY_CORE` environment variable. Without it
(or the Mac app), the scripts cannot run — the wrapper reports this.

**How N4V3R41N uses it:** wrapper/invoke only. The
`n4v3r41n-cli hello-sn-bypass` subcommand (see
`src/rust/src/exploits/hello_sn_bypass.rs`) execs
`bunny_serial_bypass.py` with CLI args passed through.
**No upstream source is copied into Rust files.**
