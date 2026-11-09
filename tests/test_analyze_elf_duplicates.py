import csv
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "analyze-elf-duplicates.py"

class DuplicateElfTests(unittest.TestCase):
    def test_groups_identical_elfs_and_ignores_non_elf(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = pathlib.Path(tmp) / "audit.csv"
            output = pathlib.Path(tmp) / "result.json"
            fields = ["path", "kind", "sha256", "size", "machine", "elf_class"]
            rows = [
                {"path":"usr/lib/libEGL.so", "kind":"elf", "sha256":"abc", "size":"100", "machine":"ARM", "elf_class":"ELF32"},
                {"path":"usr/lib/libMali.so", "kind":"elf", "sha256":"abc", "size":"100", "machine":"ARM", "elf_class":"ELF32"},
                {"path":"usr/lib/libdrm.so", "kind":"elf", "sha256":"def", "size":"50", "machine":"ARM", "elf_class":"ELF32"},
                {"path":"etc/graphics.conf", "kind":"file", "sha256":"abc", "size":"20", "machine":"", "elf_class":""},
            ]
            with source.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            proc = subprocess.run([sys.executable, str(SCRIPT), str(source), "-o", str(output)],
                                  text=True, capture_output=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            import json
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["group_count"], 1)
            self.assertEqual(result["duplicate_groups"][0]["count"], 2)
            self.assertEqual(result["duplicate_groups"][0]["distinct_basenames"], 2)

if __name__ == "__main__":
    unittest.main()
