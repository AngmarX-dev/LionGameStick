#!/usr/bin/env python3
"""Summarize identical ELF payloads from audit-graphics-stack.py CSV output."""
import argparse
import csv
import json
import os
from collections import defaultdict

def analyze(path):
    groups = defaultdict(list)
    with open(path, newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row.get("kind") == "elf" and row.get("sha256"):
                groups[row["sha256"]].append(row)
    findings = []
    for digest, entries in sorted(groups.items()):
        if len(entries) < 2:
            continue
        names = sorted({os.path.basename(item["path"]) for item in entries})
        findings.append({
            "sha256": digest,
            "size": int(entries[0].get("size") or 0),
            "machine": entries[0].get("machine", ""),
            "class": entries[0].get("elf_class", ""),
            "count": len(entries),
            "distinct_basenames": len(names),
            "paths": sorted(item["path"] for item in entries),
            "assessment": (
                "review-required: identical ELF payload under distinct library names"
                if len(names) > 1 else
                "likely-version-or-multilib-duplicate; verify packaging and ABI"
            ),
        })
    return findings

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file")
    parser.add_argument("-o", "--output", default="elf-duplicate-audit.json")
    args = parser.parse_args()
    findings = analyze(args.csv_file)
    with open(args.output, "w", encoding="utf-8") as stream:
        json.dump({"duplicate_groups": findings, "group_count": len(findings)},
                  stream, indent=2)
        stream.write("\n")
    print("Duplicate ELF groups: {}".format(len(findings)))
    for item in findings:
        print("{} bytes | {} paths | {} distinct names | {}".format(
            item["size"], item["count"], item["distinct_basenames"], item["assessment"]))
    print("JSON: {}".format(os.path.abspath(args.output)))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
