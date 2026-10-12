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

pub fn run() {
    info!("Running environment diagnostics");
    let mut checks = vec![
        Check {
            name: "Platform",
            status: Status::Pass,
            detail: format!("{} / {}", std::env::consts::OS, std::env::consts::ARCH),
        },
        check_libusb(),
        check_tool(
            "idevice_id",
            "install libimobiledevice for normal-mode device info",
        ),
        check_tool(
            "ideviceinfo",
            "install libimobiledevice for normal-mode device info",
        ),
        check_tool(
            "irecovery",
            "install libimobiledevice for recovery-mode communication",
        ),
        check_tool("python3", "needed by some helper scripts"),
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
    if failed {
        std::process::exit(1);
    }
}
