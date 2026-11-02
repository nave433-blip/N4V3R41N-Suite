#!/bin/bash

set -e

if [[ ! -n $TARGET ]]; then
    echo "no TARGET specified!"; exit;
fi

mkdir -p build

clang -arch arm64 start.S -Wl,-segalign,0x10 -Wl,-preload -nostdlib -Itargets/$TARGET -o build/shellcode_$TARGET.o

vmacho -f build/shellcode_$TARGET.o build/shellcode_$TARGET.bin

echo -n "const " > ../resources/shellcode_$TARGET.h
xxd -i -n shellcode_$TARGET build/shellcode_$TARGET.bin >> ../resources/shellcode_$TARGET.h
