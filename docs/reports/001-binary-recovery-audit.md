# 001 — Binary Recovery Audit and Git-History Archive Restoration

- **Date:** 2026-11-09
- **Objective:** Recover binary source material without modifying the live runtime tree.
- **Work branch:** `recovery/01-git-history-archive`

## Initial state and findings

Audited `main` at `3e89841be432a54d06ec57a94cdfcc7386b4dc35`. A recursive comparison found **1,330 historical files** under `extracted/GameStickLite/` and zero missing or changed Git blob SHA values in the current root. The tracked binaries from that snapshot were already present; the removed artifact was the original archive.

The archive was recovered from Git history as the exact original blob:

- Path: `archive.7z.001`
- Size: `23,657,146` bytes
- Git blob SHA-1: `053d3f4707cca5348fff73011daebc481dac5dec`

## Files and implementation

The recovery branch restored the archive without re-encoding it and added documentation. No existing root binary was overwritten.

## Validation and status

- Historical tree comparison: **1,330/1,330 exact blob matches**.
- Binary download and `7z t`: **not run** in the GitHub connector environment.
- Firmware build: **not run**; this is an archive restoration.
- GitHub Actions: no workflow configured on `main`; no CI success claimed.
- Hardware verification: **not performed**.

## Limitations / next steps

The archive may require additional split volumes. Validate it with 7-Zip on a local Linux/Windows machine before relying on extraction. Do not replace already matching runtime binaries without a verified integrity or compatibility failure.
