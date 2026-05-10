//! Auto-Spoofing Server for iOS Activation Bypass
//! Integrates HTTPS self-signed certificates and DNS spoofing logic.

use std::{
    collections::HashMap,
    net::{IpAddr, SocketAddr},
};
use tokio::sync::Mutex;
use warp::{Filter, Reply, Rejection};
use rcgen::{CertificateParams, SanType, Certificate};
use rustls::{Certificate as RustlsCertificate, PrivateKey};
use serde::Serialize;
use chrono::Utc;
use sha2::{Sha256, Digest};
use log::info;
use once_cell::sync::Lazy;
use duct::cmd;

#[derive(Debug, Clone, Serialize)]
pub struct ActivationRecord {
    pub udid: String,
    pub model: String,
    pub activation_time: i64,
    pub server_token: String,
}

static ACTIVATION_DB: Lazy<Mutex<HashMap<String, ActivationRecord>>> =
    Lazy::new(|| Mutex::new(HashMap::new()));

pub async fn start_spoof_server(ip: IpAddr, port: u16, use_https: bool) -> Result<(), Box<dyn std::error::Error>> {
    info!("[*] Starting N4V3R41N Auto-Spoof Server on {}:{}", ip, port);

    // DNS Spoofing
    setup_hosts_spoof();

    let addr = SocketAddr::from((ip, port));

    let activation_route = warp::path("activation")
        .and(warp::post())
        .and(warp::body::json())
        .and_then(handle_activation);

    let fmip_route = warp::path("fmipmobile")
        .and(warp::get())
        .and_then(handle_fmip);

    let routes = activation_route
        .or(fmip_route)
        .with(warp::cors().allow_any_origin());

    if use_https {
        let (cert_der, key_der) = generate_cert_pair()?;
        
        info!("🔒 HTTPS server live.");
        warp::serve(routes)
            .tls()
            .cert(&cert_der)
            .key(&key_der)
            .run(addr)
            .await;
    } else {
        info!("🌐 HTTP server live.");
        warp::serve(routes).run(addr).await;
    }

    Ok(())
}

async fn handle_activation(body: serde_json::Value) -> Result<impl Reply, Rejection> {
    let udid = body["UDID"].as_str().unwrap_or("unknown").to_string();
    let model = body["DeviceModel"].as_str().unwrap_or("unknown").to_string();
    
    let token = format!("{:x}", Sha256::digest(format!("{}{}", udid, Utc::now().timestamp()).as_bytes()));
    
    let record = ActivationRecord {
        udid: udid.clone(),
        model,
        activation_time: Utc::now().timestamp(),
        server_token: token.clone(),
    };

    ACTIVATION_DB.lock().await.insert(udid, record.clone());

    Ok(warp::reply::json(&serde_json::json!({
        "response": {
            "activationState": "Activated",
            "isActivated": true,
            "serverToken": token,
            "activationRecord": record
        }
    })))
}

async fn handle_fmip() -> Result<impl Reply, Rejection> {
    Ok(warp::reply::json(&serde_json::json!({
        "response": {
            "status": "success",
            "isFMIEnabled": false,
            "message": "FMI disabled via N4V3R41N"
        }
    })))
}

fn generate_cert_pair() -> Result<(Vec<u8>, Vec<u8>), Box<dyn std::error::Error>> {
    let mut params = CertificateParams::new(vec!["activation.apple.com".to_string()]);
    params.subject_alt_names = vec![SanType::DnsName("activation.apple.com".to_string())];
    let cert = Certificate::from_params(params)?;
    Ok((cert.serialize_der()?, cert.serialize_private_key_der()))
}

fn setup_hosts_spoof() {
    let entries = [
        "127.0.0.1 activation.apple.com",
        "127.0.0.1 setup.icloud.com",
        "127.0.0.1 fmipmobile.icloud.com",
    ];

    for entry in entries {
        let _ = cmd!("sudo", "sh", "-c", &format!("echo '{}' >> /etc/hosts", entry)).run();
    }
}
