#!/bin/sh
# Rebuild a portable archive from the already tracked runtime filesystem.
set -eu

DEST=${1:-LionGameStick-rootfs.tar.gz}
[ ! -e "$DEST" ] || {
    printf 'repack-rootfs: refusing to overwrite %s\n' "$DEST" >&2
    exit 1
}

ROOT_ITEMS="bin data etc init lib lib32 linuxrc mnt sbin sdcard tmp usr userdata var"
for item in $ROOT_ITEMS; do
    [ -e "$item" ] || {
        printf 'repack-rootfs: required rootfs path is missing: %s\n' "$item" >&2
        exit 1
    }
done

tmp_file=$(mktemp "${DEST}.tmp.XXXXXX")
cleanup() {
    rm -f "$tmp_file"
}
trap cleanup EXIT HUP INT TERM

# Archive only the known runtime filesystem paths; do not include .git or reports.
tar -czpf "$tmp_file" -- $ROOT_ITEMS
tar -tzf "$tmp_file" >/dev/null
mv "$tmp_file" "$DEST"
trap - EXIT HUP INT TERM
printf 'Root filesystem archive created: %s\n' "$DEST"
