// src/main.rs
#![allow(dead_code, unused_imports, unused_variables, clippy::needless_lifetimes)]
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
        _ => {
            println!("Use --help for usage.");
        }
    }
}
