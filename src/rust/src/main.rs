// src/main.rs
/**
 * N4V3R41N-Core v5.0.0 - High Performance Exploit Engine
 * Part of the N4V3R41N Suite: The Ultimate Unified iOS Exploit & Bypass Toolset.
 *
 * This component handles low-level USB communication, DFU state management,
 * and executes integrated C exploits (Checkm8, SparseRestore, etc.).
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
        .version("5.0.0")
        .author("Evan Shipley")
        .about("Native Rust iOS Exploit Suite - Orchestrator")
        .subcommand(Command::new("list-devices").about("List connected iOS devices"))
        .subcommand(Command::new("sparse-restore").about("Run SparseRestore CVE-2024-44258 bypass"))
        .subcommand(Command::new("signal-detect").about("Detect device cellular capabilities"))
        .subcommand(Command::new("repair-all").about("Run deep system repair suite"))
        .subcommand(Command::new("identity-fix").about("Run Path-B identity manipulation"))
        .subcommand(Command::new("purple-mode").about("Enter diagnostic Purple Mode"))
        .get_matches();

    match matches.subcommand() {
        Some(("list-devices", _)) => {
            let devices = device::list_devices();
            if devices.is_empty() {
                error!("No devices detected.");
                process::exit(1);
            }
            // For now, simple println output
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
        _ => {
            println!("Use --help for usage.");
        }
    }
}
