# udevadm compatibility assessment

Date: 2026-11-10
Scope: static compatibility review only; no target binary was executed.

## Findings

- The ARM candidate `recovery-candidates/udevadm/sbin-udevadm.armhf` is byte-for-byte identical to the tracked `usr/bin/udevadm` (Git blob SHA-1 `7f6547d6a9cead8b46dd5962aeba2f1439cb97ca`).
- Candidate metadata from the prior ELF audit: ELF32/ARM, little-endian, ARMv7-A/Cortex-A7, VFPv4 hard-float, interpreter `/lib/ld-linux-armhf.so.3`.
- Candidate strings contain `udev-3.2.7`. The paired daemon `sbin/udevd` contains `starting version 3.2.7` and `starting eudev-3.2.7`. This is strong evidence that the candidate belongs to the same eudev release family as the daemon; it is not a substitute for a package manifest or source-build provenance.
- The candidate's recorded DT_NEEDED set is `libblkid.so.1`, `libuuid.so.1`, `libkmod.so.2`, `libz.so.1`, and `libc.so.6`. Matching ARM libraries and the ARM hard-float loader are present in the repository tree under `lib/` and `usr/lib/` (with additional aliases under `lib32/` and `usr/lib32/`).
- The init script `etc/init.d/S10udev` invokes `/sbin/udevd -d`, then calls `udevadm trigger --type=subsystems --action=add`, `udevadm trigger --type=devices --action=add`, `udevadm settle --timeout=30`, and on stop `udevadm control --stop-exec-queue`. The candidate's embedded command/help strings include trigger, settle, and control functionality and the relevant option names.
- `etc/profile` defines `PATH=/bin:/sbin:/usr/bin:/usr/sbin`, but this file is for login shells. BusyBox init executes `/etc/init.d/rcS` directly and the repository's init scripts do not set PATH before `S10udev`. The effective PATH inherited by init must therefore be confirmed on the target; the login profile alone does not prove it.

## Assessment

The ARM candidate is a substantially stronger replacement candidate than an arbitrary ARM executable: architecture, hard-float interpreter, required libraries, command surface, and eudev release string align with the paired ARM daemon. The x86-64 `sbin/udevadm` remains an architecture outlier and links against systemd-shared-261, which does not match the eudev 3.2.7 daemon family.

## Decision

Do not overwrite `sbin/udevadm` yet. Keep the candidate isolated. Before promotion:
1. Confirm the exact effective PATH in BusyBox init on the physical device or by inspecting the exact BusyBox build/configuration.
2. Run candidate `--version`, `trigger --dry-run`, `settle`, and `control` smoke tests in a recoverable target environment.
3. Verify hotplug events, device-node creation, and shutdown behavior with logs.
4. Confirm the original x86-64 file is not intentionally used by a host-side packaging/build process.

Firmware build and physical-device tests were not available in this audit. No runtime file was modified.
