#!/bin/sh
# Safely recover the historical GameStickLite tree from the original archive.
set -eu

ARCHIVE=${1:-archive.7z.001}
DEST=${2:-recovered/GameStickLite}
EXPECTED_GIT_BLOB=053d3f4707cca5348fff73011daebc481dac5dec

fail() {
    printf 'recover-binaries: %s\n' "$*" >&2
    exit 1
}

command -v 7z >/dev/null 2>&1 || fail "7z is required"
command -v git >/dev/null 2>&1 || fail "git is required"
[ -f "$ARCHIVE" ] || fail "archive not found: $ARCHIVE"
[ ! -e "$DEST" ] || fail "destination already exists; refusing to overwrite: $DEST"

actual_blob=$(git hash-object "$ARCHIVE")
[ "$actual_blob" = "$EXPECTED_GIT_BLOB" ] ||
    fail "archive Git blob mismatch (expected $EXPECTED_GIT_BLOB, got $actual_blob)"

parent_dir=$(dirname "$DEST")
mkdir -p "$parent_dir"
tmp_dir=$(mktemp -d "$parent_dir/.liongamestick-recovery.XXXXXX")
cleanup() {
    rm -rf "$tmp_dir"
}
trap cleanup EXIT HUP INT TERM

7z t "$ARCHIVE" >/dev/null || fail "7-Zip integrity test failed"
7z x -y "$ARCHIVE" "-o$tmp_dir" >/dev/null ||
    fail "archive extraction failed"
[ -d "$tmp_dir/GameStickLite" ] ||
    fail "expected GameStickLite/ directory was not found in the archive"

mv "$tmp_dir/GameStickLite" "$DEST"
printf 'Recovered tree: %s\n' "$DEST"
