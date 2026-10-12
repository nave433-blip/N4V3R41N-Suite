# N4V3R41N-Suite on Windows

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

- `chip-db` — Apple SoC database (25 chips, CPID lookup, checkm8 flags).
  Pure Rust, fully portable.
- `list-devices`, `doctor`, `info` — device detection paths that don't
  need the native C backend.
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
