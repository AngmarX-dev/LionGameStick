# Experimental udevadm recovery candidate

This directory is **not part of the runtime root filesystem**.

- Candidate: `sbin-udevadm.armhf`
- Source: existing `usr/bin/udevadm`
- Git blob SHA-1: `7f6547d6a9cead8b46dd5962aeba2f1439cb97ca`
- Size: 227,684 bytes
- ELF: ELF32, little-endian, ARM
- Interpreter: `/lib/ld-linux-armhf.so.3`
- ARM attributes: Cortex-A7 / ARMv7-A / VFPv4 / VFP-register argument convention
- Dependencies: `libblkid.so.1`, `libuuid.so.1`, `libkmod.so.2`, `libz.so.1`, `libc.so.6`, `ld-linux-armhf.so.3`

The candidate is a byte-for-byte copy of the already tracked ARM `usr/bin/udevadm` object. It is preserved separately for comparison only. It has **not** replaced `sbin/udevadm`.

The existing `sbin/udevadm` is ELF64/x86-64, 807,448 bytes, with interpreter `/lib64/ld-linux-x86-64.so.2`. This is a confirmed architecture mismatch for an ARM rootfs. Before promotion, compare package/source versions and verify command behavior on the target. Do not install this candidate into the live rootfs without that validation.
