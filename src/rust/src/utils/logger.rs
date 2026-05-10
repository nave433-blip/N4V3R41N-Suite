// src/utils/logger.rs
use log::{LevelFilter};
use env_logger::Builder;
use std::io::Write;

pub fn init_logger() {
    Builder::new()
        .filter_level(LevelFilter::Info)
        .format(|buf, record| {
            writeln!(buf, "{} [{}] {}",
                     chrono::Local::now().format("%Y-%m-%d %H:%M:%S"),
                     record.level(),
                     record.args())
        })
        .init();
}
