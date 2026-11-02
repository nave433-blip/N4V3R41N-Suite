# usbliter8 (vendored)

**Origin:** https://github.com/bunnyciaa/usbliter8
**License:** NONE DECLARED — no LICENSE file, copyright headers, or SPDX
identifiers were found in the vendored tree (checked 2026-11-02).
**What it is:** Tethered bootrom exploit for Apple A12, S4/S5 & A13 SoCs.
REAL implementation (contrast with the theoretical `bookra1n` path in
N4V3R41N). Host tool `usbliter8ctl` (Python) drives a pwned-DFU device;
RP2350 firmware sources are included for building .uf2 images.

**Hardware requirements (from upstream README + operator notes):**
- RP2350 microcontroller board (e.g. Raspberry Pi Pico 2, Waveshare
  RP2350-USB-A) to deliver the exploit over USB DFU. Without this board
  the usbliter8 paths cannot run.
- USB-A to Lightning cable specifically. USB-C to Lightning cables fail
  the exploit timing constraints. Keep the cable short.

**How N4V3R41N uses it:** wrapper/invoke only. The `n4v3r41n-cli usbliter8`
subcommand (see `src/rust/src/exploits/usbliter8.rs`) locates this directory
and execs `usbliter8ctl` with CLI args passed through.
**No upstream source is copied into Rust files.**

Because no license is declared, treat this tree as all-rights-reserved
upstream code: do not copy its sources elsewhere.
