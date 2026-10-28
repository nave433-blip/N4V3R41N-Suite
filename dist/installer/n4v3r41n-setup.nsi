; N4V3R41N-Suite one-click Windows installer (NSIS).
;
; Double-click setup exe -> wizard -> Finish. No terminal, no admin,
; no PowerShell execution-policy or "blocked download" hoops: the
; installer itself extracts the files, so they carry no Mark-of-the-Web.
;
; Installs to %LOCALAPPDATA%\N4V3R41N\bin (same folder the old
; install.ps1 used, so it upgrades cleanly over a script install),
; adds that folder to the user's PATH, puts shortcuts in the Start
; Menu, and registers an uninstaller in Add/Remove Programs.
;
; Build on any machine with makensis (Linux OK):
;   makensis dist/installer/n4v3r41n-setup.nsi
; Output: dist/N4V3R41N-Setup-v5.2.1.exe
;
; NOTE: the exe is unsigned (no code-signing certificate), so the
; first run on a fresh machine may show a SmartScreen prompt:
; click "More info" -> "Run anyway". That is a one-time click, not
; a failure, and it only happens for the setup file itself.

!include "MUI2.nsh"
!include "StrFunc.nsh"
${StrContains}

!define APP_NAME "N4V3R41N-Suite"
!define APP_VERSION "5.2.1"
!define EXE_NAME "n4v3r41n-cli.exe"
!define INSTALL_SUBDIR "N4V3R41N\bin"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "dist\N4V3R41N-Setup-v${APP_VERSION}.exe"
InstallDir "$LOCALAPPDATA\${INSTALL_SUBDIR}"
RequestExecutionLevel user
SetCompressor /SOLID lzma

!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "Run N4V3R41N Doctor now (checks your setup)"
!define MUI_FINISHPAGE_RUN_FUNCTION RunDoctor

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

; ---- PATH helpers (user PATH, HKCU, broadcast the change) ----------------
!define HWND_BROADCAST 0xFFFF
!define WM_WININICHANGE 0x1A

Function AddToUserPath
  ; $0 = dir to add. Leaves $0 untouched on failure.
  ReadRegStr $1 HKCU "Environment" "Path"
  ${StrContains} $2 $0 $1
  StrCmp $2 "" 0 done
    StrCmp $1 "" 0 append
      WriteRegExpandStr HKCU "Environment" "Path" $0
      Goto broadcast
    append:
      WriteRegExpandStr HKCU "Environment" "Path" "$1;$0"
    broadcast:
      System::Call 'user32::SendMessageTimeout(i ${HWND_BROADCAST}, i ${WM_WININICHANGE}, i 0, t "Environment", i 0, i 5000, *i .r3) '
  done:
FunctionEnd

Function RemoveFromUserPath
  ; $0 = dir to remove.
  ReadRegStr $1 HKCU "Environment" "Path"
  StrCmp $1 "" done
  ; Rebuild the path without $0 (case-insensitive compare, trailing
  ; backslashes ignored).
  StrCpy $2 ""
  StrCpy $3 0
  loop:
    StrCpy $4 $1 1 $3
    StrCmp $4 "" finish
    StrCmp $4 ";" found_sep
    StrCpy $5 "$5$4"
    IntOp $3 $3 + 1
    Goto loop
  found_sep:
    ; $5 holds one entry; keep it unless it equals $0.
    StrCpy $6 $5
    loop_trim:
      StrCpy $7 $6 1 -1
      StrCmp $7 "\" 0 check
      StrCpy $6 $6 -1
      Goto loop_trim
    check:
      StrCmp $6 $0 "" keep
      StrCpy $5 ""
      Goto next
    keep:
      StrCmp $2 "" 0 join
        StrCpy $2 $5
        Goto next
      join:
        StrCpy $2 "$2;$5"
    next:
      StrCpy $5 ""
      IntOp $3 $3 + 1
      Goto loop
  finish:
    ; Trailing entry (no trailing semicolon in the original).
    StrCmp $5 "" write
    StrCpy $6 $5
    loop_trim2:
      StrCpy $7 $6 1 -1
      StrCmp $7 "\" 0 check2
      StrCpy $6 $6 -1
      Goto loop_trim2
    check2:
      StrCmp $6 $0 "" keep2
      Goto write
    keep2:
      StrCmp $2 "" 0 join2
        StrCpy $2 $5
        Goto write
      join2:
        StrCpy $2 "$2;$5"
  write:
    WriteRegExpandStr HKCU "Environment" "Path" $2
    System::Call 'user32::SendMessageTimeout(i ${HWND_BROADCAST}, i ${WM_WININICHANGE}, i 0, t "Environment", i 0, i 5000, *i .r3) '
  done:
FunctionEnd

Function RunDoctor
  ; Finish-page checkbox: open a window that stays open with the
  ; doctor report, so a non-terminal user can read it.
  ExecShell "" "$WINDIR\System32\cmd.exe" '/k "$INSTDIR\${EXE_NAME}" doctor' SW_SHOWNORMAL
FunctionEnd

Section "Install"
  SetOutPath "$INSTDIR"
  File "dist\${EXE_NAME}"
  File /oname=WINDOWS.txt "dist\WINDOWS.txt"

  ; Uninstaller + Add/Remove Programs entry.
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
    "DisplayName" "${APP_NAME} ${APP_VERSION}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
    "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
    "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
    "DisplayVersion" "${APP_VERSION}"
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
    "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
    "NoRepair" 1

  ; Start Menu shortcuts (doctor opens in a window that stays open).
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\N4V3R41N Doctor.lnk" \
    "$WINDIR\System32\cmd.exe" '/k "$INSTDIR\${EXE_NAME}" doctor'
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\N4V3R41N Help.lnk" \
    "$WINDIR\System32\cmd.exe" '/k "$INSTDIR\${EXE_NAME}" --help'
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

  ; PATH (user level, no admin).
  StrCpy $0 "$INSTDIR"
  Call AddToUserPath

  ; Sanity check: the installed exe must at least answer --version.
  ; Warn (don't abort) if it can't run, so a first-time Windows quirk
  ; is visible instead of silently "installed but broken".
  nsExec::ExecToStack '"$INSTDIR\${EXE_NAME}" --version'
  Pop $0
  StrCmp $0 "0" version_ok
    MessageBox MB_ICONEXCLAMATION|MB_OK \
      "Installed, but $\"$INSTDIR\${EXE_NAME}$\" --version did not run cleanly.$\n$\nTry opening a NEW terminal and running: n4v3r41n-cli doctor"
  version_ok:
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\${EXE_NAME}"
  Delete "$INSTDIR\WINDOWS.txt"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  ; Remove the parent folder too if it is now empty.
  RMDir "$LOCALAPPDATA\N4V3R41N"

  Delete "$SMPROGRAMS\${APP_NAME}\N4V3R41N Doctor.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\N4V3R41N Help.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"

  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

  StrCpy $0 "$INSTDIR"
  Call un.RemoveFromUserPath
SectionEnd
