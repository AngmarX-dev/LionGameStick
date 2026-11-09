#!/usr/bin/env python3
"""Read-only inventory of firmware binaries, ELF ABI metadata and dependencies."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

FIELDS = [
    "path", "size_bytes", "sha256", "kind", "elf_class",
    "endianness", "machine", "interpreter", "needed_libraries",
    "symlink_target",
]


def run_tool(args: list[str]) -> str:
    try:
        result = subprocess.run(
            args, check=False, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True,
        )
        return result.stdout if result.returncode == 0 else ""
    except OSError:
        return ""


def inspect(path: Path, root: Path, file_cmd: str | None,
            readelf_cmd: str | None) -> dict[str, str | int]:
    rel = path.relative_to(root).as_posix()
    if path.is_symlink():
        return {
            "path": rel, "size_bytes": 0, "sha256": "",
            "kind": "symlink", "elf_class": "", "endianness": "",
            "machine": "", "interpreter": "", "needed_libraries": "",
            "symlink_target": str(path.readlink()),
        }

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        magic = stream.read(4)
        digest.update(magic)
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)

    kind = run_tool([file_cmd, "-b", str(path)]) if file_cmd else ""
    if not kind:
        kind = "ELF" if magic == b"\\x7fELF" else "unknown (file utility unavailable)"

    elf_class = endianness = machine = interpreter = ""
    needed: list[str] = []
    if magic == b"\\x7fELF" and readelf_cmd:
        header = run_tool([readelf_cmd, "-h", str(path)])
        for line in header.splitlines():
            stripped = line.strip()
            if stripped.startswith("Class:"):
                elf_class = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Data:"):
                endianness = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Machine:"):
                machine = stripped.split(":", 1)[1].strip()

        program_headers = run_tool([readelf_cmd, "-l", str(path)])
        for line in program_headers.splitlines():
            if "Requesting program interpreter:" in line:
                interpreter = line.split("Requesting program interpreter:", 1)[1]
                interpreter = interpreter.strip().strip("[]")

        dynamic = run_tool([readelf_cmd, "-d", str(path)])
        for line in dynamic.splitlines():
            if "(NEEDED)" in line and "[" in line and "]" in line:
                needed.append(line.split("[", 1)[1].split("]", 1)[0])

    return {
        "path": rel,
        "size_bytes": path.stat().st_size,
        "sha256": digest.hexdigest(),
        "kind": kind,
        "elf_class": elf_class,
        "endianness": endianness,
        "machine": machine,
        "interpreter": interpreter,
        "needed_libraries": ";".join(sorted(set(needed))),
        "symlink_target": "",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".",
                        help="firmware checkout root (default: current directory)")
    parser.add_argument("-o", "--output", default="binary-audit.csv",
                        help="CSV output path (default: binary-audit.csv)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    file_cmd = shutil.which("file")
    readelf_cmd = shutil.which("readelf")
    output = Path(args.output).resolve()
    rows = []
    for path in sorted(root.rglob("*")):
        if ".git" in path.relative_to(root).parts:
            continue
        if path.resolve() == output:
            continue
        if path.is_symlink() or path.is_file():
            try:
                rows.append(inspect(path, root, file_cmd, readelf_cmd))
            except (OSError, ValueError) as exc:
                rows.append({
                    "path": path.relative_to(root).as_posix(),
                    "size_bytes": "", "sha256": "", "kind": f"inspection error: {exc}",
                    "elf_class": "", "endianness": "", "machine": "",
                    "interpreter": "", "needed_libraries": "", "symlink_target": "",
                })

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    elf_count = sum(1 for row in rows if row["elf_class"])
    summary = {
        "root": str(root),
        "files_and_symlinks": len(rows),
        "elf_files_inspected": elf_count,
        "file_utility_available": bool(file_cmd),
        "readelf_available": bool(readelf_cmd),
        "csv": str(output),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
