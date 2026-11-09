import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "audit-all-binaries.py"

class BinaryInventoryTests(unittest.TestCase):
    def test_magic_signatures_and_unknown_binary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            root.mkdir()
            (root / "tool").write_bytes(b"\x7fELF" + b"\x00" * 32)
            (root / "archive.zip").write_bytes(b"PK\x03\x04" + b"payload")
            (root / "opaque.dat").write_bytes(bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]))
            (root / "readme.txt").write_text("ordinary readable text", encoding="utf-8")
            (root / "link.so").symlink_to("tool")
            csv_path = pathlib.Path(tmp) / "inventory.csv"
            json_path = pathlib.Path(tmp) / "elf.json"
            proc = subprocess.run([sys.executable, str(SCRIPT), str(root),
                                   "--csv", str(csv_path), "--json", str(json_path)],
                                  text=True, capture_output=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            import csv
            with csv_path.open(newline="", encoding="utf-8") as f:
                rows = {r["path"]: r for r in csv.DictReader(f)}
            self.assertEqual(rows["tool"]["classification"], "ELF")
            self.assertEqual(rows["archive.zip"]["classification"], "ZIP")
            self.assertEqual(rows["opaque.dat"]["classification"], "BINARY_UNRECOGNIZED")
            self.assertEqual(rows["link.so"]["kind"], "symlink")
            self.assertNotIn("readme.txt", rows)
            result = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(result["elf_count"], 1)

if __name__ == "__main__":
    unittest.main()
