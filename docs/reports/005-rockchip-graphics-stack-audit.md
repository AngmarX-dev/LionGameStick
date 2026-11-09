# 005 — Rockchip Graphics Stack Recovery Audit

- **Date:** 2026-11-09
- **Objective:** Inspect the graphics/display runtime inventory and add a reproducible, read-only audit method without replacing any binary.
- **Work branch:** `recovery/05-rockchip-graphics-audit`
- **Report location:** `main` branch, as requested.

## Initial state

Main head before this report: `3e89841be432a54d06ec57a94cdfcc7386b4dc35`. The repository tree contains 1,458 entries. The README describes a Buildroot-based runtime with Rockchip DRM/KMS, MiniGUI, RetroArch, and multimedia components. This report treats those as repository claims and does not infer physical hardware compatibility from names alone.

## Graphics inventory findings

The recursive Git tree search found 173 paths matching graphics/display-related names, including libraries, MiniGUI configs/resources, DRM rules, and helper scripts.

Notable library path groups include:

- `usr/lib/` and `usr/lib32/`: EGL, GLESv1, GLESv2, Mali, Mali OpenCL, GBM, libdrm, and libdrm_rockchip names.
- The Git tree shows many versioned/unversioned names as ordinary regular-file blobs, not symlinks.
- The EGL/GLES/Mali/GBM-named files in both library directories share Git blob SHA `5f488634502f489b542251f0be8d3df2bdf332d7` and size 929,956 bytes.
- The libdrm names share blob SHA `e6d3ba7a36366ebe2f29d3a0dfeaf041a7db6e15` (46,680 bytes); libdrm_rockchip names share `4823fe81eb5f74942b930ded90081e58cf3a32a3` (9,448 bytes).
- MiniGUI library names share a separate 1,248,260-byte blob.

These identical hashes do **not** establish that the files are correct or incorrect. In particular, identical content in `usr/lib` and `usr/lib32` is an ABI risk requiring ELF inspection. No replacement was made.

## Implementation

Added `scripts/audit-graphics-stack.py` on the single work branch `recovery/05-rockchip-graphics-audit`. The script:

- Recursively inventories graphics/display/MiniGUI/RGA-related paths and excludes `.git`.
- Records regular files, ELF magic detection, symlink targets, file sizes, and SHA-256.
- Uses `readelf` when installed to capture ELF class, machine, interpreter, and DT_NEEDED entries.
- Writes CSV output and does not execute, modify, delete, or replace firmware files.

## Validation

- Python source compilation: **passed**.
- Synthetic inventory test: **passed** for ELF magic detection, regular-file hashing, symlink target reporting, path filtering, and CSV generation.
- The synthetic ELF fixture only tests detection and does not prove the target libraries' architecture or ABI.
- Actual binary readelf inspection: **not completed** because binary blob bytes could not be obtained through the GitHub text endpoint.
- Firmware build: **not run**; no firmware source or build configuration was changed.
- GitHub Actions: no workflow/checks were configured or reported for this branch; **no CI success is claimed**.
- Hardware verification: **not performed**.

## Next steps

On a Linux checkout of `recovery/05-rockchip-graphics-audit`, run:

```sh
python3 scripts/audit-graphics-stack.py . -o graphics-stack-audit.csv
```

Share the generated CSV. Before any recovery/replacement, confirm the exact Rockchip SoC/GPU generation, ELF class and machine, endianness, dynamic loader, libc, SONAMEs, DT_NEEDED dependencies, and driver userspace/kernel compatibility. Do not copy generic Mali libraries from another board.
