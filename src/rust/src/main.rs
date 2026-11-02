// src/main.rs
/**
 * N4V3R41N-Core v9.1.0-ULTRA - Universal Research & Automation Edition
 * Part of the N4V3R41N Suite: The Ultimate Unified iOS Exploit & Bypass Toolset.
 *
 * This component handles low-level USB communication, DFU state management,
 * and executes integrated C/Rust exploits (Checkm8, AI-Chains, Passcode Ext, etc.).
 *
 * Developed by Evan Shipley.
 */
#[macro_use] extern crate log;
#[macro_use] extern crate lazy_static;

use clap::{Arg, Command};
use std::process;

mod device;
mod doctor;
mod exploits;
mod server;
mod ssh;
mod utils;
/// Apple SoC database ported from tr4mpass (chip_db) — CPID lookup +
/// checkm8 exploit parameters. See src/chip_db.rs for attribution.
pub mod chip_db;

use comfy_table::{Cell, Table};

fn print_chip_table(chips: impl Iterator<Item = chip_db::ChipInfo>) {
    let mut table = Table::new();
    table.set_header(vec!["CPID", "Name", "Marketing", "checkm8"]);
    for c in chips {
        table.add_row(vec![
            Cell::new(format!("0x{:04X}", c.cpid)),
            Cell::new(c.name),
            Cell::new(c.marketing),
            Cell::new(if c.checkm8_vulnerable { "yes" } else { "no" }),
        ]);
    }
    println!("{table}");
}

#[tokio::main]
async fn main() {
    utils::logger::init_logger();

    let matches = Command::new("N4V3R41N")
        .version("9.1.0-ULTRA")
        .author("Evan Shipley")
        .about("Native Rust iOS Exploit Suite - Orchestrator")
        .subcommand(Command::new("list-devices").about("List connected Apple USB devices (DFU/Recovery/Normal)"))
        .subcommand(Command::new("doctor").about("Check host environment: USB access, helper tools, platform"))
        .subcommand(Command::new("checkm8").about("checkm8 pre-flight: find DFU device, identify its chip, show exploit parameters"))
        .subcommand(Command::new("chip-db").about("Look up an Apple SoC by CPID, name, or marketing string (e.g. chip-db 0x8947, chip-db A11); no arg lists the table")
            .arg(Arg::new("query").help("CPID in hex (0x8947), chip name (A11), or marketing string"))
            .arg(Arg::new("vulnerable").short('v').long("vulnerable").action(clap::ArgAction::SetTrue).help("List only checkm8-vulnerable chips")))
        .subcommand(Command::new("sparse-restore").about("Run SparseRestore CVE-2024-44258 bypass"))
        .subcommand(Command::new("signal-detect").about("Detect device cellular capabilities"))
        .subcommand(Command::new("repair-all").about("Run deep system repair suite"))
        .subcommand(Command::new("identity-fix").about("Run Path-B identity manipulation"))
        .subcommand(Command::new("purple-mode").about("Enter diagnostic Purple Mode"))
        .subcommand(Command::new("r1nderpest").about("Run R1nderpest kernel exploit (A12–A15)"))
        .subcommand(Command::new("spiderpro").about("Run SpiderPRO activation bypass (A12–A15)"))
        .subcommand(Command::new("mix-bypass").about("Run Mix Bypass hybrid exploit (A12–A15)"))
        .subcommand(Command::new("cloudpass").about("Run CloudPass activation spoofing (A5–A15)"))
        .subcommand(Command::new("bookra1n").about("Run Bookra1n BootROM exploit (A12–A15, theoretical)"))
        .subcommand(Command::new("auto-spoof").about("Start automated HTTPS/DNS activation spoofer"))
        .subcommand(Command::new("passcode-bypass").about("Bypass passcode (A5-A11)"))
        .subcommand(Command::new("brute-force")
            .about("Brute force passcode")
            .arg(Arg::new("digits").required(true).help("Number of digits (4 or 6)")))
        .subcommand(Command::new("fmi-off").about("Disable FMI via SSH file removal"))
        .subcommand(Command::new("account-logout").about("Log out of Apple ID via SSH"))
        .subcommand(Command::new("passcode-ext").about("Extract passcode from rooted device"))
        .subcommand(Command::new("android-host").about("Initiate Android USB Host automation"))
        .subcommand(Command::new("ai-chain").about("Run AI-optimized A12+ kernel chain"))
        .subcommand(Command::new("spyware-intel").about("Run spyware behavioral research and simulation"))
        .subcommand(Command::new("hacktivate")
            .about("Run hacktivator checkm8 iCloud bypass via SSH-over-USB (A9–A11, jailbroken device)")
            .arg(Arg::new("dry-run").long("dry-run").action(clap::ArgAction::SetTrue).help("Print the planned steps without touching the device"))
            .arg(Arg::new("ssh-password").long("ssh-password").default_value("alpine").help("Device root SSH password (default is the public jailbreak default)"))
            .arg(Arg::new("port").long("port").default_value("4444").value_parser(clap::value_parser!(u16)).help("Local port for iproxy forwarding"))
            .arg(Arg::new("device-port").long("device-port").default_value("44").value_parser(clap::value_parser!(u16)).help("Device-side SSH port"))
            .arg(Arg::new("patch").long("patch").help("Local patched mobileactivationd binary (skips download)"))
            .arg(Arg::new("plist").long("plist").help("Local LaunchDaemon plist (skips download)"))
            .arg(Arg::new("patch-url").long("patch-url").help("Override URL for the patched mobileactivationd"))
            .arg(Arg::new("plist-url").long("plist-url").help("Override URL for the LaunchDaemon plist")))
        .subcommand(Command::new("tr4mpass")
            .about("Run vendored tr4mpass iCloud activation lock bypass (external/tr4mpass; wrapper only, no code copied)")
            .arg(Arg::new("dry-run").long("dry-run").action(clap::ArgAction::SetTrue).help("Print what would run without touching the device"))
            .arg(Arg::new("rebuild").long("rebuild").action(clap::ArgAction::SetTrue).help("Force rebuild of the vendored tr4mpass binary"))
            .arg(Arg::new("tr4mpass-dir").long("tr4mpass-dir").help("Override vendored tr4mpass directory"))
            .arg(Arg::new("args").num_args(0..).trailing_var_arg(true).allow_hyphen_values(true).help("Arguments passed through to tr4mpass (after --)")))
        .subcommand(Command::new("sshrd")
            .about("Run vendored SSHRD_Script SSH ramdisk iCloud bypass (external/sshrd; wrapper only, no code copied)")
            .arg(Arg::new("dry-run").long("dry-run").action(clap::ArgAction::SetTrue).help("Print what would run without touching the device"))
            .arg(Arg::new("sshrd-dir").long("sshrd-dir").help("Override vendored sshrd directory"))
            .arg(Arg::new("args").num_args(0..).trailing_var_arg(true).allow_hyphen_values(true).help("Arguments passed through to sshrd.sh (after --)")))
        .subcommand(Command::new("usbliter8")
            .about("Run vendored usbliter8 A12/A13 SecureROM exploit host tool (external/usbliter8; wrapper only)")
            .long_about("Run vendored usbliter8 A12/A13 SecureROM exploit host tool (external/usbliter8; wrapper only, no code copied).\n\nHARDWARE REQUIRED: RP2350 microcontroller board (e.g. Raspberry Pi Pico 2) flashed with usbliter8 firmware, plus a USB-A to Lightning cable (USB-C breaks exploit timing). The device must already be in pwned DFU.")
            .arg(Arg::new("dry-run").long("dry-run").action(clap::ArgAction::SetTrue).help("Print what would run without touching the device"))
            .arg(Arg::new("usbliter8-dir").long("usbliter8-dir").help("Override vendored usbliter8 directory"))
            .arg(Arg::new("args").num_args(0..).trailing_var_arg(true).allow_hyphen_values(true).help("Arguments passed through to usbliter8ctl (after --)")))
        .subcommand(Command::new("hello-sn-bypass")
            .about("Run vendored A12/A13 Hello-screen SN-change bypass (external/hello-sn-bypass; wrapper only)")
            .arg(Arg::new("dry-run").long("dry-run").action(clap::ArgAction::SetTrue).help("Print what would run without touching the device"))
            .arg(Arg::new("hello-sn-dir").long("hello-sn-dir").help("Override vendored hello-sn-bypass directory"))
            .arg(Arg::new("args").num_args(0..).trailing_var_arg(true).allow_hyphen_values(true).help("Arguments passed through to bunny_serial_bypass.py (after --)")))
        .subcommand(Command::new("activation-backup")
            .about("Run vendored BUNNY RAMDISK activation backup/restore (external/activation-backup; wrapper only)")
            .arg(Arg::new("dry-run").long("dry-run").action(clap::ArgAction::SetTrue).help("Print what would run without touching the device"))
            .arg(Arg::new("restore").long("restore").action(clap::ArgAction::SetTrue).help("Run restore instead of backup"))
            .arg(Arg::new("backup-dir").long("backup-dir").help("Override vendored activation-backup directory"))
            .arg(Arg::new("args").num_args(0..).trailing_var_arg(true).allow_hyphen_values(true).help("Arguments passed through (after --)")))
        .subcommand(Command::new("kernel-patchfinder")
            .about("Run vendored arm64e kernel patchfinder (external/kernel-patchfinder; wrapper only)")
            .arg(Arg::new("dry-run").long("dry-run").action(clap::ArgAction::SetTrue).help("Print what would run without touching the device"))
            .arg(Arg::new("patchfinder-dir").long("patchfinder-dir").help("Override vendored kernel-patchfinder directory"))
            .arg(Arg::new("args").num_args(0..).trailing_var_arg(true).allow_hyphen_values(true).help("Arguments passed through to kernel_patchfinder.py (after --)")))
        .get_matches();

    match matches.subcommand() {
        Some(("list-devices", _)) => {
            match device::scan_usb() {
                Ok(devices) => {
                    if devices.is_empty() {
                        println!("No Apple USB devices detected.");
                        println!("Tip: put a device in DFU mode (black screen, 05ac:1227) and re-run.");
                        process::exit(1);
                    }
                    let mut table = Table::new();
                    table.set_header(vec!["Bus", "Addr", "VID:PID", "Mode", "CPID", "Chip", "checkm8"]);
                    for d in &devices {
                        table.add_row(vec![
                            Cell::new(d.bus.to_string()),
                            Cell::new(d.address.to_string()),
                            Cell::new(format!("{:04x}:{:04x}", d.vid, d.pid)),
                            Cell::new(d.mode.label()),
                            Cell::new(d.cpid.map(|c| format!("0x{c:04X}")).unwrap_or_else(|| "-".into())),
                            Cell::new(d.chip_name().unwrap_or("-")),
                            Cell::new(match d.checkm8_vulnerable() {
                                Some(true) => "yes",
                                Some(false) => "no",
                                None => "-",
                            }),
                        ]);
                    }
                    println!("{table}");
                }
                Err(e) => {
                    error!("{e}");
                    process::exit(1);
                }
            }
        }
        Some(("doctor", _)) => {
            doctor::run();
        }
        Some(("checkm8", _)) => {
            process::exit(exploits::checkm8::run_preflight());
        }
        Some(("chip-db", args)) => {
            if args.get_flag("vulnerable") {
                print_chip_table(chip_db::vulnerable_chips().copied());
                return;
            }
            match args.get_one::<String>("query") {
                Some(q) => {
                    // Accept "0x8947" hex, bare "8947", or a name like "A11".
                    let by_cpid = q
                        .trim_start_matches("0x")
                        .trim_start_matches("0X")
                        .chars()
                        .all(|c| c.is_ascii_hexdigit())
                        .then(|| u32::from_str_radix(q.trim_start_matches("0x").trim_start_matches("0X"), 16).ok())
                        .flatten()
                        .and_then(chip_db::lookup);
                    match by_cpid.or_else(|| chip_db::find_by_name(q)) {
                        Some(c) => {
                            println!("CPID 0x{:04X} — {} ({})", c.cpid, c.name, c.marketing);
                            println!("  checkm8 vulnerable: {}", c.checkm8_vulnerable);
                            println!("  large_leak={} overwrite_pad=0x{:x} hole={}", c.config_large_leak, c.config_overwrite_pad, c.config_hole);
                            println!("  insecure_mem_base=0x{:x}", c.insecure_memory_base);
                            println!("  patch_addr=0x{:x} memcpy=0x{:x} aes_crypto_cmd=0x{:x}", c.patch_addr, c.memcpy_addr, c.aes_crypto_cmd);
                        }
                        None => { error!("Unknown chip '{}'. Try 'chip-db' with no args to list the table.", q); process::exit(1); }
                    }
                }
                None => {
                    print_chip_table(chip_db::CHIP_TABLE.iter().copied());
                }
            }
        }
        Some(("sparse-restore", _)) => {
            exploits::sparse_restore::run();
        }
        Some(("signal-detect", _)) => {
            exploits::signal::run();
        }
        Some(("repair-all", _)) => {
            exploits::repair::run_diagnostics();
        }
        Some(("identity-fix", _)) => {
            exploits::path_b::run_identity_fix();
        }
        Some(("purple-mode", _)) => {
            #[cfg(target_vendor = "apple")]
            {
                extern "C" { fn purple_mode_enter(dev: *mut std::ffi::c_void) -> i32; }
                unsafe { purple_mode_enter(std::ptr::null_mut()); }
            }
            #[cfg(not(target_vendor = "apple"))]
            {
                error!("purple-mode requires the native C backend, which is only compiled on macOS builds.");
                process::exit(1);
            }
        }
        Some(("r1nderpest", _)) => {
            #[cfg(target_vendor = "apple")]
            exploits::r1nderpest::run();
            #[cfg(not(target_vendor = "apple"))]
            {
                error!("r1nderpest requires macOS (Mach kernel APIs). Not available on this platform.");
                process::exit(1);
            }
        }
        Some(("spiderpro", _)) => {
            exploits::spiderpro::run();
        }
        Some(("mix-bypass", _)) => {
            exploits::mix_bypass::run();
        }
        Some(("cloudpass", _)) => {
            exploits::cloudpass::run();
        }
        Some(("bookra1n", _)) => {
            exploits::bookra1n::run();
        }
        Some(("auto-spoof", _)) => {
            let _ = server::auto_spoof::start_spoof_server("0.0.0.0".parse().unwrap(), 443, true).await;
        }
        Some(("passcode-bypass", _)) => {
            exploits::passcode::checkm8_passcode_bypass();
        }
        Some(("brute-force", args)) => {
            let digits = args.get_one::<String>("digits").unwrap().parse().unwrap_or(4);
            exploits::passcode::brute_force(digits);
        }
        Some(("fmi-off", _)) => {
            exploits::account::remove_fmi_files();
        }
        Some(("account-logout", _)) => {
            exploits::account::remove_apple_id();
        }
        Some(("passcode-ext", _)) => {
            exploits::passcode_extraction::run_extraction_suite();
        }
        Some(("android-host", _)) => {
            exploits::android_ext::run_android_automation();
        }
        Some(("ai-chain", _)) => {
            exploits::ai_research::run_ai_kernel_chain();
        }
        Some(("spyware-intel", _)) => {
            exploits::spyware_research::run_spyware_analysis();
            exploits::spyware_research::simulate_0click();
        }
        Some(("hacktivate", args)) => {
            process::exit(exploits::hacktivator::run_from_matches(args));
        }
        Some(("tr4mpass", args)) => {
            process::exit(exploits::tr4mpass::run_from_matches(args));
        }
        Some(("sshrd", args)) => {
            process::exit(exploits::sshrd::run_from_matches(args));
        }
        Some(("usbliter8", args)) => {
            process::exit(exploits::usbliter8::run_from_matches(args));
        }
        Some(("hello-sn-bypass", args)) => {
            process::exit(exploits::hello_sn_bypass::run_from_matches(args));
        }
        Some(("activation-backup", args)) => {
            process::exit(exploits::activation_backup::run_from_matches(args));
        }
        Some(("kernel-patchfinder", args)) => {
            process::exit(exploits::kernel_patchfinder::run_from_matches(args));
        }
        _ => {
            println!("Use --help for usage.");
        }
    }
}
