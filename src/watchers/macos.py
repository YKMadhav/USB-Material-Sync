import os
import plistlib
import subprocess

from .base import BaseUSBWatcher

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class MacOSUSBWatcher(BaseUSBWatcher):
    def get_removable_volumes(self):
        volumes = self._diskutil_detection()
        if volumes is not None:
            return volumes
        return self._psutil_detection()

    def _diskutil_detection(self):
        try:
            result = subprocess.run(
                ["diskutil", "list", "-plist"],
                capture_output=True,
                timeout=10,
            )
            if result.returncode != 0:
                return None

            plist = plistlib.loads(result.stdout)
            removable = []

            for disk in plist.get("AllDisksAndPartitions", []):
                for partition in disk.get("Partitions", []):
                    mount = partition.get("MountPoint", "")
                    if mount.startswith("/Volumes/"):
                        removable.append(mount + "/")

            return removable
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return None

    def _psutil_detection(self):
        volumes = []
        if not HAS_PSUTIL:
            return volumes

        system_volume = "/"
        for part in psutil.disk_partitions():
            mount = part.mountpoint
            if mount == system_volume:
                continue
            if mount.startswith("/Volumes/"):
                volumes.append(mount + "/" if not mount.endswith("/") else mount)
            elif self.detect_fixed and mount.startswith("/dev/"):
                volumes.append(mount + "/" if not mount.endswith("/") else mount)
        return volumes
