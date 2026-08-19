import os
import tempfile
import shutil
import unittest

from src.config import Config
from src.logger import SyncLogger
from src.synchronizer import MaterialSynchronizer


class StubLogger:
    def __init__(self):
        self.messages = []

    def info(self, msg):
        self.messages.append(("info", msg))

    def warn(self, msg):
        self.messages.append(("warn", msg))

    def error(self, msg):
        self.messages.append(("error", msg))

    def debug(self, msg):
        self.messages.append(("debug", msg))


class TestSynchronizer(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.src_dir = os.path.join(self.tmpdir, "source")
        self.dst_dir = os.path.join(self.tmpdir, "dest")
        os.makedirs(self.src_dir)
        os.makedirs(self.dst_dir)

        self.config = Config.__new__(Config)
        self.config.data = {
            "recursive": True,
            "verify_hash": True,
            "copy_entire_directory": False,
        }
        self.logger = StubLogger()
        self.sync = MaterialSynchronizer(self.config, self.logger)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _create_file(self, path, content=b"test data"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(content)

    def test_discover_files_recursively(self):
        self._create_file(os.path.join(self.src_dir, "a.pdf"), b"aaa")
        self._create_file(os.path.join(self.src_dir, "sub/b.pptx"), b"bbb")
        self._create_file(os.path.join(self.src_dir, "sub/c.txt"), b"txt")
        files = self.sync.discover_files(self.src_dir)
        names = [os.path.basename(f) for f in files]
        self.assertIn("a.pdf", names)
        self.assertIn("b.pptx", names)
        self.assertIn("c.txt", names)

    def test_discover_files_non_recursive(self):
        self.config.data["recursive"] = False
        self._create_file(os.path.join(self.src_dir, "a.pdf"))
        self._create_file(os.path.join(self.src_dir, "sub/b.pdf"))
        files = self.sync.discover_files(self.src_dir)
        self.assertEqual(len(files), 1)

    def test_sync_new_files(self):
        self._create_file(os.path.join(self.src_dir, "Lecture.pdf"))
        stats, dest = self.sync.sync(self.src_dir, self.dst_dir)
        self.assertEqual(stats["new"], 1)
        self.assertEqual(stats["updated"], 0)
        self.assertEqual(stats["unchanged"], 0)
        self.assertTrue(os.path.exists(os.path.join(dest, "Lecture.pdf")))

    def test_sync_single_file_source(self):
        src = os.path.join(self.tmpdir, "Lecture.pdf")
        self._create_file(src)

        stats, dest = self.sync.sync(src, self.dst_dir)

        self.assertEqual(stats["discovered"], 1)
        self.assertEqual(stats["new"], 1)
        self.assertEqual(dest, self.dst_dir)
        self.assertTrue(os.path.exists(os.path.join(self.dst_dir, "Lecture.pdf")))

    def test_sync_single_file_source_accepts_any_extension(self):
        src = os.path.join(self.tmpdir, "script.py")
        self._create_file(src)

        stats, dest = self.sync.sync(src, self.dst_dir)

        self.assertEqual(stats["discovered"], 1)
        self.assertEqual(stats["new"], 1)
        self.assertEqual(dest, self.dst_dir)
        self.assertTrue(os.path.exists(os.path.join(self.dst_dir, "script.py")))

    def test_sync_unchanged_files(self):
        src = os.path.join(self.src_dir, "Lecture.pdf")
        self._create_file(src)
        stats, dest = self.sync.sync(self.src_dir, self.dst_dir)
        self.assertEqual(stats["new"], 1)

        stats2, _ = self.sync.sync(self.src_dir, self.dst_dir)
        self.assertEqual(stats2["unchanged"], 1)
        self.assertEqual(stats2["new"], 0)

    def test_sync_updated_files(self):
        src = os.path.join(self.src_dir, "Lecture.pdf")
        self._create_file(src, b"version1")
        self.sync.sync(self.src_dir, self.dst_dir)

        with open(src, "wb") as f:
            f.write(b"version2_longer")
        stats, _ = self.sync.sync(self.src_dir, self.dst_dir)
        self.assertEqual(stats["updated"], 1)

    def test_sync_preserves_directory_structure(self):
        self._create_file(os.path.join(self.src_dir, "top.pdf"))
        self._create_file(os.path.join(self.src_dir, "sub", "nested.pdf"))
        stats, dest = self.sync.sync(self.src_dir, self.dst_dir)
        self.assertTrue(os.path.exists(os.path.join(dest, "top.pdf")))
        self.assertTrue(os.path.exists(os.path.join(dest, "sub", "nested.pdf")))

    def test_sync_empty_directory(self):
        stats, dest = self.sync.sync(self.src_dir, self.dst_dir)
        self.assertEqual(stats["discovered"], 0)

    def test_sync_verifies_copied_files(self):
        self._create_file(os.path.join(self.src_dir, "Lecture.pdf"))
        stats, dest = self.sync.sync(self.src_dir, self.dst_dir)
        failed = self.sync.verify_copied_files(self.src_dir, dest)
        self.assertEqual(len(failed), 0)

    def test_verify_single_file_source(self):
        src = os.path.join(self.tmpdir, "Lecture.pdf")
        self._create_file(src)
        _, dest = self.sync.sync(src, self.dst_dir)

        failed = self.sync.verify_copied_files(src, dest)

        self.assertEqual(len(failed), 0)


if __name__ == "__main__":
    unittest.main()
