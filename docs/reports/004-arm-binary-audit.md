# 004 — ARM Binary and ABI Inventory

- **Date:** 2026-11-09
- **Objective:** Establish a reproducible, read-only inventory of firmware executables, ELF architecture, dynamic loaders, shared-library dependencies, symlinks, and file hashes.
- **Branch:** `recovery/04-arm-binary-audit`

## Findings from repository metadata

- The current `main` snapshot contains 1,332 tracked blobs.
- 112 paths have a `.so` extension; the extension alone does not establish ABI or architecture.
- The tree includes BusyBox-style command links/names under `bin/`, shared-library paths, configuration files, MiniGUI-related assets, fonts, and graphics-related files.
- The historical extracted tree has 1,330 files; all 1,330 paths were matched against the current root by exact Git blob SHA.
- The initial repository commit contains only two blobs; no older firmware binary snapshot is available in the visible eight-commit history.


## Additional integrity signals from Git tree metadata

A content-SHA grouping of the 1,332 tracked blobs found **116 duplicate-content groups covering 702 paths**, and **zero Git symlink entries**.

Notable groups requiring byte-level inspection:
- **256 executable paths** across `bin/`, `sbin/`, and `usr/bin/`/ `usr/sbin/` share one 674,748-byte blob (the BusyBox multicall command family).
- **30 graphics-library paths** across `usr/lib/` and `usr/lib32/` share one 929,956-byte blob. These paths include EGL, GLES, Mali, OpenCL, and GBM names.
- The presence of identical content under both `usr/lib/` and `usr/lib32/` is a high-priority ABI verification item. It is not enough to conclude corruption from Git metadata alone; the paths may be intentional aliases, but Git records them as regular files rather than symlinks.
- 112 paths end in `.so` (including versioned shared-object names). This is a filename count, not a verified ELF count.

**Do not normalize these duplicate groups or replace libraries yet.** First run the local inventory script and inspect the actual ELF class, machine, SONAME, loader, and DT_NEEDED values. If the `usr/lib32` objects are truly identical 64-bit or otherwise incompatible files, treat that as a firmware packaging defect and recover the correct 32-bit objects from a trusted source.

## Important inspection limitation

The GitHub file-content endpoint cannot decode the raw bytes of `bin/busybox` as UTF-8. Therefore, no ELF architecture, ABI, endianness, dynamic loader, or dependency is asserted from the filename or extension. These properties require inspecting the actual binary bytes in a local checkout.

## Implementation

Added `scripts/audit-binaries.py`, a read-only inventory tool. It:
- Recursively inventories files and symlinks while excluding `.git`.
- Computes SHA-256 for regular files.
- Uses `file` to classify formats when available.
- Uses `readelf` to collect ELF class, byte order, machine, PT_INTERP, and DT_NEEDED entries when available.
- Writes a CSV report and a concise JSON summary.
- Does not modify, replace, execute, or delete firmware files.

## Validation

- Historical Git comparison: **1,330 / 1,330 exact blob matches**.
- Python syntax and runtime validation: **not run in this environment**.
- Firmware build: **not run**; no firmware source change is included.
- GitHub Actions: no workflow runs are configured/reported for the recovery branches; no CI pass is claimed.
- Physical hardware validation: **not performed**.

## Required next step

Run from a Linux checkout with Python 3.10+, and preferably `file` and `binutils` installed:

```sh
python3 scripts/audit-binaries.py . -o binary-audit.csv
```

Review the CSV before changing any binary. Confirm the target SoC, ARM EABI version, hard-float/soft-float ABI, libc family, dynamic loader, and required shared-library SONAMEs against the device firmware. Never replace a library based only on its filename.
