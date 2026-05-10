#include <stdio.h>
#include <stdarg.h>

void log_info(const char *format, ...) {
    va_list args;
    va_start(args, format);
    printf("[v7-C] [INFO] ");
    vprintf(format, args);
    printf("\n");
    va_end(args);
}
