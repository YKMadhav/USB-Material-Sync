import os
import tempfile
import shutil
import unittest

from src.path_validator import PathValidator


class TestPathValidator(unittest.TestCase):
    def test_valid_relative_path(self):
        result = PathValidator.validate_relative_path("Quantum Computing/Unit 3")
        self.assertEqual(result, os.path.normpath("Quantum Computing/Unit 3"))

    def test_valid_with_forward_slash(self):
        result = PathValidator.validate_relative_path("folder/subfolder/file")
        self.assertIn("folder", result)

    def test_valid_with_backslash(self):
        result = PathValidator.validate_relative_path("folder\\subfolder\\file")
        self.assertIn("folder", result)

    def test_empty_path_raises(self):
        with self.assertRaises(ValueError):
            PathValidator.validate_relative_path("")

    def test_whitespace_only_raises(self):
        with self.assertRaises(ValueError):
            PathValidator.validate_relative_path("   ")

    def test_absolute_unix_path_raises(self):
        with self.assertRaises(ValueError):
            PathValidator.validate_relative_path("/etc/passwd")

    def test_absolute_windows_path_raises(self):
        with self.assertRaises(ValueError):
            PathValidator.validate_relative_path("C:\\Users\\test")

    def test_path_traversal_raises(self):
        with self.assertRaises(ValueError):
            PathValidator.validate_relative_path("folder/../../etc/passwd")

    def test_traversal_with_backslash_raises(self):
        with self.assertRaises(ValueError):
            PathValidator.validate_relative_path("folder\\..\\..\\etc")

    def test_illegal_angle_bracket(self):
        with self.assertRaises(ValueError):
            PathValidator.validate_relative_path("folder<test")

    def test_illegal_question_mark(self):
        with self.assertRaises(ValueError):
            PathValidator.validate_relative_path("folder?test")

    def test_illegal_pipe(self):
        with self.assertRaises(ValueError):
            PathValidator.validate_relative_path("folder|test")

    def test_tilde_path_raises(self):
        with self.assertRaises(ValueError):
            PathValidator.validate_relative_path("~/something")

    def test_dot_component_raises(self):
        with self.assertRaises(ValueError):
            PathValidator.validate_relative_path("./something")

    def test_strips_trailing_slash(self):
        result = PathValidator.validate_relative_path("Quantum Computing/Unit 3/")
        self.assertNotEqual(result[-1], "/")

    def test_construct_full_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            usb_root = os.path.join(tmpdir, "USB")
            os.makedirs(usb_root)
            rel = "Quantum Computing/Unit 3"
            full = PathValidator.construct_full_path(usb_root, rel)
            expected = os.path.normpath(os.path.join(usb_root, rel))
            self.assertEqual(full, expected)

    def test_construct_full_path_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            usb_root = os.path.join(tmpdir, "USB")
            os.makedirs(usb_root)
            with self.assertRaises(ValueError):
                PathValidator.construct_full_path(usb_root, "../../etc/passwd")


if __name__ == "__main__":
    unittest.main()
