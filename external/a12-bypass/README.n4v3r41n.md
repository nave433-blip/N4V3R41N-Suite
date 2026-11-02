# A12_Tool_OSS (vendored)

**Origin (this copy):** https://github.com/bunnyciaa/A12_Tool_OSS
**Attribution chain:** @rhcp011235 (original "Fully Open Source A12+ Bypass";
original repo DMCA'd) → unfriendliness/A12_Tool_OSS (fork) →
bunnyciaa/A12_Tool_OSS (fork; this vendored copy).
Co-authors credited upstream: @rhcp011235 / @rust_505 / @Matty_Inc.
**License:** MIT License, Copyright (c) 2025 rhcp011235 (see LICENSE in this dir).
**What it is:** Client/server A12+ activation bypass. `server/` is a PHP
activation server (`php -S <ip>:8000 -t public`); `client/` has the
`activator.py` client; `Mac_GUI/` is macOS-only.

**How N4V3R41N uses it:** wrapper/invoke only. The `n4v3r41n-cli a12-bypass`
subcommand (see `src/rust/src/exploits/a12_bypass.rs`) verifies php/python3,
starts the PHP server component, and can run the `activator.py` client
(`--client`). Server runs in the foreground unless `--background` is given.
**No upstream code is copied into Rust files.**

MIT attribution retained via the vendored LICENSE file.
