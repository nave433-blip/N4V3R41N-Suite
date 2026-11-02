#!/usr/bin/env python3
"""
Patch MobileGestalt CacheData byte offsets (portable, stdlib only).

Default patches (from libMobileGestalt RE / iPod spoof):
  offset 672 (0x2A0)  VolumeUpButtonCGRect            -> 0x00
  offset 673 (0x2A1)  VolumeUpButtonNormalizedCGRect  -> 0xFE
  offset 3192 (0xC78) HasBaseband (slot 399)          -> 0x00 if currently 1 (leave if already 0)

Usage:
  python3 patch_gestalt_cachedata.py input.plist
  python3 patch_gestalt_cachedata.py input.plist -o output.plist
  python3 patch_gestalt_cachedata.py input.plist --binary
  python3 patch_gestalt_cachedata.py input.plist --xml
  python3 patch_gestalt_cachedata.py input.plist --dry-run
"""

from __future__ import annotations

import argparse
import plistlib
import sys
from pathlib import Path

# CacheData byte offsets -> new value
DEFAULT_PATCHES = {
    672: 0x00,   # VolumeUpButtonCGRect
    673: 0xFE,   # VolumeUpButtonNormalizedCGRect
}

HAS_BASEBAND_OFFSET = 0xC78  # slot 399 * 8


def load_plist(path: Path) -> dict:
    with path.open("rb") as f:
        return plistlib.load(f)


def save_plist(path: Path, data: dict, fmt: str) -> None:
    if fmt == "xml":
        out_fmt = plistlib.FMT_XML
    elif fmt == "binary":
        out_fmt = plistlib.FMT_BINARY
    else:
        # keep same as input sniff
        raw = path.read_bytes() if path.exists() else b""
        out_fmt = plistlib.FMT_BINARY if raw.startswith(b"bplist") else plistlib.FMT_XML
    with path.open("wb") as f:
        plistlib.dump(data, f, fmt=out_fmt)


def sniff_fmt(path: Path) -> str:
    raw = path.read_bytes()
    return "binary" if raw.startswith(b"bplist") else "xml"


def patch_cachedata(
    pl: dict,
    patches: dict[int, int],
) -> list[str]:
    if "CacheData" not in pl:
        raise SystemExit("ERROR: no CacheData key in plist")

    cd = bytearray(pl["CacheData"])
    changes: list[str] = []

    for off, new in sorted(patches.items()):
        if off < 0 or off >= len(cd):
            raise SystemExit(f"ERROR: offset {off} out of range (CacheData len={len(cd)})")
        old = cd[off]
        if old == new:
            changes.append(f"CacheData[{off}] = 0x{old:02X} (already)")
        else:
            cd[off] = new
            changes.append(f"CacheData[{off}] = 0x{old:02X} -> 0x{new:02X}")

    # HasBaseband: only change 1 -> 0; leave if already 0
    off = HAS_BASEBAND_OFFSET
    if off >= len(cd):
        raise SystemExit(f"ERROR: HasBaseband offset {off} out of range (CacheData len={len(cd)})")
    old = cd[off]
    if old == 0:
        changes.append(f"CacheData[{off}] HasBaseband = 0x00 (already 0, left)")
    elif old == 1:
        cd[off] = 0
        changes.append(f"CacheData[{off}] HasBaseband = 0x01 -> 0x00")
    else:
        changes.append(f"CacheData[{off}] HasBaseband = 0x{old:02X} (unexpected, left unchanged)")

    pl["CacheData"] = bytes(cd)
    return changes


def main() -> int:
    ap = argparse.ArgumentParser(description="Patch MobileGestalt CacheData offsets")
    ap.add_argument("input", help="Input com.apple.MobileGestalt.plist (xml or binary)")
    ap.add_argument("-o", "--output", help="Output path (default: overwrite input, or *_patched)")
    ap.add_argument("--inplace", action="store_true", help="Overwrite input file")
    ap.add_argument("--xml", action="store_true", help="Write XML plist")
    ap.add_argument("--binary", action="store_true", help="Write binary plist")
    ap.add_argument(
        "--set",
        metavar="OFF=HEX",
        action="append",
        default=[],
        help="Extra patch, e.g. --set 672=00 (can repeat)",
    )
    ap.add_argument("--dry-run", action="store_true", help="Show changes only, do not write")
    args = ap.parse_args()

    if args.xml and args.binary:
        ap.error("use only one of --xml / --binary")

    inp = Path(args.input).expanduser().resolve()
    if not inp.is_file():
        print(f"ERROR: not found: {inp}", file=sys.stderr)
        return 1

    patches = dict(DEFAULT_PATCHES)
    for item in args.set:
        if "=" not in item:
            ap.error(f"bad --set {item!r}, expected OFF=HEX")
        off_s, val_s = item.split("=", 1)
        off = int(off_s, 0)
        val = int(val_s, 16) if val_s.lower().startswith("0x") else int(val_s, 16)
        if not 0 <= val <= 0xFF:
            ap.error(f"value out of byte range: {item}")
        patches[off] = val

    in_fmt = sniff_fmt(inp)
    pl = load_plist(inp)

    print(f"input:  {inp}")
    print(f"format: {in_fmt}")
    print(f"CacheData length: {len(pl.get('CacheData', b''))}")

    changes = patch_cachedata(pl, patches)
    for line in changes:
        print(f"  {line}")

    if args.dry_run:
        print("dry-run: no file written")
        return 0

    if args.output:
        out = Path(args.output).expanduser().resolve()
    elif args.inplace:
        out = inp
    else:
        out = inp.with_name(inp.stem + "_patched" + inp.suffix)

    if args.xml:
        out_fmt = "xml"
    elif args.binary:
        out_fmt = "binary"
    else:
        out_fmt = in_fmt

    save_plist(out, pl, out_fmt)
    print(f"wrote:  {out} ({out_fmt}, {out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
