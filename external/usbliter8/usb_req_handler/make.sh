#!/bin/bash

set -e

if [[ ! -n $TARGET ]]; then
    echo "no TARGET specified!"; exit;
fi

mkdir -p build

clang -arch arm64 handler.c -Os -Wl,-preload -nostdlib -e _custom_handle_usb_req -Wl,-order_file,symorder.txt -Itargets/$TARGET -o build/handler_$TARGET.o

vmacho -f build/handler_$TARGET.o build/handler_$TARGET.bin

echo -n "const " > ../resources/handler_$TARGET.h
xxd -i -n handler_$TARGET build/handler_$TARGET.bin >> ../resources/handler_$TARGET.h
