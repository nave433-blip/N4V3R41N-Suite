// src/main.rs
/**
 * N4V3R41N-Core v7.0.0-ULTRA - High Performance Exploit Engine
 * Part of the N4V3R41N Suite: The Ultimate Unified iOS Exploit & Bypass Toolset.
 *
 * This component handles low-level USB communication, DFU state management,
 * and executes integrated C/Rust exploits (Checkm8, SparseRestore, R1nderpest, etc.).
 *
 * Developed by Evan Shipley.
 */
#[macro_use] extern crate log;
#[macro_use] extern crate lazy_static;

use clap::{Arg, Command};
use std::process;
use tokio::runtime::Runtime;

mod device;
mod exploits;
mod server;
mod ssh;
mod utils;

use device::{DeviceInfo, list_devices};

fn main() {
    utils::logger::init_logger();

    let matches = Command::new("N4V3R41N")
        .version("7.0.0-ULTRA")
        .author("Evan Shipley")
        .about("Native Rust iOS Exploit Suite - Orchestrator")
        .subcommand(Command::new("list-devices").about("List connected iOS devices"))
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
            extern "C" { fn purple_mode_enter(dev: *mut std::ffi::c_void) -> i32; }
            unsafe { purple_mode_enter(std::ptr::null_mut()); }
        }
        Some(("r1nderpest", _)) => {
            exploits::r1nderpest::run();
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
        _ => {
            println!("Use --help for usage.");
        }
    }
}
