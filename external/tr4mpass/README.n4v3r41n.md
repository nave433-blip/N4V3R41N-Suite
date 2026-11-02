# tr4mpass (vendored)

**Origin:** https://github.com/fleshka1711-alt/1 (fork of https://github.com/tr4m0ryp/tr4mpass)
**License:** NONE DECLARED — no LICENSE file, copyright headers, or SPDX
identifiers were found in the vendored tree (checked 2026-11-02).
**What it is:** C implementation of an iCloud activation lock bypass
(supports a wide iOS range per its README).

**How N4V3R41N uses it:** wrapper/invoke only. The `n4v3r41n-cli tr4mpass`
subcommand (see `src/rust/src/exploits/tr4mpass.rs`) locates this directory,
builds it with its own Makefile if the `tr4mpass` binary is missing, and
execs the binary passing CLI args through. **No tr4mpass source code is
copied into Rust files.**

**Note:** because no license is declared, treat this tree as
all-rights-reserved upstream code: do not copy its sources elsewhere.
If the upstream later declares a license, update this note.
