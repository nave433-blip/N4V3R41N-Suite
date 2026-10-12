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
mod exploits;
mod server;
mod ssh;
mod utils;
/// Apple SoC database ported from tr4mpass (chip_db) — CPID lookup +
/// checkm8 exploit parameters. See src/chip_db.rs for attribution.
pub mod chip_db;

use device::{DeviceInfo, list_devices};

#[tokio::main]
async fn main() {
    utils::logger::init_logger();

    let matches = Command::new("N4V3R41N")
        .version("9.1.0-ULTRA")
        .author("Evan Shipley")
        .about("Native Rust iOS Exploit Suite - Orchestrator")
        .subcommand(Command::new("list-devices").about("List connected iOS devices"))
        .subcommand(Command::new("chip-db").about("Look up an Apple SoC by CPID (e.g. chip-db 0x8947); no arg lists the table")
            .arg(Arg::new("cpid").help("Chip CPID in hex, e.g. 0x8947")))
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
            let devices = device::list_devices();
            if devices.is_empty() {
                error!("No devices detected.");
                process::exit(1);
            }
            for dev in devices {
                println!("{:?}", dev);
            }
        }
        Some(("chip-db", args)) => {
            match args.get_one::<String>("cpid") {
                Some(cpid_str) => {
                    let cpid = u32::from_str_radix(cpid_str.trim_start_matches("0x"), 16)
                        .unwrap_or_else(|_| { error!("Invalid CPID '{}'. Use hex, e.g. 0x8947.", cpid_str); process::exit(1); });
                    match chip_db::lookup(cpid) {
                        Some(c) => {
                            println!("CPID 0x{:04X} — {} ({})", c.cpid, c.name, c.marketing);
                            println!("  checkm8 vulnerable: {}", c.checkm8_vulnerable);
                            println!("  large_leak={} overwrite_pad=0x{:x} hole={}", c.config_large_leak, c.config_overwrite_pad, c.config_hole);
                            println!("  insecure_mem_base=0x{:x}", c.insecure_memory_base);
                        }
                        None => { error!("Unknown CPID 0x{:04X}", cpid); process::exit(1); }
                    }
                }
                None => {
                    println!("{:<8} {:<6} {:<38} {}", "CPID", "Name", "Marketing", "checkm8");
                    for c in chip_db::CHIP_TABLE {
                        println!("0x{:04X}   {:<6} {:<38} {}", c.cpid, c.name, c.marketing, if c.checkm8_vulnerable { "yes" } else { "no" });
                    }
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
