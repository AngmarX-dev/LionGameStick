# 002 — Verified, Non-Destructive Archive Extraction

- **Date:** 2026-11-09
- **Objective:** Provide a second recovery method: re-extract the historical archive into a separate staging destination with integrity and overwrite safeguards.
- **Branch:** `recovery/02-verified-extraction`

## Initial state and audit

The audit found that all 1,330 files in the historical extracted filesystem already match the current root by Git blob SHA. The original archive remains recoverable from Git history as blob `053d3f4707cca5348fff73011daebc481dac5dec` (23,657,146 bytes).

## Implementation

- Restored the exact historical `archive.7z.001` blob.
- Added `scripts/recover-binaries.sh`.
- The script checks for 7-Zip, checks the archive's Git blob SHA-1, runs the 7-Zip archive test, extracts into a temporary directory, requires the expected `GameStickLite/` directory, and refuses to overwrite an existing destination.
- Extraction is staged outside the live filesystem; the script does not write into `/`, `/usr`, or the repository's current runtime directories.

## Validation

- Historical tree comparison: **1,330 / 1,330 paths matched by exact Git blob SHA; 0 mismatches**.
- Script execution and 7-Zip CRC test: **not run** because the binary archive is not available as a local file in this environment.
- Shell static analysis: **not run**; no ShellCheck result is claimed.
- Firmware build: **not run**; this is a recovery utility, not a firmware source change.
- GitHub Actions: no workflow directory is present on `main`; no CI result is claimed.
- Hardware verification: **not performed**.

## Limitations and next steps

- The archive may require additional split-volume files; the script intentionally fails if 7-Zip cannot validate the supplied archive.
- Run the script on a Linux host with 7-Zip and Git installed, then compare the extracted tree against the tracked filesystem before considering any replacement.
- Keep this recovery output separate until ABI, architecture, file mode, symlink, and runtime compatibility checks are complete.
