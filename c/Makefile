# N4V3R41N C Implementation Makefile

CC = gcc
CFLAGS = -Wall -Wextra -O2 -I. -Isrc
LDFLAGS = -limobiledevice -lusbmuxd -lplist -lssl -lcrypto -lcurl -lssh2

TARGET = n4v3r41n

SRCS = \
	src/n4v3r41n.c \
	src/utils/logger.c

OBJS = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean
