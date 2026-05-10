// build.rs
extern crate bindgen;
extern crate cc;

use std::env;
use std::path::PathBuf;

fn main() {
    println!("cargo:rerun-if-changed=wrapper.h");
    println!("cargo:rerun-if-changed=exploits/c/checkm8/");

    let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    
    // Bindgen
    let builder = bindgen::Builder::default()
        .header("wrapper.h")
        .clang_arg("-I/usr/local/include")
        .clang_arg("-I/usr/local/opt/openssl@3/include")
        .clang_arg("-I/usr/local/opt/libssh2/include")
        .clang_arg("-I/usr/local/opt/curl/include");

    let bindings = builder.generate().expect("Unable to generate bindings");

    bindings
        .write_to_file(out_path.join("bindings.rs"))
        .expect("Couldn't write bindings!");

    // C Compilation
    let mut build = cc::Build::new();
    let base_c_path = "exploits/c/checkm8";
    
    build.include(base_c_path);
    build.include(format!("{}/activation", base_c_path));
    build.include(format!("{}/bypass", base_c_path));
    build.include(format!("{}/device", base_c_path));
    build.include(format!("{}/util", base_c_path));
    
    build.include("/usr/local/include");
    build.include("/usr/local/opt/openssl@3/include");
    build.include("/usr/local/opt/libusb/include/libusb-1.0");
    build.include("/usr/local/opt/libssh2/include");
    build.include("/usr/local/opt/curl/include");
    
    let c_files = [
        "checkm8.c",
        "checkm8_patch.c",
        "checkm8_payload.c",
        "checkm8_spray.c",
        "checkm8_stages.c",
        "dfu_proto.c",
        "activation/activation.c",
        "activation/cert_extract.c",
        "activation/provision_inject.c",
        "activation/record.c",
        "activation/session_online.c",
        "activation/session.c",
        "activation/signer.c",
        "bypass/afc_utils.c",
        "bypass/bypass.c",
        "bypass/deletescript.c",
        "bypass/path_a_ramdisk_poll.c",
        "bypass/path_a_ramdisk.c",
        "bypass/path_a_ssh_helpers.c",
        "bypass/path_a_ssh.c",
        "bypass/path_a.c",
        "bypass/path_b_identity.c",
        "bypass/path_b.c",
        "bypass/repair.c",
        "bypass/signal.c",
        "bypass/sparse_restore.c",
        "device/chip_db.c",
        "device/device.c",
        "device/usb_dfu.c",
        "util/env_config.c",
        "util/log.c",
        "util/plist_helpers.c",
        "util/usb_helpers.c",
    ];

    for file in &c_files {
        build.file(format!("{}/{}", base_c_path, file));
    }

    build.compile("libn4v3r41n_core_c.a");

    // Linking
    println!("cargo:rustc-link-search=native=/usr/local/lib");
    println!("cargo:rustc-link-search=native=/usr/local/opt/openssl@3/lib");
    println!("cargo:rustc-link-search=native=/usr/local/opt/libusb/lib");
    println!("cargo:rustc-link-search=native=/usr/local/opt/libssh2/lib");
    println!("cargo:rustc-link-search=native=/usr/local/opt/curl/lib");
    
    println!("cargo:rustc-link-lib=dylib=imobiledevice-1.0");
    println!("cargo:rustc-link-lib=dylib=irecovery-1.0");
    println!("cargo:rustc-link-lib=dylib=usbmuxd-2.0");
    println!("cargo:rustc-link-lib=dylib=plist-2.0");
    println!("cargo:rustc-link-lib=dylib=usb-1.0");
    println!("cargo:rustc-link-lib=dylib=crypto");
    println!("cargo:rustc-link-lib=dylib=ssl");
    println!("cargo:rustc-link-lib=dylib=ssh2");
    println!("cargo:rustc-link-lib=dylib=curl");
}
