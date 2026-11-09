#!/usr/bin/env python3
"""Read-only inventory and metadata analysis for every binary-like repository file.

The scanner never executes target binaries and never modifies scanned files.
Requires Python 3.8+; GNU readelf is optional but strongly recommended.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

MAGIC = [
    (b"\x7fELF", "ELF"),
    (b"\x7fE\x45\x4c\x46", "ELF"),
    (b"PK\x03\x04", "ZIP"),
    (b"7z\xbc\xaf\x27\x1c", "7Z"),
    (b"\x1f\x8b", "GZIP"),
    (b"BZh", "BZIP2"),
    (b"\xfd7zXZ\x00", "XZ"),
    (b"\x28\xb5\x2f\xfd", "ZSTD"),
    (b"hsqs", "SQUASHFS"),
    (b"\x68\x73\x71\x73", "SQUASHFS"),
    (b"ANDROID!", "ANDROID_BOOT_IMAGE"),
    (b"U-Boot", "UBOOT_TEXT"),
    (b"\x27\x05\x19\x56", "UIMAGE"),
    (b"\xd0\x0d\xfe\xed", "FLAT_DEVICE_TREE"),
    (b"\x89PNG\r\n\x1a\n", "PNG"),
    (b"\xff\xd8\xff", "JPEG"),
    (b"GIF87a", "GIF"),
    (b"GIF89a", "GIF"),
    (b"\x00asm", "WASM"),
]
EXTENSIONS = {
    ".so": "SHARED_LIBRARY_CANDIDATE", ".ko": "KERNEL_MODULE_CANDIDATE",
    ".bin": "BINARY_CANDIDATE", ".img": "DISK_IMAGE_CANDIDATE",
    ".dtb": "DEVICE_TREE_CANDIDATE", ".dtbo": "DEVICE_TREE_OVERLAY_CANDIDATE",
    ".fw": "FIRMWARE_CANDIDATE", ".rom": "ROM_CANDIDATE",
    ".nes": "ROM_CANDIDATE", ".gba": "ROM_CANDIDATE", ".gb": "ROM_CANDIDATE",
    ".zip": "ARCHIVE_CANDIDATE", ".7z": "ARCHIVE_CANDIDATE",
}
STRING_RE = re.compile(rb"[\x20-\x7e]{6,}")

def digest_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def readelf_metadata(path, readelf):
    meta = {"elf_class": "", "endianness": "", "machine": "", "os_abi": "",
            "abi_version": "", "type": "", "interpreter": "", "soname": "",
            "needed": [], "build_id": "", "arm_attributes": [],
            "defined_symbols": 0, "undefined_symbols": 0, "readelf_status": ""}
    if not readelf:
        meta["readelf_status"] = "readelf-unavailable"
        return meta
    try:
        p = subprocess.run([readelf, "-h", "-l", "-d", "-n", "-A", "-Ws", path],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           universal_newlines=True, timeout=20, check=False)
    except subprocess.TimeoutExpired:
        meta["readelf_status"] = "timeout"
        return meta
    except OSError as exc:
        meta["readelf_status"] = "error:" + str(exc)
        return meta
    text = p.stdout
    meta["readelf_status"] = "ok" if p.returncode == 0 else "readelf-error"
    patterns = {
        "elf_class": r"^\s*Class:\s*(.+)$",
        "endianness": r"^\s*Data:\s*(.+)$",
        "machine": r"^\s*Machine:\s*(.+)$",
        "os_abi": r"^\s*OS/ABI:\s*(.+)$",
        "abi_version": r"^\s*ABI Version:\s*(.+)$",
        "type": r"^\s*Type:\s*(.+)$",
        "interpreter": r"Requesting program interpreter:\s*([^\]]+)",
        "soname": r"\(SONAME\).*?\[([^]]+)\]",
        "build_id": r"Build ID:\s*([0-9a-fA-F]+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.M)
        if match:
            meta[key] = match.group(1).strip()
    meta["needed"] = re.findall(r"\(NEEDED\).*?\[([^]]+)\]", text)
    meta["arm_attributes"] = [line.strip() for line in text.splitlines()
                              if "Tag_" in line and ("Tag_CPU" in line or "Tag_ABI" in line or "Tag_FP" in line)]
    for line in text.splitlines():
        if re.search(r"\s+\d+:\s", line) and " FUNC " in line:
            if " UND " in line:
                meta["undefined_symbols"] += 1
            else:
                meta["defined_symbols"] += 1
    return meta

def classify(path, header, sample, size):
    for magic, label in MAGIC:
        if header.startswith(magic):
            return label
    ext = os.path.splitext(path)[1].lower()
    if ext in EXTENSIONS:
        return EXTENSIONS[ext]
    if size == 0:
        return "EMPTY"
    if b"\x00" in sample or (sample and sum(c < 9 or 13 < c < 32 for c in sample) / len(sample) > 0.08):
        return "BINARY_UNRECOGNIZED"
    return None

def scan(root, readelf, max_strings):
    rows, elf_details = [], []
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in (".git", "__pycache__"))
        for name in sorted(files):
            full = os.path.join(current, name)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            row = {"path": rel, "kind": "", "size": 0, "sha256": "",
                   "classification": "", "symlink_target": ""}
            if os.path.islink(full):
                row["kind"] = "symlink"
                row["symlink_target"] = os.readlink(full)
                row["classification"] = "SYMLINK"
                rows.append(row)
                continue
            if not os.path.isfile(full):
                continue
            size = os.path.getsize(full)
            with open(full, "rb") as f:
                header = f.read(16)
                f.seek(0)
                sample = f.read(min(size, 65536))
            classification = classify(rel, header, sample, size)
            if classification is None:
                continue
            row.update({"kind": "file", "size": size, "sha256": digest_file(full),
                        "classification": classification})
            rows.append(row)
            if classification == "ELF":
                detail = {"path": rel, "size": size, "sha256": row["sha256"],
                          "metadata": readelf_metadata(full, readelf),
                          "strings": [s.decode("ascii", "replace") for s in STRING_RE.findall(sample)[:max_strings]]}
                elf_details.append(detail)
    rows.sort(key=lambda x: x["path"])
    elf_details.sort(key=lambda x: x["path"])
    return rows, elf_details

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--csv", default="binary-inventory.csv")
    parser.add_argument("--json", default="elf-deep-analysis.json")
    parser.add_argument("--max-strings", type=int, default=30)
    args = parser.parse_args()
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        parser.error("root must be an existing directory")
    if args.max_strings < 0 or args.max_strings > 500:
        parser.error("--max-strings must be between 0 and 500")
    readelf = shutil.which("readelf")
    rows, elfs = scan(root, readelf, args.max_strings)
    with open(args.csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "kind", "size", "sha256", "classification", "symlink_target"])
        writer.writeheader()
        writer.writerows(rows)
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump({"root": ".", "readelf": readelf or None, "binary_candidate_count": len(rows),
                   "elf_count": len(elfs), "files": elfs}, f, indent=2)
        f.write("\n")
    counts = {}
    for row in rows:
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1
    print("Binary-like entries: {}".format(len(rows)))
    print("ELF files deeply inspected: {}".format(len(elfs)))
    print("Classification counts: {}".format(json.dumps(counts, sort_keys=True)))
    print("readelf: {}".format(readelf or "unavailable"))
    return 0

if __name__ == "__main__":
    sys.exit(main())
