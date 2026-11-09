# 001 — Binary Recovery Audit and Git-History Archive Restoration

- **Date:** 2026-11-09
- **Objective:** Recover binary source material without modifying `main`, using Git object history as the first recovery method.
- **Branch:** `recovery/01-git-history-archive`

## Initial state

- Default branch: `main`
- Audited main commit: `3e89841be432a54d06ec57a94cdfcc7386b4dc35`
- Main tree: 1,332 blob entries.
- The historical extraction commit `4aa4010ea9b650f93f8cca35708eb0388aec5196` contains `archive.7z.001` and an extracted filesystem.
- The later cleanup commits removed the archive and extraction workflow; the current root contains the extracted filesystem.

## Recovery findings

A recursive comparison of the historical `extracted/GameStickLite/` tree against the current root found **1,330 historical files and zero missing or changed blob SHA values**. Thus, the tracked binary files from that historical filesystem are already present in `main`; blindly replacing them would add risk without recovering anything new.

The original archive was recoverable directly from Git history:

- Historical path: `archive.7z.001`
- Size: `23,657,146` bytes
- Git blob SHA-1: `053d3f4707cca5348fff73011daebc481dac5dec`

This branch restores that exact Git blob at the repository root. No archive bytes were re-encoded or rebuilt.

## Files changed

- Added `archive.7z.001` from its original historical Git blob.
- Added `docs/reports/README.md`.
- Added this report.

## Validation

- Historical tree comparison: **1,330 / 1,330 paths matched by exact Git blob SHA; 0 mismatches**.
- Archive object provenance: exact historical blob SHA and byte size recorded above.
- Binary download and `7z t` were **not run** in this environment; the GitHub connector does not provide binary blob download content.
- Firmware build: **not run**; this branch restores an archive and does not change firmware sources or toolchain configuration.
- GitHub Actions: no workflow directory is present on `main` (the contents endpoint returned 404); no CI result is claimed.
- Hardware verification: **not performed**.

## Limitations and next steps

- The archive is a single tracked `.001` part. Its successful extraction depends on any additional volumes required by the archive being available; verify with 7-Zip before relying on it.
- Compare this branch with the verified-extraction branch before merging anything.
- Do not replace the already matching root binaries unless a later integrity check proves corruption.
