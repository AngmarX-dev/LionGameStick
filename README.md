# 🦁 LionGameStick

<p align="center">
  <strong>A lightweight embedded Linux gaming platform for Rockchip-based GameStick hardware.</strong>
</p>

<p align="center">
  <a href="https://github.com/AngmarX-dev/LionGameStick">
    <img src="https://img.shields.io/badge/status-active-2ea44f" alt="Status">
  </a>
  <img src="https://img.shields.io/badge/platform-ARM%20%2F%20Rockchip-blue" alt="Platform">
  <img src="https://img.shields.io/badge/base-Buildroot-orange" alt="Buildroot">
  <img src="https://img.shields.io/badge/UI-MiniGUI-purple" alt="MiniGUI">
  <img src="https://img.shields.io/badge/emulation-RetroArch-red" alt="RetroArch">
</p>

## 🎮 What is LionGameStick?

LionGameStick is an embedded Linux gaming environment designed around a compact GameStick-style device. It combines a Buildroot-based userspace, Rockchip display and multimedia support, MiniGUI, RetroArch, and startup scripts that bring the system from boot to a playable interface.

The repository currently contains the extracted runtime filesystem and its system configuration, utilities, assets, and bundled applications.

## ✨ Highlights

- 🐧 **Buildroot Linux base** — built around Buildroot 2018.02-rc3.
- 🖥️ **Rockchip DRM/KMS display stack** — connector and preferred-mode selection for HDMI and internal displays.
- 🎨 **MiniGUI interface** — lightweight graphical environment with fonts, cursors, icons, skins, and display configurations.
- 🕹️ **RetroArch integration** — bundled frontend plus multiple libretro core configurations.
- 🔌 **USB gadget support** — configurable ADB, MTP, mass-storage, ACM, UVC, RNDIS, and audio gadget functions.
- 🌐 **Networking and SSH** — ifupdown networking and Dropbear SSH are included.
- 🔊 **Audio / video tools** — ALSA and GStreamer utilities are available for playback and hardware testing.
- ⚙️ **Embedded startup system** — BusyBox init launches the ordered /etc/init.d boot sequence.

## 🧩 System Architecture

    Bootloader
       │
       ▼
    /init
       │
       └── /sbin/init
              │
              ├── /etc/inittab
              │
              └── /etc/init.d/rcS
                     │
                     ├── Logging
                     ├── udev
                     ├── Mount / filesystem setup
                     ├── Network
                     ├── USB gadget configuration
                     ├── Dropbear SSH
                     └── MiniGUI / Game UI
                                  │
                                  └── RetroArch

## 🗂️ Repository Layout

| Path | Purpose |
|---|---|
| bin/, sbin/ | Core system utilities and init programs |
| etc/ | System, networking, udev, MiniGUI, and RetroArch configuration |
| lib/, lib32/ | Runtime libraries and udev support |
| usr/bin/ | Game UI, multimedia utilities, DRM helpers, and applications |
| usr/local/share/minigui/ | MiniGUI configurations, resources, launch scripts, fonts, icons, and cursors |
| mnt/, sdcard/, userdata/ | Device/runtime storage locations |
| var/, tmp/ | Runtime state, caches, locks, logs, and temporary files |

## 🕹️ Emulator Launching

The bundled start_game.sh script maps numbered game selections to libretro cores and launches RetroArch with the selected content.

Configured core families include:

- Arcade / MAME / FinalBurn
- NES
- Mega Drive / Genesis
- SNES
- Game Boy / Game Boy Advance
- Nintendo 64
- PlayStation
- PC Engine
- WonderSwan
- Nintendo DS
- Atari 2600 / 5200 / 7800

The exact available cores depend on the files installed under /sdcard/retro_lib/.

## 🖥️ Display and HDMI

LionGameStick uses the Linux DRM subsystem and Rockchip modetest utilities to discover connected display connectors and select a preferred mode.

The included display helper supports automatic preference selection with common modes such as:

    1280x720
    1024x*
    1280x1024
    800x600
    1920x1080

MiniGUI configurations are also provided for HDMI-oriented operation.

## 🔌 USB Device Mode

The USB gadget startup script can configure several functions through Linux ConfigFS:

    ADB
    MTP
    USB Mass Storage
    ACM / Serial
    UVC
    RNDIS
    USB Audio

The active gadget composition is controlled through:

    /etc/init.d/.usb_config

## 🛠️ Multimedia

The runtime includes utilities for:

- ALSA playback and testing
- GStreamer audio playback
- GStreamer H.264 video playback
- KMS video output
- Weston / Wayland testing
- OpenGL ES benchmarking with glmark2

## 📌 Current Notes

LionGameStick is an **embedded runtime image**, so many important components are precompiled binaries rather than source code. The repository is therefore useful as a complete system filesystem, reference environment, and base for further hardware-specific development.

Hardware behavior can vary between GameStick boards, display panels, controllers, and USB devices.

## 🚀 Project Direction

The long-term goal is to turn LionGameStick into a cleaner, more maintainable embedded gaming platform with:

- better hardware abstraction
- robust controller and USB compatibility
- improved display detection
- a polished game launcher
- cleaner system configuration
- easier firmware/image rebuilding
- broader emulator support

## 📜 License

See LICENSE for the project license information.

---

<p align="center">
  <strong>🦁 LionGameStick — Small device, big games.</strong>
</p>
