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
        _ => {
            println!("Use --help for usage.");
        }
    }
}
