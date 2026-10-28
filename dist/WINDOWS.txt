# N4V3R41N-Suite on Windows

## Dependencies

The Rust core vendors everything it needs — no separate installs for the
CLI itself:

| Dependency | How it's provided |
|---|---|
| Rust crates (clap, tokio, rusb, …) | `cargo` fetches from crates.io on build |
| libusb (for `rusb`) | `libusb1-sys` compiles its own copy when system headers are absent — verified building on a machine without `libusb-dev` |
| WinUSB driver (DFU USB access) | **not vendored** — install via Zadig (see below) |
| `idevice_id` / `irecovery` (optional) | libimobiledevice Windows builds; `doctor` warns if absent |
| C checkm8 backend | macOS only (Xcode CLT + Homebrew `libusb`, `openssl@3`, `libimobiledevice`, `libssh2`, `curl`); skipped on Windows by `build.rs` |

### Zadig / WinUSB (required for DFU mode)

DFU-mode devices (`05ac:1227`) need the WinUSB driver on Windows:

1. Put the device in DFU mode (black screen).
2. Open [Zadig](https://zadig.akeo.ie/), select `Apple Mobile Device (DFU Mode)`.
3. Install the WinUSB driver for it.

Run `n4v3r41n-cli doctor` afterwards to confirm USB enumeration works.

## Install (recommended)

1. Download the Windows zip from the latest GitHub release and extract it.
2. Right-click `install.ps1` → **Run with PowerShell**, or from a terminal in
   that folder:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\install.ps1
   ```
   The installer copies `n4v3r41n-cli.exe` to
   `%LocalAppData%\N4V3R41N\bin`, adds it to your user PATH (no admin
   rights needed), and verifies with `n4v3r41n-cli --version`.
3. Open a **new** terminal and run `n4v3r41n-cli doctor` to check your setup.

For DFU-mode USB access, install the WinUSB driver for the DFU device
with [Zadig](https://zadig.akeo.ie/) (device `05AC:1227`).

## Build

The Rust core (`src/rust/`) cross-compiles from Linux with the
`x86_64-pc-windows-gnu` target:

```bash
rustup target add x86_64-pc-windows-gnu
# install mingw-w64 for the linker, then in ~/.cargo/config.toml:
# [target.x86_64-pc-windows-gnu]
# linker = "x86_64-w64-mingw32-gcc"
cargo build --release --target x86_64-pc-windows-gnu
```

Output: `src/rust/target/x86_64-pc-windows-gnu/release/n4v3r41n-cli.exe`
(PE32+ x86-64 console binary, ~3.7 MB, verified with `file`).

## What works on Windows

- `chip-db` — Apple SoC database (25 chips; CPID / name / marketing lookup,
  `--vulnerable` filter). Pure Rust, fully portable.
- `list-devices` — real USB enumeration via rusb: finds Apple devices in
  DFU (05ac:1227), Recovery, and Normal modes, parses CPID/ECID from the
  DFU serial string, cross-references the chip database.
- `checkm8` — pre-flight workflow: identifies a DFU device's chip and
  prints exact exploit parameters + readiness checklist.
- `doctor` — environment diagnostics (USB stack, helper tools, platform).
- `sparse-restore`, `signal-detect`, `repair-all`, `identity-fix`,
  `purple-mode`, `r1nderpest`, `mix-bypass` — these print an honest
  "requires macOS build" message instead of crashing or pretending.

## Platform-gated (Apple-only, by design)

The following are compiled out on Windows via
`#[cfg(target_vendor = "apple")]` because they depend on macOS-only
primitives:

| Component | Why it's Apple-only |
|---|---|
| `exploits/r1nderpest.rs` | Mach kernel APIs (`mach_task_self`, `vm_read_overwrite`, `vm_write`) |
| C backend (`build.rs` skips it) | Developed against macOS CLT/Homebrew libusb/openssl |
| `sparse_restore` native path | Needs the C backend (`sparse_restore_apply`) |
| `purple_mode_enter` | Needs the C backend |
| `path_b` / `signal` / `repair` native paths | Need the C backend |

On Apple targets the full functionality is compiled in; on other
platforms the CLI stays usable and every gated command explains itself.

## Limitations

- The exe has never been executed on a real Windows machine — smoke test
  needed (see `PLACEHOLDERS.md`).
- USB device access on Windows needs a libusb-compatible driver
  (e.g. via Zadig) for the `rusb`-based paths; untested.
- The Python components (`n4v3r41n.py`, PyQt6 GUI) are not bundled into
  the exe; run them with a Windows Python 3 install.
