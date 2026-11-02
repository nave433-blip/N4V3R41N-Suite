#!/bin/bash

set -e

BOARDS=(
    waveshare_rp2350_usb_a
    waveshare_rp2350_zero
    pimoroni_tiny2350
    pico2
    # adafruit_feather_rp2040
    # pico
)

rm -rf artifacts
mkdir -p artifacts

for b in "${BOARDS[@]}"
do
    rm -rf build
    echo "building for $b"
    cmake -S . -B build -DPICO_BOARD=$b -DPICO_SDK_PATH=$PICO_SDK_PATH -DPICO_TOOLCHAIN_PATH=$PICO_TOOLCHAIN_PATH
    cmake --build build -j24
    cp build/usbliter8.uf2 artifacts/usbliter8.$b.uf2
done

rm -rf build
