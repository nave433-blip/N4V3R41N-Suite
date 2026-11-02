# BUNNY RAMDISK — Backup / Restore (Standalone CLI)

A12/A13 (iPhone XS–11 series, SE2) activation backup & restore scripts for the
BUNNY RAMDISK SSH ramdisk workflow. These are standalone CLI versions of the
GUI tool's backup/restore buttons — same logic, no GUI needed.

## Files

| File | Purpose |
|---|---|
| `bunny_backup.py` | Pull activation files from the SSH ramdisk → backup zip `0x<ECID>.zip` |
| `bunny_restore.py` | Restore activation files from a backup zip → reboot to normal iOS |

## Requirements

- A12/A13 device booted to the **BUNNY RAMDISK SSH ramdisk** (usbliter8 pwned DFU
  → iBEC → ramdisk → SSH up), filesystems mounted (`mount_ich`, `/mnt2` up)
- `python3` on the host
- macOS BUNNY RAMDISK install (scripts auto-discover `core.py`; override with the
  `BUNNY_CORE` environment variable if needed)

---

## 🔧 Prerequisites (for both backup and restore)

1. **Put the device in DFU mode** → boot the SSH ramdisk:
   - Power + Home 10s → release Power, keep Home 5s → black screen = DFU
2. **Boot the ramdisk** (GUI "Boot" button, or `usbliter8_boot` + payloads)
3. **Mount the filesystems** (GUI "Mount", or `mount_ich` over SSH)
4. Verify: `nc -z 127.0.0.1 2222` → port open, and `/mnt2` exists on the device

---

## 📤 BACKUP — How to do it

### Step 1 — Boot + Mount
```
Device in DFU  →  GUI: 🚀 Boot  →  💾 Mount
```
Wait for: `SSH done` + `MOUNT DONE THANKS TO BUNNYCIA`

### Step 2 — Run backup
```bash
python3 bunny_backup.py
```

### Step 3 — What it does (automatically)
Pulls from the device (via SSH on port 2222, password `alpine`):

| File pulled | From device |
|---|---|
| `activation_record.plist` | `System container/Library/activation_records/` |
| `data_ark.plist` | `System container/Library/internal/` |
| `com.apple.commcenter.device_specific_nobackup.plist` | `wireless/Library/Preferences/` |
| `IC-Info.sisv` | `mobile/Library/FairPlay/iTunes_Control/iTunes/` |
| `owner_info.txt` | device / serial / ECID / phone |

### Step 4 — Result
```
~/BUNNY RAMDISK/Backup/0x<ECID>.zip
```
The device reboots to normal iOS automatically.

> **Tip:** Keep this zip safe — it is your activation identity backup. Copy it to
> another drive.

---

## 📥 RESTORE — How to do it

### Step 1 — Boot + Mount (same as backup)
```
Device in DFU  →  GUI: 🚀 Boot  →  💾 Mount
```
Wait for `MOUNT DONE`.

### Step 2 — Run restore with your zip
```bash
python3 bunny_restore.py ~/BUNNY\ RAMDISK/Backup/0x<ECID>.zip
```
Use **your** zip path — the one produced by the backup step.

### Step 3 — What it does (automatically)
1. Extracts the backup zip
2. Stages files on the device (`/mnt2/root/Activation/`)
3. Runs `restore.sh` — places record, data_ark, IC-Info, commcenter at all required locations
4. Runs `skip_setup.sh` — purplebuddy + CloudConfigurationDetails + SkipSetup markers
5. Locks activation blobs (anti runtime wipe)
6. Verifies sizes (`act_rec` / `data_ark` / `IC`)
7. **Reboots to normal iOS**

### Step 4 — Result
- Home screen, no Hello, no activation banner
- Setup skipped — do **NOT** walk through Hello/setup

---

## ⚠️ Important Notes

| Rule | Why |
|---|---|
| Do NOT run Hello/Setup after restore | It can re-trigger activation |
| Keep `data_ark` build matching device iOS | Mismatch → boot-reject → Hello returns |
| Device must be in ramdisk + mounted | Scripts fail with "SSH not up" otherwise |
| Backup and restore are a pair | Same zip layout expected |

## ❓ Error Meanings

| Error | Fix |
|---|---|
| `SSH not up` | Boot the ramdisk first |
| `Filesystems not mounted` | Run Mount first |
| `Backup zip not found` | Wrong path — check the zip name |
| `BACKUP FAILED` | Check USB cable / device state |

## Commands Summary

```bash
# Backup
python3 bunny_backup.py

# Restore
python3 bunny_restore.py ~/BUNNY\ RAMDISK/Backup/0x<ECID>.zip
```

---

## ☕ Buy Me a Coffee

