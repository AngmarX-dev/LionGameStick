import csv
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "audit-graphics-stack.py"

class GraphicsAuditTests(unittest.TestCase):
    def test_fixture_inventory_and_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "root"
            root.mkdir()
            libdir = root / "usr" / "lib"
            libdir.mkdir(parents=True)
            elf = libdir / "libEGL.so.1"
            elf.write_bytes(b"\x7fELF" + b"fixture-payload")
            link = libdir / "libGLES.so"
            link.symlink_to("libEGL.so.1")
            unrelated = root / "notes.txt"
            unrelated.write_text("not a graphics file", encoding="utf-8")
            output = pathlib.Path(tmp) / "audit.csv"

            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(root), "-o", str(output)],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with output.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            by_path = {row["path"]: row for row in rows}
            self.assertIn("usr/lib/libEGL.so.1", by_path)
            self.assertEqual(by_path["usr/lib/libEGL.so.1"]["kind"], "elf")
            self.assertTrue(by_path["usr/lib/libEGL.so.1"]["sha256"])
            self.assertIn("usr/lib/libGLES.so", by_path)
            self.assertEqual(by_path["usr/lib/libGLES.so"]["kind"], "symlink")
            self.assertEqual(by_path["usr/lib/libGLES.so"]["symlink_target"], "libEGL.so.1")
            self.assertNotIn("notes.txt", by_path)

if __name__ == "__main__":
    unittest.main()
