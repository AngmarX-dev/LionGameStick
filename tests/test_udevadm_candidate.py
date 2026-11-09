import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "usr" / "bin" / "udevadm"
CANDIDATE = ROOT / "recovery-candidates" / "udevadm" / "sbin-udevadm.armhf"

class UdevadmCandidateTests(unittest.TestCase):
    def test_candidate_is_exact_copy_of_existing_armhf_udevadm(self):
        source = SOURCE.read_bytes()
        candidate = CANDIDATE.read_bytes()
        self.assertEqual(candidate, source)
        self.assertEqual(candidate[:4], b"\x7fELF")
        self.assertEqual(candidate[4], 1, "candidate must be ELF32")
        self.assertEqual(candidate[5], 1, "candidate must be little-endian")
        self.assertEqual(candidate[18:20], b"\x28\x00", "e_machine must be EM_ARM")
        self.assertIn(b"/lib/ld-linux-armhf.so.3", candidate)

if __name__ == "__main__":
    unittest.main()
