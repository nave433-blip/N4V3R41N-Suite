# Changelog — N4V3R41N-Suite

All notable changes to this project, committed locally (pushes to GitHub need Evan's explicit word each time).

## [Unreleased] — 2026-10-12 workstream
### Added
- `docs/AUDIT.md`: full engineering audit (claimed-vs-actual gap list, competitor R&D).
- `PLACEHOLDERS.md`: items needing Evan's hands.
- `CHANGELOG.md` / `PROGRESS.md`: running workstream notes.

### Added (Windows-port workstream)
- `src/rust/src/chip_db.rs`: Apple SoC database ported from tr4mpass
  (`include/device/chip_db_table*.h`, values originally from gaster) —
  25 chips with CPID lookup, checkm8-vulnerability flags, and exploit
  config parameters; 4 unit tests.
- `chip-db` CLI subcommand: `n4v3r41n-cli chip-db [CPID]` lists the table
  or looks up one chip.
- Windows port: `cargo build --release --target x86_64-pc-windows-gnu`
  produces a verified PE32+ `n4v3r41n-cli.exe` (~3.7 MB).
- `docs/WINDOWS.md`: build instructions, what works, platform gates.

### Fixed
- `src/rust` now compiles on non-Apple targets: gated `r1nderpest`
  (Mach-only APIs), `sparse_restore` native path, and `purple-mode` FFI
  behind `#[cfg(target_vendor = "apple")]` with honest fallbacks —
  matching the existing pattern in `path_b`/`signal`/`repair`.
