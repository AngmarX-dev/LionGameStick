# 003 — Repack Tracked Root Filesystem

- **Date:** 2026-11-09
- **Objective:** Provide a portable backup route from the tracked runtime filesystem without replacing binaries.
- **Work branch:** `recovery/03-repack-rootfs`

## Implementation

Added `scripts/repack-rootfs.sh`. It packages the known runtime directories, preserves modes and symlinks with tar, validates the resulting gzip archive, stages output before publication, and refuses to overwrite an existing destination. This produces a new backup format, not a byte-identical reconstruction of the historical 7-Zip archive.

## Validation and status

- Historical tree comparison: **1,330/1,330 exact blob matches**.
- POSIX shell syntax check (`sh -n`): **passed**.
- Synthetic fixture test: **passed** for archive listing, regular-file and symlink preservation, and overwrite protection.
- Actual rootfs repack: **not run**.
- Firmware build: **not run**.
- GitHub Actions: no workflow configured on `main`; no CI success claimed.
- Hardware verification: **not performed**.

## Limitations / next steps

Run from a Linux checkout with GNU tar. Review archive contents and file metadata before treating it as a deployment artifact.
