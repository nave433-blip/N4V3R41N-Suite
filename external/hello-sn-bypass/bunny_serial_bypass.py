#!/usr/bin/env python3
"""BUNNY RAMDISK - Serial Change Bypass (SSH mount + SN change bypass).

FE00 serial-change bypass method (proven on A12/A13):
  1. Boot SSH ramdisk + mount filesystems (SSH mount)
  2. Serial gate: device SN readable? -> use it; else required SN from settings.
     FE00 records are serial-independent (Apple signs the donor identity
     iPod7,1/MWH22/CCQQ4JXBGGK6) - a mismatch is a warning, not a block.
  3. Generate Apple-signed FE00 activation record (default params).
  4. Patch data_ark to device build (critical - build mismatch boot-rejects).
  5. Gestalt swap (672=00, 673=FE, 3192 per device) + Camera fix (CAMFIX).
  6. restore.sh + skip_setup.sh + SkipSetup markers.
  7. Reboot to normal iOS - home screen, no Hello, setup skipped.

Usage:
  python3 bunny_serial_bypass.py            # full run (boot -> mount -> bypass)
  python3 bunny_serial_bypass.py --mount    # SSH mount only
  python3 bunny_serial_bypass.py --check    # serial gate check only
  python3 bunny_serial_bypass.py --sn XXXX  # override required serial
"""
import importlib.util
import os
import sys
import time

CORE = '/Users/bunny.cia/Documents/BUNNY RAMDISK/BUNNY RAMDISK 2.app/Contents/Resources/core.py'
spec = importlib.util.spec_from_file_location('bunnycore', CORE)
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


def log(kind, msg):
    ts = time.strftime('%H:%M:%S')
    tag = {'ok': 'OK  ', 'error': 'ERR ', 'warn': 'WARN', 'info': 'INFO',
           'big': 'BIG ', 'bypass': 'BYP ', 'mount': 'MNT ', 'boot': 'BOOT'}.get(kind, '    ')
    print('%s [%s] %s' % (ts, tag, msg), flush=True)


def serial_gate(log, sn_override=''):
    """Serial change bypass gate: FE00 records are serial-independent.
    Device SN readable -> use it; else required SN from settings.
    Mismatch is a WARNING (Apple signs the donor identity regardless)."""
    s = core.load_settings()
    required = (sn_override or (s.get('bypass') or {}).get('requiredSerial') or 'GB035LDEZ39').strip().upper()
    dev = core.get_device_info()
    dev_sn = (dev.get('serial') or '').strip().upper()

    log('info', 'Serial gate - required: %s' % required)
    if dev_sn:
        log('info', 'Device serial (readable): %s' % dev_sn)
        if required and dev_sn != required:
            log('warn', 'SN mismatch device=%s vs required=%s - FE00 serial-independent, continuing' % (dev_sn, required))
        record_sn = dev_sn
    else:
        log('info', 'Device serial not readable (DFU/ramdisk) - using required SN %s' % required)
        record_sn = required

    # persist serial for the record + gate
    s.setdefault('bypass', {})['requiredSerial'] = required
    core.save_settings(s)
    log('ok', 'Serial gate OK - record will use SN %s (serial change bypass)' % record_sn)
    return record_sn


def ssh_mount(log):
    """SSH mount: boot ramdisk (if needed) -> iproxy/SSH -> mount_ich."""
    if not core.boot_and_ssh(log):
        log('error', 'BOOT FAILED - device must be pwned DFU (PWND: usbliter8)')
        return False
    if not core.mount_all(log):
        log('error', 'MOUNT FAILED')
        return False
    log('big', 'SSH MOUNT DONE - /mnt2 up')
    return True


def main():
    args = [a for a in sys.argv[1:]]
    sn_override = ''
    if '--sn' in args:
        i = args.index('--sn')
        if i + 1 < len(args):
            sn_override = args[i + 1]

    print('=== BUNNY RAMDISK - SERIAL CHANGE BYPASS ===', flush=True)

    if '--check' in args:
        serial_gate(log, sn_override)
        return 0

    # 1. SSH mount (boot + mount)
    if not ssh_mount(log):
        return 1

    if '--mount' in args:
        log('big', 'MOUNT-ONLY DONE')
        return 0

    # 2. Serial gate (SN change bypass)
    serial_gate(log, sn_override)

    # 3. Full bypass (FE00 + data_ark patch + gestalt + restore + camera)
    ok = core.do_hello_bypass(log)
    log('big', 'RESULT: %s' % ('SERIAL CHANGE BYPASS OK' if ok else 'FAILED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
