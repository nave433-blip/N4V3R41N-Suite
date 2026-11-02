#!/usr/bin/env python3
"""BUNNY RAMDISK - Passcode/Activation RESTORE (standalone CLI).

Restores activation files from a backup zip onto the SSH ramdisk (device must
be booted to ramdisk with filesystems mounted), runs restore.sh + skip_setup,
then reboots the device to normal iOS.

Usage:
  python3 bunny_restore.py /path/to/0x<ECID>.zip
"""
import importlib.util
import os
import sys
import time


def _find_core():
    env = os.environ.get('BUNNY_CORE', '').strip()
    if env and os.path.exists(env):
        return env
    candidates = [
        '/Users/bunny.cia/Documents/BUNNY RAMDISK/BUNNY RAMDISK 2.app/Contents/Resources/core.py',
        '/Users/bunny.cia/BUNNY RAMDISK/BUNNY RAMDISK 2.app/Contents/Resources/core.py',
        '/Applications/BUNNY RAMDISK.app/Contents/Resources/core.py',
        os.path.expanduser('~/BUNNY RAMDISK/GUI/core.py'),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return ''


CORE = _find_core()
if not CORE:
    sys.exit('core.py not found - set BUNNY_CORE=/path/to/core.py')

spec = importlib.util.spec_from_file_location('bunnycore', CORE)
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


def log(kind, msg):
    ts = time.strftime('%H:%M:%S')
    tag = {'ok': 'OK  ', 'error': 'ERR ', 'warn': 'WARN', 'info': 'INFO',
           'big': 'BIG ', 'bypass': 'BYP ', 'mount': 'MNT '}.get(kind, '    ')
    print('%s [%s] %s' % (ts, tag, msg), flush=True)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 bunny_restore.py /path/to/0x<ECID>.zip', flush=True)
        sys.exit(2)
    zip_path = sys.argv[1]
    if not os.path.exists(zip_path):
        print('ERROR: backup zip not found: %s' % zip_path, flush=True)
        sys.exit(2)
    print('=== BUNNY RAMDISK - RESTORE ===', flush=True)
    ok = core.do_restore(zip_path, log)
    log('big', 'RESULT: %s' % ('RESTORE OK' if ok else 'RESTORE FAILED'))
    sys.exit(0 if ok else 1)
