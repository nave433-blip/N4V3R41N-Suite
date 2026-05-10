// src/ssh/mod.rs
use log::info;

pub async fn ssh_sideload(ip: &str, payload: &str) -> bool {
    info!("Sideloading {} to {} via SSH (simulated)...", payload, ip);
    true
}
