import os
import tempfile
import hashlib
import unittest

from src.verifier import FileVerifier


class TestFileVerifier(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.source = os.path.join(self.tmpdir, "source.pdf")
        with open(self.source, "wb") as f:
            f.write(b"Hello, Quantum Computing!")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_get_size(self):
        size = FileVerifier.get_size(self.source)
        self.assertEqual(size, len(b"Hello, Quantum Computing!"))

    def test_compute_sha256(self):
        expected = hashlib.sha256(b"Hello, Quantum Computing!").hexdigest()
        result = FileVerifier.compute_sha256(self.source)
        self.assertEqual(result, expected)

    def test_verify_full_passes(self):
        dest = os.path.join(self.tmpdir, "dest.pdf")
        with open(dest, "wb") as f:
            f.write(b"Hello, Quantum Computing!")
        passed, msg = FileVerifier.verify_full(self.source, dest)
        self.assertTrue(passed)

    def test_verify_full_fails_size(self):
        dest = os.path.join(self.tmpdir, "dest.pdf")
        with open(dest, "wb") as f:
            f.write(b"Different content")
        passed, msg = FileVerifier.verify_full(self.source, dest)
        self.assertFalse(passed)
        self.assertIn("mismatch", msg.lower())

    def test_verify_full_fails_hash(self):
        dest = os.path.join(self.tmpdir, "dest.pdf")
        with open(dest, "wb") as f:
            f.write(b"X" * len(b"Hello, Quantum Computing!"))
        passed, msg = FileVerifier.verify_full(self.source, dest)
        self.assertFalse(passed)

    def test_verify_full_dest_missing(self):
        passed, msg = FileVerifier.verify_full(self.source, "/nonexistent")
        self.assertFalse(passed)

    def test_verify_quick_passes(self):
        dest = os.path.join(self.tmpdir, "dest.pdf")
        with open(dest, "wb") as f:
            f.write(b"Hello, Quantum Computing!")
        passed, msg = FileVerifier.verify_quick(self.source, dest)
        self.assertTrue(passed)

    def test_verify_quick_fails_size(self):
        dest = os.path.join(self.tmpdir, "dest.pdf")
        with open(dest, "wb") as f:
            f.write(b"Short")
        passed, _ = FileVerifier.verify_quick(self.source, dest)
        self.assertFalse(passed)


import shutil

if __name__ == "__main__":
    unittest.main()
