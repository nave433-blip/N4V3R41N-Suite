# A12/A13 Hello Screen Bypass with SN Change

A12/A13 (iPhone XS–11 series, SE2) Hello/activation lock bypass toolkit:
FE00 activation record + MobileGestalt CacheData patch + activation restore.

## Files

| File | Purpose |
|---|---|
| `activate.sh` | Restore activation files (record, IC-Info, commcenter, purplebuddy) onto the SSH ramdisk |
| `patch_gestalt_cachedata.py` | Patch MobileGestalt `CacheData` offsets (672 / 673 / 3192) |
| `patch_gestalt_cachedata_iPhone.py` | Same CacheData patch + DeviceClass key change |
| `Archive.zip` | FE00 record generator (`act.php`) + gestalt pull/restore helpers (`get_gestalt.py`, `restore_gestalt.py`) |

## Requirements

- A12/A13 device (iPhone XS, XS Max, XR, 11, 11 Pro, 11 Pro Max, SE 2) — checkm8 vulnerable
- Bootrom exploit pwned DFU (usbliter8 / checkm8 tool) + SSH ramdisk
- `iproxy`, `sshpass` (macOS) or equivalent on Windows
- SSH ramdisk up: `iproxy 2222 22` → `ssh root@localhost -p 2222` (password: `alpine`)

## Usage — Step by Step

### 1. Put device in DFU mode

Hold **Power + Home** (or Power + Vol-Down for Face ID models) for 10s,
release Power, keep the other button 5s until the screen stays black = DFU.

### 2. Pwn + boot SSH ramdisk

Use your checkm8/usbliter8 tool to pwn DFU, then boot the SSH ramdisk for your
device (iBEC → Recovery → kernelcache → ramdisk). Wait for the teal/verbose screen.

### 3. Start iproxy + mount filesystems

```bash
iproxy 2222 22 &
ssh root@localhost -p 2222   # password: alpine
# inside the ramdisk:
mount_ich    # mounts System/Data/Preboot volumes
```

### 4. Generate the FE00 activation record

Unzip `Archive.zip`, then generate the record with `act.php`:

```bash
# Option A - local PHP server (as designed):
php -S 127.0.0.1:8080 &
curl "http://127.0.0.1:8080/act.php?udid=0000FE00-XXXXXXXXXXXXXXXX&product=iPod7,1&model=MWH22"
```

This produces a folder with `info`, `activation_record.plist`, `data_ark.plist`,
`IC-Info.sisv` and the commcenter plist.

> Default identity: iPod7,1 / MWH22 / serial CCQQ4JXBGGK6 — Apple-accepted defaults.
> `act.php` auto-patches UDID prefix `00008030/8110/8120/8130/8020` → `0000FE00`.

### 5. Restore activation files

```bash
./activate.sh /path/to/UDID_FOLDER
# or drag the folder onto the script
```

This places:

- `activation_record.plist` → `System container/Library/activation_records/`
- `IC-Info.sisv` → `mobile/Library/FairPlay/iTunes_Control/iTunes/` (+ container/media paths)
- `com.apple.commcenter.device_specific_nobackup.plist` → `wireless/Library/Preferences/`
- `com.apple.purplebuddy.plist` → `mobile/Library/Preferences/`

### 6. Patch MobileGestalt (gestalt swap)

Pull the native gestalt first, then patch:

```bash
# pull native gestalt (binary-safe, from Archive.zip)
python3 get_gestalt.py

# patch CacheData offsets (672=00, 673=FE, 3192)
python3 patch_gestalt_cachedata.py com.apple.MobileGestalt.plist -o com.apple.MobileGestalt.patched.plist

# (optional) iPhone model: also flip DeviceClass
python3 patch_gestalt_cachedata_iPhone.py com.apple.MobileGestalt.plist -o com.apple.MobileGestalt.patched.plist

# upload back
python3 restore_gestalt.py com.apple.MobileGestalt.patched.plist
```

### 7. (Optional) Baseband / signal removal

For no-signal (IMEI removed) bypass, strip the baseband — rename/remove
Preboot `Baseband` and wipe commcenter prefs. See common A12 hello-bypass guides.

### 8. Reboot

```bash
ssh root@localhost -p 2222 "/sbin/reboot"
```

Device boots to Home screen with setup skipped (SkipSetup markers) — no Hello,
no activation banner.

## Notes

- Keep `data_ark.plist` `-ProductVersion` / `-BuildVersion` matching the device iOS
  build (mismatch → activation boot-reject → Hello comes back).
- On baseband devices, `HasBaseband (3192)=1` keeps Settings → About from freezing.
- The RSA private key inside `act.php` is the FE00 signing identity — treat it as
  the tool's signing material.

## ☕ Buy Me a Coffee

If this tool helped you unlock or bypass your device, consider buying me a coffee:
- **FOLLOW ME ON X : https://x.com/bunnyciaa?s=11
- **BINANCE:** ACCOUNT : 589455835

Every coffee keeps the A12/A13 bypass scripts maintained and updated. Thanks! 
