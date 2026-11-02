#!/bin/bash

set -e

mkdir -p build

TARGET=t8030

clang -arch arm64 -Os -Wl,-preload -Wl,-segalign,0x10 -Wl,-order_file,symorder.txt -nostdlib -fno-vectorize start.S patch.c tt.c -o build/shellcode_$TARGET.o
vmacho -f build/shellcode_$TARGET.o build/shellcode_$TARGET.bin

echo -n "const " > ../resources/shellcode_$TARGET.h
xxd -i -n shellcode_$TARGET build/shellcode_$TARGET.bin >> ../resources/shellcode_$TARGET.h
