# 002 — Verified, Non-Destructive Archive Extraction

- **Date:** 2026-11-09
- **Objective:** Add a staged extraction method with integrity and overwrite safeguards.
- **Work branch:** `recovery/02-verified-extraction`

## Initial state

The historical extracted tree's 1,330 files all matched the current root by Git blob SHA. The original archive was recovered as blob `053d3f4707cca5348fff73011daebc481dac5dec` (23,657,146 bytes).

## Implementation

Added `scripts/recover-binaries.sh` and restored the exact archive. The script checks for Git and 7-Zip, verifies the archive Git blob SHA-1, runs the archive integrity test, extracts to a temporary staging directory, checks for the expected `GameStickLite/` directory, and refuses to overwrite an existing destination.

## Validation and status

- Historical tree comparison: **1,330/1,330 exact blob matches**.
- POSIX shell syntax check (`sh -n`): **passed**.
- Actual extraction and archive CRC test: **not run**; archive bytes were not locally available to the execution environment.
- Firmware build: **not run**.
- GitHub Actions: no workflow configured on `main`; no CI success claimed.
- Hardware verification: **not performed**.

## Limitations / next steps

Run on a host with Git and 7-Zip. If the archive is multi-volume, provide all required parts. Keep extracted output separate until architecture, ABI, permissions, symlinks, and runtime compatibility are checked.
