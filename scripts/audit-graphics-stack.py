#!/usr/bin/env python3
"""Read-only inventory of graphics, display and MiniGUI runtime files.

No files are modified. Requires Python 3.8+; readelf is optional.
"""
import argparse
import csv
import hashlib
import os
import re
import shutil
import subprocess
import sys

PATTERN = re.compile(
    r"(mali|egl|gles|gbm|drm|rga|minigui|wayland|weston|opengl|vulkan|"
    r"libgl|kms|rockchip)", re.IGNORECASE
)
CATEGORIES = (
    ("gpu-driver", re.compile(r"mali|panfrost|gpu", re.I)),
    ("egl-gles", re.compile(r"egl|gles|opengl|libgl", re.I)),
    ("drm-gbm-kms", re.compile(r"drm|gbm|kms", re.I)),
    ("rga", re.compile(r"rga", re.I)),
    ("minigui", re.compile(r"minigui", re.I)),
    ("wayland-weston", re.compile(r"wayland|weston", re.I)),
    ("other-display", re.compile(r"rockchip|vulkan", re.I)),
)

def classify(path):
    for name, pattern in CATEGORIES:
        if pattern.search(path):
            return name
    return "other"

def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def elf_info(path, readelf):
    result = {"elf_class": "", "machine": "", "interpreter": "", "needed": ""}
    if not readelf:
        return result
    try:
        proc = subprocess.run(
            [readelf, "-h", "-l", "-d", path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=10, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return result
    output = proc.stdout
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("Class:"):
            result["elf_class"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Machine:"):
            result["machine"] = stripped.split(":", 1)[1].strip()
        elif "Requesting program interpreter:" in stripped:
            result["interpreter"] = stripped.split(":", 1)[1].split("]", 1)[0].strip()
    needed = re.findall(r"Shared library: \[([^]]+)\]", output)
    result["needed"] = ";".join(needed)
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="root filesystem/repository path")
    parser.add_argument("-o", "--output", default="graphics-stack-audit.csv")
    args = parser.parse_args()
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        parser.error("root must be an existing directory")
    readelf = shutil.which("readelf")
    fields = ["path", "category", "kind", "size", "sha256",
              "elf_class", "machine", "interpreter", "needed", "symlink_target"]
    rows = []
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d != ".git")
        for name in sorted(files):
            full = os.path.join(current, name)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            if not PATTERN.search(rel):
                continue
            row = {key: "" for key in fields}
            row["path"] = rel
            row["category"] = classify(rel)
            if os.path.islink(full):
                row["kind"] = "symlink"
                row["symlink_target"] = os.readlink(full)
            elif os.path.isfile(full):
                row["kind"] = "file"
                row["size"] = os.path.getsize(full)
                row["sha256"] = sha256_file(full)
                if open(full, "rb").read(4) == b"\x7fELF":
                    row.update(elf_info(full, readelf))
                    row["kind"] = "elf"
                elif row["size"] == 0:
                    row["kind"] = "empty"
            else:
                row["kind"] = "other"
            rows.append(row)
    rows.sort(key=lambda item: item["path"])
    output = os.path.abspath(args.output)
    if os.path.commonpath([root, output]) == root:
        # Output inside root is permitted only if it is not itself selected by the scan.
        if os.path.exists(output) and os.path.samefile(output, os.path.join(root, output)):
            parser.error("output path resolves to an input file")
    with open(output, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print("Graphics/display candidates: {}".format(len(rows)))
    print("readelf: {}".format(readelf or "not found; ELF ABI fields omitted"))
    print("CSV: {}".format(output))
    return 0

if __name__ == "__main__":
    sys.exit(main())
