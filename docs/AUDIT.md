# N4V3R41N-Suite — Engineering Audit (2026-10-12)

**Repo:** `nave433-blip/N4V3R41N-Suite`
**Domain:** iOS security research / jailbreak / activation-bypass tooling (research & educational use).
**Components:** Python TUI (`n4v3r41n.py`), Rust core (`src/rust` → `n4v3r41n-core`), C checkm8 backend (`src/rust/exploits/c`), PyQt6 GUI + Python cloudpass (`src/python`), helper scripts (`scripts/upgrade.py`), docs.

## What is real
- Python TUI framework (rich-based menu, argparse CLI) — real, but has bugs (see below).
- Rust CLI skeleton: 22 subcommands wired in `main.rs` — real dispatch.
- C backend (~7,800 lines: checkm8, DFU/USB, activation, bypass paths, signal, sparse_restore) — structured, plausible; unverified against hardware.
- warp-based activation HTTP servers (spiderpro, cloudpass, auto_spoof) — real HTTP servers.
- `scripts/upgrade.py` — functional helper.
- `data/servers.json` — static intel data.

## Gap list (claimed vs actual)

### Build / portability — CRITICAL
1. **Rust core does not build on Linux.** `objc`/`objc-foundation` are Apple-only deps, and they are **unused** in code (dead deps). Build fails with E0455.
2. **`build.rs` is macOS-only**: `-mmacosx-version-min` flags, `/usr/local/opt/*` Homebrew include paths, links mac-only dylibs (`imobiledevice-1.0`, `irecovery-1.0`). Fails on Linux/Windows.
3. **bindgen is unconditional** but its output (`bindings.rs`) is never `include!`d — pure build-time failure risk (needs libclang).
4. **`r1nderpest.rs` uses Mach-only APIs** (`mach_task_self`, `vm_write`) — will not compile on Linux/Windows.
5. **Checked-in binaries are macOS Mach-O** (`n4v3r41n` 47 MB, `n4v3r41n-core` 3.5 MB). Useless on Linux/Windows; 47 MB blob in git.
6. No Windows support anywhere (no targets, no docs).

### Python TUI (`n4v3r41n.py`)
7. **Crashes on startup**: `from fastapi import ...` (line ~24) — fastapi is not a dependency and is never used. `ModuleNotFoundError` on any machine without fastapi.
8. `rich` is required but there is no `requirements.txt`.
9. `console = Console(...)` initialized twice; `main_menu()` called twice at the end (dead second call; recursion instead of loop → eventual `RecursionError` on long sessions).
10. `core_command()` joins multi-arg commands into one string passed as a single argv element — breaks any subcommand needing real args.
11. README claims `list-devices` CLI command — not implemented in Python (only in Rust core).
12. `os.system('clear')` — Windows needs `cls` (partially handled via os.name check already).

### Honesty gaps (print-and-claim stubs)
13. `device::list_devices()` returns a **hardcoded mock device** ("mock-udid-12345"). Device detection is fake.
14. `exploits::checkm8::run()` — logs "Running Checkm8 (FFI simulated)...", returns true. Fake.
15. `exploits::ai_research` — fake "AI-Optimized kernel chain" that logs success stages. Fake.
16. `server::gesalt`, `server::c2` — log "starting (simulated)", do nothing. Fake.
17. `ssh::ssh_sideload` — logs, returns true. Fake.
18. `spiderpro::run()`, `cloudpass::start_dns_spoofing()` — log "(simulated)". Partially real servers underneath.
19. `spyware_research`, `pegasus_zero_click`, `ios_18_6_2`, `ios_26_2` modules — research-note stubs.
20. `passcode_extraction::dump_sep_passcode_hash` — "Simulating septool dump". Fake.

### Missing / incomplete
21. No test suite at all (Rust or Python).
22. `data/servers.json` and `src/data/servers.json` are duplicated.
23. GUI (`n4v3r41n_gui.py`) is demo-grade: hardcoded localhost exploit, no real wiring to core.
24. `offline_cloudpass.py` needs `requests` + `ratelimit`, undocumented; single hardcoded exploit entry.
25. No `doctor` implementation details beyond shelling to brew (macOS-only logic).

## Competitor R&D (2026-10-12)
| Tool | License | Killer features relevant here |
|---|---|---|
| palera1n | open source | checkm8 DFU flow, pongoOS pre-boot env, rootless/rootful, Linux+macOS CLI, palen1x (Windows via USB boot) |
| checkra1n | proprietary free | checkm8 semi-tethered JB iOS 12–14; **no Windows port ever shipped** — gap we can fill |
| pymobiledevice3 | **GPL-3.0 — flagged, do not copy** | pure-Python usbmux/lockdown/AFC/syslog/recovery/DFU, cross-platform incl. Windows; recreate concepts clean-room only |
| libimobiledevice | **LGPL — flagged, do not copy** | device info query, AFC, activation, backup/restore concepts |
| axi0mX ipwndfu | open (check) | checkm8 USB/DFU exploit reference implementation |

**Adoption plan:** clean-room recreate (no copied code): real USB DFU/recovery device enumeration via rusb; usbmuxd-socket device discovery where available; guided DFU-entry flow (palera1n-style); honest research-lab modules; Windows cross-compile + Zadig/WinUSB docs.

## Build plan (in progress)
1. ✅ Audit docs (this file), CHANGELOG, PROGRESS, PLACEHOLDERS.
2. Cargo: drop dead Apple-only deps, remove bindgen, cfg-gate Mach/C code, `cargo build` green on Linux.
3. Real USB device detection via rusb (VID 0x05AC PID map) replacing the mock.
4. Python TUI repair + requirements.txt.
5. Activation-server hardening + tests.
6. Doctor module (real checks).
7. Honest research-lab conversion for fake exploit modules.
8. Windows cross-compile + docs.
9. GUI wiring improvements.
