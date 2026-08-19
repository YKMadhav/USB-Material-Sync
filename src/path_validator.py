import os
import re


ILLEGAL_WIN_CHARS = re.compile(r'[<>\?"\*\|]')
WIN_ABSOLUTE = re.compile(r'^[A-Za-z]:[\\/]')


class PathValidator:
    @staticmethod
    def validate_relative_path(path):
        if not path or not path.strip():
            raise ValueError("Path cannot be empty.")

        raw = path.strip()
        if os.path.isabs(raw) or WIN_ABSOLUTE.match(raw) or raw.startswith("~"):
            raise ValueError(
                "Path must be relative. Do not include a drive letter or leading slash."
            )

        path = raw.strip("/").strip("\\")

        if not path:
            raise ValueError("Path cannot be empty.")

        if ".." in path.split("/") or ".." in path.split("\\"):
            raise ValueError("Path must not contain '..' (path traversal).")

        if ILLEGAL_WIN_CHARS.search(path):
            raise ValueError(
                "Path contains illegal characters: < > ? \" * |"
            )

        for part in path.replace("\\", "/").split("/"):
            if part in ("", ".", "..", "~"):
                raise ValueError(f"Path contains invalid component: '{part}'")

        normalized = os.path.normpath(path)
        if normalized.startswith("..") or os.path.isabs(normalized):
            raise ValueError("Normalized path escapes current directory.")

        return normalized

    @staticmethod
    def construct_full_path(usb_root, relative_path):
        full = os.path.normpath(os.path.join(usb_root, relative_path))
        root_normalized = os.path.normpath(usb_root)

        if not full.startswith(root_normalized):
            raise ValueError(
                "Resolved path escapes the USB root. Path traversal detected."
            )

        return full
