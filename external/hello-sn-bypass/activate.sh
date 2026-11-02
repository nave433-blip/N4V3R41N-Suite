#!/usr/bin/env bash
# activate.sh — restore Hello activation files onto SSH ramdisk
#
# Usage (Terminal):
#   ./activate.sh /path/to/UDID_FOLDER
#   ./activate.sh /path/to/UDID.zip
#
# Drag & drop:
#   Drop the UDID folder (or .zip) onto "Activate (drop folder here).command"
#   Or: ./activate.sh   then drop the path into Terminal after the command
#
# Required inside the folder:
#   activation_record.plist
#   IC-Info.sisv
#   com.apple.commcenter.device_specific_nobackup.plist
# Optional:
#   com.apple.purplebuddy.plist   (else downloads known purplebuddy)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PASS="${SSHPASS_PASSWORD:-alpine}"
PORT="${SSH_PORT:-2222}"

# Prefer PATH tools, then ICH ramdisk tools
find_bin() {
  local n="$1"
  if command -v "$n" >/dev/null 2>&1; then command -v "$n"; return; fi
  for d in \
    "$ROOT/tools" \
    "$ROOT/../ICH_A12_plus_Ramdisk-main-2/tools/darwin" \
    "/Users/$(whoami)/Desktop/ICH_A12_plus_Ramdisk-main-2/tools/darwin"
  do
    [[ -x "$d/$n" ]] && { echo "$d/$n"; return; }
  done
  return 1
}

SSHPASS_BIN="$(find_bin sshpass)" || { echo "ERROR: sshpass not found"; exit 1; }
IPROXY_BIN="$(find_bin iproxy)" || { echo "ERROR: iproxy not found"; exit 1; }

SSH_OPTS=(
  -o HostKeyAlgorithms=+ssh-rsa
  -o StrictHostKeyChecking=no
  -o UserKnownHostsFile=/dev/null
  -o PubkeyAuthentication=no
  -o PreferredAuthentications=password
  -o KbdInteractiveAuthentication=yes
  -o ConnectTimeout=20
  -p "$PORT"
)
SCP_OPTS=(
  -o HostKeyAlgorithms=+ssh-rsa
  -o StrictHostKeyChecking=no
  -o UserKnownHostsFile=/dev/null
  -o PubkeyAuthentication=no
  -o PreferredAuthentications=password
  -o KbdInteractiveAuthentication=yes
  -o ConnectTimeout=20
  -P "$PORT"
)

ssh12() {
  "$SSHPASS_BIN" -p "$PASS" ssh "${SSH_OPTS[@]}" root@localhost "$@"
}

ssh13() {
  # scp local -> remote (same idea as their sshpass13)
  local src="$1" dst="$2"
  "$SSHPASS_BIN" -p "$PASS" scp "${SCP_OPTS[@]}" "$src" "$dst"
}

die() { echo "ERROR: $*" >&2; exit 1; }
log() { echo "==> $*"; }

# --- resolve input folder ---
SRC="${1:-}"
[[ -n "$SRC" ]] || die "Usage: $0 /path/to/UDID_FOLDER_or.zip
Drop the activation folder onto this script / .command"

# strip trailing slash / expand
SRC="$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")"

WORK="$(mktemp -d /tmp/activate_hello.XXXXXX)"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

FOLDER=""
if [[ -d "$SRC" ]]; then
  FOLDER="$SRC"
elif [[ -f "$SRC" && "$SRC" == *.zip ]]; then
  log "Unzipping $(basename "$SRC")"
  unzip -o -q "$SRC" -d "$WORK/unz"
  # if zip contains one top folder, use it; else use unz root
  if [[ $(find "$WORK/unz" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ') -eq 1 && \
        $(find "$WORK/unz" -mindepth 1 -maxdepth 1 -type f | wc -l | tr -d ' ') -eq 0 ]]; then
    FOLDER="$(find "$WORK/unz" -mindepth 1 -maxdepth 1 -type d | head -1)"
  else
    FOLDER="$WORK/unz"
  fi
else
  die "Need a folder or .zip, got: $SRC"
fi

need() { [[ -f "$FOLDER/$1" ]] || die "Missing $1 in $FOLDER"; }
need activation_record.plist
need IC-Info.sisv
need com.apple.commcenter.device_specific_nobackup.plist

# purplebuddy
PURPLE="$FOLDER/com.apple.purplebuddy.plist"
if [[ ! -f "$PURPLE" ]]; then
  for c in \
    "$ROOT/com.apple.purplebuddy.plist" \
    "$ROOT/purplebuddy.plist" \
    "$ROOT/_bypass_work/com.apple.purplebuddy.plist"
  do
    [[ -f "$c" ]] && { PURPLE="$c"; break; }
  done
fi
if [[ ! -f "$PURPLE" ]]; then
  log "Downloading purplebuddy.plist"
  curl -fsSL \
    "https://raw.githubusercontent.com/linhbg1998/bypass-icloud/87b0394af8600515ee58adf0c422b8dfd70bec58/GSMUNLOCK/htools/libs/purplebuddy.plist" \
    -o "$WORK/com.apple.purplebuddy.plist"
  PURPLE="$WORK/com.apple.purplebuddy.plist"
fi

log "ACTIVATION HELLO 10%"
log "Source: $FOLDER"

# --- iproxy ---
pkill -f "iproxy ${PORT} 22" 2>/dev/null || true
sleep 0.3
"$IPROXY_BIN" "$PORT" 22 >/dev/null 2>&1 &
IPROXY_PID=$!
sleep 1
kill -0 "$IPROXY_PID" 2>/dev/null || die "iproxy failed to start (is the device in SSH ramdisk?)"

ssh12 'echo connected' >/dev/null || die "SSH failed — check ramdisk / iproxy / password"

log "ACTIVATION HELLO 20%"
# ensure mounts have System data
if ! ssh12 'ls /mnt2/containers/Data/' 2>/dev/null | grep -q System; then
  die "/mnt2/containers/Data/System not found — mount filesystems first"
fi

log "Upload to /mnt1 + Downloads"
ssh13 "$FOLDER/activation_record.plist" "root@localhost:/mnt1/activation_record.plist"
ssh13 "$FOLDER/IC-Info.sisv" "root@localhost:/mnt1/IC-Info.sisv"

# Downloads path often ACL-blocked for scp; stage then place
ssh12 'mkdir -p /mnt2/mobile/Media/Downloads /mnt2/root'
if ! ssh13 "$FOLDER/com.apple.commcenter.device_specific_nobackup.plist" \
  "root@localhost:/mnt2/mobile/Media/Downloads/com.apple.commcenter.device_specific_nobackup.plist" 2>/dev/null; then
  log "Downloads scp blocked — staging via /mnt2/root"
  ssh13 "$FOLDER/com.apple.commcenter.device_specific_nobackup.plist" \
    "root@localhost:/mnt2/root/com.apple.commcenter.device_specific_nobackup.plist"
  ssh12 'mv -f /mnt2/root/com.apple.commcenter.device_specific_nobackup.plist /mnt2/mobile/Media/Downloads/com.apple.commcenter.device_specific_nobackup.plist' \
    || ssh12 'cp /mnt2/root/com.apple.commcenter.device_specific_nobackup.plist /mnt2/mobile/Media/Downloads/com.apple.commcenter.device_specific_nobackup.plist'
fi

ssh13 "$PURPLE" "root@localhost:/mnt1/com.apple.purplebuddy.plist"

log "ACTIVATION HELLO 30%"
ssh12 '/bin/rm -f /mnt2/root/activation_record.plist'

# ===== exact restore sequence =====
ssh12 '/bin/mv -f /mnt1/activation_record.plist /mnt2/root/'
ssh12 '/bin/rm -rf /mnt2/mobile/Library/FairPlay'
ssh12 '/bin/rm -rf /mnt2/containers/Data/System/*/Library/activation_records'

ssh12 '/bin/mkdir -p -m 00755 /mnt2/mobile/Library/FairPlay/iTunes_Control/iTunes'

ssh12 '/bin/mv -f /mnt1/IC-Info.sisv /mnt2/root/'
ssh12 '/bin/mv -f /mnt2/root/IC-Info.sisv /mnt2/mobile/Library/FairPlay/iTunes_Control/iTunes/'
ssh12 '/bin/chmod 00664 /mnt2/mobile/Library/FairPlay/iTunes_Control/iTunes/IC-Info.sisv'
ssh12 '/usr/sbin/chown -R mobile:mobile /mnt2/mobile/Library/FairPlay'

log "ACTIVATION HELLO 40%"
# mkdir via internal/../
ssh12 'cd /mnt2/containers/Data/System/*/Library/internal/../ && /bin/mkdir -p activation_records' || true

# mv into activation_records; if Data Vault blocks, directory-swap to SAME path
if ! ssh12 'cd /mnt2/containers/Data/System/*/Library/activation_records && /bin/mv -f /mnt2/root/activation_record.plist ./'; then
  log "activation_records write blocked — swapping directory to same path"
  ssh12 '/bin/sh -s' <<'EOS'
set -e
LIB=""
for d in /mnt2/containers/Data/System/*/Library; do
  [ -d "$d/internal" ] || continue
  LIB=$d
  break
done
[ -n "$LIB" ] || { echo "no Library/internal found"; exit 1; }
rm -rf "$LIB/activation_records" /mnt2/tmp/ar.new
mkdir -p /mnt2/tmp/ar.new
/bin/mv -f /mnt2/root/activation_record.plist /mnt2/tmp/ar.new/activation_record.plist
/bin/mv /mnt2/tmp/ar.new "$LIB/activation_records"
EOS
fi

ssh12 'cd /mnt2/containers/Data/System/*/Library/activation_records/.. && chmod 755 activation_records'
ssh12 'cd /mnt2/containers/Data/System/*/Library/activation_records/.. && chmod 0664 activation_records/activation_record.plist'
ssh12 'rm -rf /mnt2/mobile/Library/Logs/'

log "ACTIVATION HELLO 60%"
ssh12 'mv -f /mnt2/mobile/Media/Downloads/com.apple.commcenter.device_specific_nobackup.plist /mnt2/wireless/Library/Preferences/'

ssh12 'rm -f /mnt2/mobile/Library/Preferences/com.apple.purplebuddy.plist' || true
if ! ssh12 'mv -f /mnt1/com.apple.purplebuddy.plist /mnt2/mobile/Library/Preferences/com.apple.purplebuddy.plist'; then
  log "purplebuddy Preferences blocked — swapping Preferences dir"
  ssh12 '/bin/sh -s' <<'EOS'
set -e
PREF=/mnt2/mobile/Library/Preferences
SRC=/mnt1/com.apple.purplebuddy.plist
rm -rf /mnt2/tmp/pref.new
mkdir -p /mnt2/tmp/pref.new
for f in "$PREF"/*; do
  [ -e "$f" ] || continue
  bn=$(basename "$f")
  [ "$bn" = "com.apple.purplebuddy.plist" ] && continue
  cp -R "$f" /mnt2/tmp/pref.new/ 2>/dev/null || true
done
cp "$SRC" /mnt2/tmp/pref.new/com.apple.purplebuddy.plist
rm -rf /mnt2/tmp/pref.old
mv "$PREF" /mnt2/tmp/pref.old 2>/dev/null || rm -rf "$PREF"
mv /mnt2/tmp/pref.new "$PREF"
/usr/sbin/chown -R mobile:mobile "$PREF" 2>/dev/null || true
rm -f "$SRC"
EOS
fi
ssh12 'rm -rf /mnt2/mobile/Media/Downloads/com.apple.purplebuddy.plist' || true

ssh12 'launchctl unload /mnt1/System/Library/LaunchDaemons/com.apple.CommCenter.plist' || true
ssh12 'sync'

log "ACTIVATION HELLO 100% — verify"
ssh12 '/bin/sh -s' <<'EOS'
ok=1
check() {
  if [ -e "$1" ]; then echo "THERE  $1"; ls -la "$1"
  else echo "MISSING $1"; ok=0; fi
}
check /mnt2/mobile/Library/FairPlay/iTunes_Control/iTunes/IC-Info.sisv
check /mnt2/wireless/Library/Preferences/com.apple.commcenter.device_specific_nobackup.plist
check /mnt2/mobile/Library/Preferences/com.apple.purplebuddy.plist
echo "--- activation_records ---"
ls -la /mnt2/containers/Data/System/*/Library/activation_records/activation_record.plist 2>&1 || { echo MISSING activation_record; ok=0; }
ls -ld /mnt2/containers/Data/System/*/Library/activation_records 2>&1 || true
[ "$ok" = 1 ] && echo ALL_OK || echo SOME_MISSING
EOS

log "Done."
