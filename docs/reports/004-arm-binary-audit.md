# 004 — ARM Binary and ABI Inventory

- **Date:** 2026-11-09
- **Objective:** Inventory executable formats, ELF architecture, loaders, shared-library dependencies, symlinks, and hashes.
- **Work branch:** `recovery/04-arm-binary-audit`

## Findings

- Current main snapshot: 1,332 tracked blobs.
- Historical extracted filesystem: 1,330/1,330 files matched current root by exact Git blob SHA.
- Git tree metadata showed 116 duplicate-content groups across 702 paths and zero Git symlink entries.
- 256 executable paths share one 674,748-byte blob (BusyBox multicall family).
- 30 graphics-library paths in `usr/lib/` and `usr/lib32/` share one 929,956-byte blob, including EGL, GLES, Mali, OpenCL, and GBM names.
- Duplicate content across `usr/lib` and `usr/lib32` is a high-priority ABI check, not proof of corruption. Git records these paths as regular files.

## Implementation

Added read-only `scripts/audit-binaries.py` on its work branch. It computes hashes and collects file/ELF metadata with `file` and `readelf` when available. It does not execute or modify firmware binaries.

## Validation and status

- Python syntax validation: **passed**.
- Synthetic fixture: **passed** for basic file, ELF-magic, hash, CSV, and symlink handling.
- Actual firmware binary ABI inspection: **not completed**; binary bytes were not available through the GitHub text endpoint.
- Firmware build: **not run**.
- GitHub Actions: no workflow runs were available; no CI success claimed.
- Hardware verification: **not performed**.

## Required next step

From a local Linux checkout of `recovery/04-arm-binary-audit`, run:

```sh
python3 scripts/audit-binaries.py . -o binary-audit.csv
```

Verify ELF class, machine, byte order, interpreter, SONAME, and DT_NEEDED against the actual target SoC and libc before replacing any library.
