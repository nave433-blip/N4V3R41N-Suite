// src/device.rs
use log::info;

#[derive(Debug, Clone)]
pub struct DeviceInfo {
    pub udid: String,
    pub product_type: String,
    pub chip: String,
    pub ios_version: String,
    pub serial: String,
}

pub fn list_devices() -> Vec<DeviceInfo> {
    info!("Detecting devices via libimobiledevice FFI (simulated)...");
    vec![DeviceInfo {
        udid: "mock-udid-12345".to_string(),
        product_type: "iPhone12,1".to_string(),
        chip: "A13".to_string(),
        ios_version: "16.7.0".to_string(),
        serial: "mock-serial-abc".to_string(),
    }]
}
