# 005 — Rockchip Graphics Stack Recovery Audit

- **Date:** 2026-11-09
- **Objective:** Inspect the graphics/display runtime inventory and add a reproducible, read-only audit method without replacing any binary.
- **Work branch:** `recovery/05-rockchip-graphics-audit`
- **Report location:** `main` branch.

## Initial state

Main head before this report: `3e89841be432a54d06ec57a94cdfcc7386b4dc35`. The repository README describes a Buildroot-based runtime with Rockchip DRM/KMS, MiniGUI, RetroArch, and multimedia components. These are repository claims; no physical hardware compatibility is inferred from names alone.

## Graphics inventory findings

The recursive Git tree search found 173 paths matching graphics/display-related names, including libraries, MiniGUI configs/resources, DRM rules, and helper scripts.

Notable library groups:

- `usr/lib/` and `usr/lib32/`: EGL, GLESv1, GLESv2, Mali, Mali OpenCL, GBM, libdrm, and libdrm_rockchip names.
- Many versioned/unversioned names are ordinary regular-file blobs in Git, not symlinks.
- EGL/GLES/Mali/GBM-named files across both library directories share Git blob SHA `5f488634502f489b542251f0be8d3df2bdf332d7` and size 929,956 bytes.
- libdrm names share blob SHA `e6d3ba7a36366ebe2f29d3a0dfeaf041a7db6e15` (46,680 bytes); libdrm_rockchip names share `4823fe81eb5f74942b930ded90081e58cf3a32a3` (9,448 bytes).
- MiniGUI library names share a separate 1,248,260-byte blob.

Identical hashes do not prove files are correct or incorrect. In particular, identical content in `usr/lib` and `usr/lib32` requires ELF/ABI inspection. No binary replacement was made.

## Implementation on the single work branch

Branch: `recovery/05-rockchip-graphics-audit`

- Added `scripts/audit-graphics-stack.py`: read-only inventory, SHA-256, symlink metadata, ELF detection and optional readelf metadata.
- Added `tests/test_audit_graphics_stack.py`: synthetic fixture test for ELF-magic detection, hashing, symlink target, path filtering and CSV output.
- Added `.github/workflows/graphics-stack-audit.yml`: runs Python 3.12 syntax compilation, fixture tests and CLI help on pushes to this work branch, pull requests targeting main, and manual dispatch. Permissions are read-only.

## Validation status

- The workflow file and test source are committed on the work branch.
- GitHub Actions run query for commit `8d7a4cbc264505e75f99e338c9ea68c7e6a66dd2`: **zero workflow runs returned** at the time of this report.
- Commit status query: **no status checks returned**.
- Therefore CI is **not verified** and this task is not marked CI-complete. The workflow may be disabled by repository settings or may not have been scheduled; this cannot be distinguished with the available read access.
- Local Python compile/test execution in this environment: **not performed**.
- Actual firmware binary readelf inspection: **not completed**; raw binary bytes are unavailable through the GitHub text endpoint.
- Firmware build: **not run**; no firmware sources or build configuration changed.
- Hardware verification: **not performed**.

## Next steps

1. In GitHub, open **Settings → Actions → General** and confirm Actions are enabled for the repository.
2. Open the Actions tab and manually run **Graphics stack audit**, or push a new commit to `recovery/05-rockchip-graphics-audit`.
3. Confirm the run is completed and green before treating the validation as passed.
4. On a Linux checkout, run `python3 scripts/audit-graphics-stack.py . -o graphics-stack-audit.csv` and share the CSV.
5. Verify SoC/GPU generation, ELF class/machine, endianness, loader, libc, SONAMEs, DT_NEEDED, and kernel/userspace driver compatibility before recovering or replacing any graphics library.
