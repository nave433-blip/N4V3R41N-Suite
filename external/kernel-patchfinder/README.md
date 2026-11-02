# usbliter8-kernel-patchfinder

arm64e kernelcache patchfinder for A12/A13 jailbreak research, built for use with the [usbliter8](https://github.com/prdgmshift/usbliter8) BootROM exploit.

Finds 20 kernel patch targets automatically in ~6 seconds with zero hardcoded offsets. Tested on 14 kernelcaches across all A12/A13 devices, iOS 17.0 through 27.0 beta — 100% success rate.

## Usage

```
$ python3 kernel_patchfinder.py kernelcache.raw

=== Kernel Patchfinder (52.7 MB) ===
  ADRP index: 479744 entries (2.1s)
  BL index: 405464 entries (2.0s)
  _panic @ 0x1454ED0 (12816 callers)

  FOUND: 20 targets
  PE_i_can_has_debugger            0xFFFFFFF008433BF8
  AMFIIsCDHashInTrustCache         0xFFFFFFF008EF17DC
  bsd_init                         0xFFFFFFF008141E60
  vm_map_protect_func              0xFFFFFFF007E155B0
  vm_fault_enter                   0xFFFFFFF0083148E0
  task_for_pid                     0xFFFFFFF008190220
  ...
```

## Targets

| Target | Method |
|--------|--------|
| PE_i_can_has_debugger | Global variable tracing + BL histogram |
| AMFIIsCDHashInTrustCache | Instruction pattern (MOV X19,X2 / STP XZR / MOV X2,SP / BL / CBNZ) |
| bsd_init | String xref: "rootvp not authenticated" |
| SecureRootName | String xref |
| load_dylinker | String xref: "/usr/lib/dyld" |
| imageboot | String xref: "imageboot_needed" |
| cs_enforcement | String xref: "cs_enforcement_disable" |
| get_task_allow | String xref: "get-task-allow" |
| developer_mode | String xref: "developer-mode" |
| task_for_pid | String xref: "proc_ro_ref_task" |
| vm_map_protect | String xref: "vm_map_protect(" panic |
| vm_fault_enter | Instruction pattern: LDR [X,#0x20/#0x28] + TBZ #3 + MOV #0 + B |
| apfs_mount | String xref: "apfs_vfsop_mount" |
| apfs_graft | String xref |
| nvram_verify | String xref: "nvram-proxy-data" |
| mac_policy | BL frequency heuristic + page string check |
| dounmount | BL caller count heuristic |
| launch_constraints | String xref: entitlement string |
| debug_enabled_init | String xref: "debug-enabled" |
| _panic | Most-called function with "@%s:%d" format strings |

## Architecture

1. **ADRP index** — VA-aware page-to-offset map for O(1) string xref lookups
2. **BL index** — target-to-callers map for function identification by caller count
3. **String xref finder** — ADRP+ADD pair resolution across MH_FILESET segments
4. **Instruction patterns** — raw ARM64 encoding matches for targets without string anchors (vm_fault_enter cs_bypass gate, AMFI trustcache body shape)
5. **BL histogram** — PE_i_can_has_debugger found by: ADRP x8 start + LDR w,[x8] + 50-300 callers

Handles BTI c prefix (iOS 17+), PACIBSP prologues, RETAB epilogues, MH_FILESET kernelcaches.

## Pre-computed offsets

The `kernelcaches/` directory contains pre-computed offsets for all A12/A13 devices:

```
kernelcaches/
├── 17.0/README.md          — iPhone 11 (1 device)
├── 18.7.9/README.md        — iPhone XR / XS / XS Max (2 devices)
├── 26.5/README.md          — all A12/A13 iPhones + iPads (6 devices)
└── 27.0-beta/README.md     — A13 iPhones + iPads (5 devices)
```

14 kernelcaches, 20 targets each, 280 offsets total.

## Requirements

```
pip install capstone
```

## Related

- [usbliter8](https://github.com/prdgmshift/usbliter8) — A12/A13 SecureROM exploit by Paradigm Shift
- [usbliter8-iboot-patchfinder](https://github.com/Leeksov/usbliter8-iboot-patchfinder) — iBoot patchfinder (image4 bypass + CTRR NOP)
- [usbliter8-txm-patchfinder](https://github.com/Leeksov/usbliter8-txm-patchfinder) — TXM patchfinder (code signing bypass, iOS 27)
- [usbliter8-sptm-patchfinder](https://github.com/Leeksov/usbliter8-sptm-patchfinder) — SPTM patchfinder (CTRR lockdown bypass)
- [ida-iboot-loader](https://github.com/Orangera1n/ida-iboot-loader) — IDA loader for iBoot/SecureROM

For research purposes only.

## License

MIT
