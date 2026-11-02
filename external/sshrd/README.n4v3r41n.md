# SSHRD_Script (vendored)

**Origin:** https://github.com/ItIsGhastly/SSHRD_Script-iCloud-Bypass
**License:** BSD 3-Clause, Copyright (c) 2022 Nathan (see LICENSE in this dir).
**What it is:** Shell-script SSH ramdisk iCloud bypass with vendored
per-platform tool binaries under `Linux/` and `Darwin/`.

**How N4V3R41N uses it:** wrapper/invoke only. The `n4v3r41n-cli sshrd`
subcommand (see `src/rust/src/exploits/sshrd.rs`) locates this directory,
ensures the script and vendored tools are executable, and runs `sshrd.sh`
with CLI args passed through (working directory set to this dir, as the
script uses relative paths). **No SSHRD_Script code is copied into Rust.**

BSD 3-Clause attribution retained via the vendored LICENSE file.
