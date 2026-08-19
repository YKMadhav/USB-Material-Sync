import ctypes
import os

from .base import BaseUSBWatcher

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class WindowsUSBWatcher(BaseUSBWatcher):
    DRIVE_REMOVABLE = 2
    DRIVE_FIXED = 3

    def get_removable_volumes(self):
        if HAS_PSUTIL:
            return self._psutil_detection()
        return self._ctypes_detection()

    def _psutil_detection(self):
        volumes = []
        for part in psutil.disk_partitions():
            is_removable = "removable" in part.opts.lower()
            is_fixed = "fixed" in part.opts.lower() or part.fstype != ""
            if is_removable or (self.detect_fixed and is_fixed):
                mount = part.mountpoint
                if os.path.exists(mount):
                    volumes.append(mount)
        return volumes

    def _ctypes_detection(self):
        volumes = []
        kernel32 = ctypes.windll.kernel32
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            path = f"{letter}:\\"
            try:
                dtype = kernel32.GetDriveTypeW(path)
                is_removable = dtype == self.DRIVE_REMOVABLE
                is_fixed = dtype == self.DRIVE_FIXED
                if (is_removable or (self.detect_fixed and is_fixed)) and os.path.exists(path):
                    volumes.append(path)
            except Exception:
                continue
        return volumes
