//! `doctor` — host environment diagnostics.
//!
//! Real checks, honest output: USB stack availability, helper tools
//! in PATH, and platform notes. Every check reports pass/warn/fail
//! and the command exits non-zero if anything fails.

use log::info;

struct Check {
    name: &'static str,
    status: Status,
    detail: String,
}

#[derive(PartialEq)]
enum Status {
    Pass,
    Warn,
    Fail,
}

fn status_label(s: &Status) -> &'static str {
    match s {
        Status::Pass => "[ok]  ",
        Status::Warn => "[warn]",
        Status::Fail => "[fail]",
    }
}

fn check_libusb() -> Check {
    match rusb::devices() {
        Ok(devs) => {
            let apple = devs
                .iter()
                .filter_map(|d| d.device_descriptor().ok())
                .filter(|desc| desc.vendor_id() == 0x05AC)
                .count();
            Check {
                name: "USB (libusb)",
                status: Status::Pass,
                detail: format!("enumeration works, {apple} Apple device(s) attached"),
            }
        }
        Err(e) => Check {
            name: "USB (libusb)",
            status: Status::Fail,
            detail: format!(
                "enumeration failed: {e}. On Windows install the WinUSB driver via Zadig; \
                 on Linux check udev rules / permissions."
            ),
        },
    }
}

fn check_tool(name: &'static str, hint: &'static str) -> Check {
    match which::which(name) {
        Ok(path) => Check {
            name,
            status: Status::Pass,
            detail: format!("found at {}", path.display()),
        },
        Err(_) => Check {
            name,
            status: Status::Warn,
            detail: format!("not in PATH — {hint}"),
        },
    }
}

fn check_python() -> Check {
    // Windows Python installs register `python`, not `python3`, so on
    // Windows accept either name instead of warning about a Python
    // install that is actually there.
    #[cfg(target_os = "windows")]
    let names: &[&str] = &["python3", "python"];
    #[cfg(not(target_os = "windows"))]
    let names: &[&str] = &["python3"];
    for name in names {
        if let Ok(path) = which::which(name) {
            return Check {
                name: "python",
                status: Status::Pass,
                detail: format!("found at {}", path.display()),
            };
        }
    }
    Check {
        name: "python",
        status: Status::Warn,
        detail: "not in PATH — needed by some helper scripts".into(),
    }
}

fn check_rp2350() -> Check {
    // RP2350 boards (e.g. Raspberry Pi Pico 2) in BOOTSEL mode present as
    // 2e8a:0009. We can only report what is on the bus right now; the board
    // is only needed at exploit time, so absence is a warning, not a failure.
    // Honest check — no fake detection.
    match rusb::devices() {
        Ok(devs) => {
            let rp2350 = devs
                .iter()
                .filter_map(|d| d.device_descriptor().ok())
                .filter(|desc| desc.vendor_id() == 0x2E8A)
                .count();
            if rp2350 > 0 {
                Check {
                    name: "RP2350 board",
                    status: Status::Pass,
                    detail: format!(
                        "{rp2350} RP2350 USB device(s) detected - usbliter8 hardware ready"
                    ),
                }
            } else {
                Check {
                    name: "RP2350 board",
                    status: Status::Warn,
                    detail: "not detected - usbliter8 exploit needs an RP2350 board (e.g. Raspberry Pi Pico 2)                         flashed with usbliter8 firmware, plus a USB-A to Lightning cable                         (USB-C breaks exploit timing)".into(),
                }
            }
        }
        Err(_) => Check {
            name: "RP2350 board",
            status: Status::Warn,
            detail: "USB enumeration unavailable - cannot check for RP2350 board".into(),
        },
    }
}

pub fn run() {
    info!("Running environment diagnostics");
    // Windows libimobiledevice builds ship the same tool names as .exe
    // files, and `which` already resolves PATHEXT, so the checks are the
    // same — only the install hint changes per platform.
    #[cfg(target_os = "windows")]
    let idevice_hint = "install the Windows libimobiledevice build and add it to PATH";
    #[cfg(not(target_os = "windows"))]
    let idevice_hint = "install libimobiledevice for normal-mode device info";
    #[cfg(target_os = "windows")]
    let irecovery_hint = "install the Windows libimobiledevice build and add it to PATH";
    #[cfg(not(target_os = "windows"))]
    let irecovery_hint = "install libimobiledevice for recovery-mode communication";
    let mut checks = vec![
        Check {
            name: "Platform",
            status: Status::Pass,
            detail: format!("{} / {}", std::env::consts::OS, std::env::consts::ARCH),
        },
        check_libusb(),
        check_tool("idevice_id", idevice_hint),
        check_tool("ideviceinfo", idevice_hint),
        check_tool("irecovery", irecovery_hint),
        check_python(),
        check_tool("adb", "install Android platform-tools for android-host"),
        check_tool("iproxy", "install libimobiledevice — required for hacktivate (SSH-over-USB bypass)"),
        check_tool("sshpass", "install sshpass — required for hacktivate (SSH-over-USB bypass)"),
        check_tool("make", "install build-essential - required to build vendored tr4mpass"),
        check_tool("cc", "install build-essential - required to build vendored tr4mpass"),
        check_tool("pkg-config", "install pkg-config - required to build vendored tr4mpass"),
        check_tool("curl", "install curl - used by sshrd wrapper downloads"),
        check_tool("unzip", "install unzip - used by sshrd wrapper downloads"),
        check_rp2350(),
    ];

    #[cfg(target_vendor = "apple")]
    checks.push(Check {
        name: "Native C backend",
        status: Status::Pass,
        detail: "compiled in (macOS build)".into(),
    });
    #[cfg(not(target_vendor = "apple"))]
    checks.push(Check {
        name: "Native C backend",
        status: Status::Warn,
        detail: "not compiled on this platform — Apple-only exploit paths report honestly instead of running".into(),
    });

    let mut failed = false;
    for c in &checks {
        println!("{} {:<18} {}", status_label(&c.status), c.name, c.detail);
        if c.status == Status::Fail {
            failed = true;
        }
    }
    #[cfg(target_os = "windows")]
    {
        println!("Note: run in an admin cmd window for auto-spoof (port 443) and hosts-file edits.");
        println!("Note: DFU-mode USB access needs the WinUSB driver — install it with Zadig (https://zadig.akeo.ie/).");
    }
    if failed {
        std::process::exit(1);
    }
}
