#!/usr/bin/env python3
"""
upgrade.py - simple repo upgrade helper for N4V3R41N-Suite

This script performs a safe local "upgrade" workflow:
 - confirms repository is a git repo and pulls latest from origin
 - installs Python dependencies from common requirements files if present
 - updates Rust/Cargo dependencies if a Cargo.toml is present
 - prints actionable next steps

Usage: python3 scripts/upgrade.py
"""

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIREMENTS = [
    ROOT / "requirements.txt",
    ROOT / "requirements_render.txt",
]


def run(cmd, cwd=ROOT, check=False):
    try:
        print("$ ", " ".join(cmd))
        r = subprocess.run(cmd, cwd=cwd, text=True)
        if check and r.returncode != 0:
            raise SystemExit(r.returncode)
        return r.returncode
    except FileNotFoundError:
        print(f"Command not found: {cmd[0]}")
        return 127


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def upgrade_git():
    if not is_git_repo(ROOT):
        print("Not a git repository. Skipping git pull.")
        return

    # Try to fetch & fast-forward pull
    print("[git] Fetching updates from origin...")
    rc = run(["git", "fetch", "--all"], check=False)
    if rc != 0:
        print("[git] fetch failed, aborting git upgrade step.")
        return

    # Determine current branch
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        branch = "master"

    print(f"[git] Pulling latest for branch: {branch}")
    run(["git", "pull", "--ff-only", "origin", branch], check=False)
    print("[git] pull complete.")


def upgrade_python_deps():
    python = sys.executable or "python3"
    for req in REQUIREMENTS:
        if req.exists():
            print(f"[pip] Installing dependencies from {req}")
            run([python, "-m", "pip", "install", "-r", str(req)], check=False)


def upgrade_cargo():
    # update Rust dependencies if Cargo.toml exists anywhere (repo root or src)
    cargo_toml = list(ROOT.glob("**/Cargo.toml"))
    if not cargo_toml:
        return
    print("[cargo] Found Cargo.toml. Running `cargo update` in each crate folder.")
    for ct in cargo_toml:
        crate_dir = ct.parent
        print(f"[cargo] Updating in {crate_dir}")
        rc = run(["cargo", "update"], cwd=crate_dir, check=False)
        if rc != 0:
            print(f"[cargo] cargo update failed in {crate_dir} (rc={rc}).")


def main():
    print("N4V3R41N Upgrade Helper\n")
    upgrade_git()
    upgrade_python_deps()
    upgrade_cargo()

    print("\nUpgrade complete. Recommended next steps:")
    print(" - Review git status: git status")
    print(" - Run any build commands you normally use (e.g., ./build.sh, cargo build --release)")
    print(" - Restart the TUI: ./n4v3r41n")

if __name__ == '__main__':
    main()
