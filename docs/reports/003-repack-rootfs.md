# 003 — Repack Tracked Root Filesystem

- **Date:** 2026-11-09
- **Objective:** Provide a third recovery route by rebuilding a portable archive from the currently tracked runtime filesystem, without substituting or rebuilding individual binaries.
- **Branch:** `recovery/03-repack-rootfs`

## Initial state

The history audit established that all 1,330 files in the previous `extracted/GameStickLite/` tree are present at the current repository root with identical Git blob SHA values. The original `archive.7z.001` can be recovered from Git history, but its archive integrity test cannot be executed in the current environment.

## Implementation

- Added `scripts/repack-rootfs.sh`.
- The script packages only the known runtime filesystem paths (`bin`, `data`, `etc`, `init`, `lib`, `lib32`, `linuxrc`, `mnt`, `sbin`, `sdcard`, `tmp`, `usr`, `userdata`, and `var`).
- GNU tar preserves executable modes and symlinks; the script validates the generated gzip tar archive before publishing it.
- Existing output files are never overwritten. The temporary archive is removed on failure.
- The generated archive is a new backup format, not a byte-for-byte reconstruction of the original 7-Zip archive.

## Validation

- Root filesystem path comparison: the 1,330 historical paths matched current Git blobs exactly.
- POSIX shell syntax check: **passed** using `sh -n` on the committed script contents.
- Synthetic fixture test: **passed**; created an archive, confirmed regular-file and symlink entries with `tar -tzf`, and confirmed the overwrite guard rejects an existing destination. This validates script behavior only, not the actual LionGameStick root filesystem.
- Firmware build and hardware verification: not applicable / not performed.
- GitHub Actions: no workflow is configured on `main`; no CI result is claimed.

## Limitations and next steps

- Run this script from the repository root on a Linux host with GNU tar.
- Review the archive listing and compare its file modes and symlink targets before using it as a deployment artifact.
- This method can preserve the current tracked runtime tree, but cannot recover files that are absent from both Git history and the current checkout.
