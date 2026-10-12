# Changelog — N4V3R41N-Suite

All notable changes to this project, committed locally (pushes to GitHub need Evan's explicit word each time).

## [Unreleased] — 2026-10-12 Wave 2
### Added
- `device.rs`: real USB device detection via rusb — replaces the mock
  device with actual enumeration of Apple devices (DFU 05ac:1227,
  Recovery 05ac:1281, Normal), iSerial string reads, CPID/ECID parsing
  from the DFU identity string, and chip-database cross-referencing.
  5 new unit tests.
- `checkm8` CLI subcommand: honest checkm8 pre-flight — finds a DFU
  device, identifies its chip via the SoC database, prints exact exploit
  parameters and a readiness checklist; guides non-DFU devices through
  entering DFU mode. (The BootROM exploit itself still needs the native
  backend or external tooling — stated explicitly.)
- `doctor` CLI subcommand: real environment diagnostics — libusb/USB
  enumeration, `idevice_id`/`ideviceinfo`/`irecovery`/`python3` in PATH,
  platform + native-backend status. Non-zero exit on failure.
- `chip-db`: accepts chip names and marketing strings
  (`chip-db A11`, `chip-db "iPhone X"`), plus `-v/--vulnerable` to list
  only checkm8-vulnerable chips. Table output via comfy-table. 5 new tests.
- `dist/install.ps1`: proper Windows installer — copies the exe to
  `%LocalAppData%\N4V3R41N\bin`, adds it to the user PATH (no admin),
  verifies with `n4v3r41n-cli --version`, prints Zadig/WinUSB guidance.
  Syntax-checked with the real PowerShell parser and functionally tested
  end-to-end under pwsh 7.4.6 (copy + PATH + version check all pass).
  `docs/WINDOWS.md` documents it.
- Dependency audit: every `use` in the tree now resolves to a declared
  crate — removed 9 unused declarations (plist, reqwest, ssh2,
  tokio-rustls, hex, memoffset, aes, anyhow, thiserror). `rusb`'s libusb
  is confirmed to build without system `libusb-dev` headers. External
  tools (Zadig/WinUSB, optional libimobiledevice tools) are covered by
  `doctor`, the installer output, and `docs/WINDOWS.md`. C backend inputs
  (Xcode CLT, Homebrew libusb/openssl@3/libimobiledevice) documented in
  `build.rs` + `docs/WINDOWS.md`; still Apple-only by design.
- Gemini status: still quota-exhausted (free tier, 429, ~16h retry) —
  wave 2 ran as solo senior review, same as wave 1.
- Tests: 19/19 pass (9 baseline + 10 new).

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
