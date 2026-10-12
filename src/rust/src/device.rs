//! Device detection — real USB enumeration via rusb (libusb).
//!
//! Detects Apple devices in DFU mode (PID 0x1227), Recovery mode
//! (PID 0x1281), and normal mode. For DFU devices the iSerial USB
//! string descriptor carries the BootROM identity string
//! (`CPID:xxxx CPRV:xx ... ECID:xxxxxxxxxxxxxxxx`), which we parse
//! and cross-reference against [`crate::chip_db`].
//!
//! No mocks: if libusb cannot be initialised the scan reports the
//! failure honestly instead of inventing a device.

use log::{info, warn};

/// Apple USB vendor ID.
pub const APPLE_VID: u16 = 0x05AC;
/// DFU mode product ID.
pub const DFU_PID: u16 = 0x1227;
/// Recovery mode product ID.
pub const RECOVERY_PID: u16 = 0x1281;

/// What mode an attached Apple device is in.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DeviceMode {
    Dfu,
    Recovery,
    Normal,
    Unknown,
}

impl DeviceMode {
    fn from_pid(pid: u16) -> Self {
        match pid {
            DFU_PID => DeviceMode::Dfu,
            RECOVERY_PID => DeviceMode::Recovery,
            _ => DeviceMode::Normal,
        }
    }

    pub fn label(self) -> &'static str {
        match self {
            DeviceMode::Dfu => "DFU",
            DeviceMode::Recovery => "Recovery",
            DeviceMode::Normal => "Normal",
            DeviceMode::Unknown => "Unknown",
        }
    }
}

/// One USB-attached Apple device found by the scan.
#[derive(Debug, Clone)]
pub struct DetectedDevice {
    pub bus: u8,
    pub address: u8,
    pub vid: u16,
    pub pid: u16,
    pub mode: DeviceMode,
    /// Raw iSerial string from the USB descriptor (DFU identity string).
    pub serial_string: Option<String>,
    /// CPID parsed out of the DFU serial string, if present.
    pub cpid: Option<u32>,
    /// ECID parsed out of the DFU serial string, if present.
    pub ecid: Option<u64>,
}

impl DetectedDevice {
    /// Human-readable chip name via the SoC database, if we know the CPID.
    pub fn chip_name(&self) -> Option<&'static str> {
        self.cpid.and_then(|c| {
            let n = crate::chip_db::name(c);
            if n == "unknown" {
                None
            } else {
                Some(n)
            }
        })
    }

    pub fn checkm8_vulnerable(&self) -> Option<bool> {
        self.cpid.map(crate::chip_db::is_checkm8_vulnerable)
    }
}

/// Parse the DFU-mode iSerial identity string.
///
/// Example: `CPID:8015 CPRV:11 CPFM:03 SCEP:01 BDID:0A ECID:0000039A2B0E001E IBFL:3C SRTG:[iBoot-6723.41.16]`
/// Returns `(cpid, ecid)`; either may be absent from the string.
pub fn parse_dfu_serial(serial: &str) -> (Option<u32>, Option<u64>) {
    let mut cpid = None;
    let mut ecid = None;
    for token in serial.split_whitespace() {
        let mut parts = token.splitn(2, ':');
        let key = parts.next().unwrap_or("");
        let val = parts.next().unwrap_or("");
        match key {
            "CPID" => cpid = u32::from_str_radix(val, 16).ok(),
            "ECID" => ecid = u64::from_str_radix(val, 16).ok(),
            _ => {}
        }
    }
    (cpid, ecid)
}

/// Scan the USB bus for Apple devices. Real enumeration via rusb.
pub fn scan_usb() -> Result<Vec<DetectedDevice>, String> {
    let devices = rusb::devices().map_err(|e| {
        format!(
            "could not enumerate USB devices (libusb: {e}). \
             On Windows this needs the WinUSB driver via Zadig for DFU devices."
        )
    })?;

    let mut found = Vec::new();
    for device in devices.iter() {
        let desc = match device.device_descriptor() {
            Ok(d) => d,
            Err(_) => continue,
        };
        if desc.vendor_id() != APPLE_VID {
            continue;
        }
        let pid = desc.product_id();
        let mode = DeviceMode::from_pid(pid);

        // Best effort: open the device and read the iSerial string.
        // This can fail (permissions, driver) — we keep the VID/PID row anyway.
        let (serial_string, cpid, ecid) = match device.open() {
            Ok(handle) => {
                let idx = desc.serial_number_string_index();
                match idx {
                    Some(i) => match handle.read_string_descriptor_ascii(i) {
                        Ok(s) => {
                            let (cpid, ecid) = parse_dfu_serial(&s);
                            (Some(s), cpid, ecid)
                        }
                        Err(e) => {
                            warn!(
                                "could not read serial string for {:04x}:{:04x}: {e}",
                                desc.vendor_id(),
                                pid
                            );
                            (None, None, None)
                        }
                    },
                    None => (None, None, None),
                }
            }
            Err(e) => {
                warn!(
                    "could not open USB device {:04x}:{:04x} (bus {} addr {}): {e}",
                    desc.vendor_id(),
                    pid,
                    device.bus_number(),
                    device.address()
                );
                (None, None, None)
            }
        };

        found.push(DetectedDevice {
            bus: device.bus_number(),
            address: device.address(),
            vid: desc.vendor_id(),
            pid,
            mode,
            serial_string,
            cpid,
            ecid,
        });
    }

    info!("USB scan complete: {} Apple device(s)", found.len());
    Ok(found)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_dfu_serial_full() {
        let s = "CPID:8015 CPRV:11 CPFM:03 SCEP:01 BDID:0A ECID:0000039A2B0E001E IBFL:3C SRTG:[iBoot-6723.41.16]";
        let (cpid, ecid) = parse_dfu_serial(s);
        assert_eq!(cpid, Some(0x8015));
        assert_eq!(ecid, Some(0x0000039A2B0E001E));
    }

    #[test]
    fn parse_dfu_serial_a11() {
        let s = "CPID:8015 CPRV:11 CPFM:03 SCEP:01 BDID:0A ECID:0012AB34CD56EF78 IBFL:3C";
        let (cpid, ecid) = parse_dfu_serial(s);
        assert_eq!(cpid, Some(0x8015));
        assert_eq!(ecid, Some(0x0012AB34CD56EF78));
    }

    #[test]
    fn parse_dfu_serial_missing_fields() {
        let (cpid, ecid) = parse_dfu_serial("SRTG:[iBoot-1234]");
        assert_eq!(cpid, None);
        assert_eq!(ecid, None);
    }

    #[test]
    fn parse_dfu_serial_empty() {
        let (cpid, ecid) = parse_dfu_serial("");
        assert_eq!(cpid, None);
        assert_eq!(ecid, None);
    }

    #[test]
    fn mode_from_pid() {
        assert_eq!(DeviceMode::from_pid(0x1227), DeviceMode::Dfu);
        assert_eq!(DeviceMode::from_pid(0x1281), DeviceMode::Recovery);
        assert_eq!(DeviceMode::from_pid(0x12A8), DeviceMode::Normal);
    }
}
