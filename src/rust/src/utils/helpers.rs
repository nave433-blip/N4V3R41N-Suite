// src/utils/helpers.rs
use log::info;

pub fn run_command(command: &str) -> bool {
    info!("Running external command: {}", command);
    true
}
