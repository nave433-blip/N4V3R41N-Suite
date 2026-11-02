#!/bin/bash
eval "$(/home/gnosis/.linuxbrew/bin/brew shellenv bash)"
source /home/gnosis/N4V3R41N-Suite/.venv/bin/activate
exec python /home/gnosis/N4V3R41N-Suite/n4v3r41n.py "$@"
