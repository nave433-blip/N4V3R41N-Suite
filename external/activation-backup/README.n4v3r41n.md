# BUNNY-RAMDISK-Backup-Restore (vendored)

**Origin:** https://github.com/bunnyciaa/BUNNY-RAMDISK-Backup-Restore
**License:** NONE DECLARED — no LICENSE file, copyright headers, or SPDX
identifiers were found in the vendored tree (checked 2026-11-02).
**What it is:** Standalone Python CLI for A12/A13 activation backup &
restore over the SSH ramdisk (`bunny_backup.py` pulls activation files
to a backup zip; `bunny_restore.py` restores and reboots).

**Note:** like its sibling toolkit, the scripts import a `core.py` from
the BUNNY RAMDISK Mac app bundle, overridable via `BUNNY_CORE`.

**How N4V3R41N uses it:** wrapper/invoke only. The
`n4v3r41n-cli activation-backup` subcommand (see
`src/rust/src/exploits/activation_backup.rs`) execs `bunny_backup.py`
by default (`--restore` selects `bunny_restore.py`), args passed through.
**No upstream source is copied into Rust files.**
