#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    printf("N4V3R41N v7.0 - The Ultimate iOS Exploitation Suite (C)\n");
    if (argc < 2) {
        printf("Usage: %s <command>\n", argv[0]);
        return 1;
    }
    printf("[v7-C] Command received: %s\n", argv[1]);
    return 0;
}
