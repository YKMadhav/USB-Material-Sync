import json
import os
import subprocess

from .base import BaseUSBWatcher

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import pyudev

    HAS_PYUDEV = True
except ImportError:
    HAS_PYUDEV = False


class LinuxUSBWatcher(BaseUSBWatcher):
    def get_removable_volumes(self):
        volumes = self._lsblk_detection()
        if volumes is not None:
            return volumes
        if HAS_PSUTIL:
            return self._psutil_detection()
        return []

    def _lsblk_detection(self):
        try:
            result = subprocess.run(
                ["lsblk", "-J", "-o", "NAME,TYPE,RM,MOUNTPOINT"],
                capture_output=True,
                timeout=10,
            )
            if result.returncode != 0:
                return None

            data = json.loads(result.stdout)
            volumes = []
            for device in data.get("blockdevices", []):
                is_removable = device.get("rm") is True or str(device.get("rm")).lower() == "1"
                is_disk = device.get("type") == "disk"
                if is_removable or (self.detect_fixed and is_disk):
                    mount = device.get("mountpoint")
                    if mount and os.path.exists(mount):
                        volumes.append(mount + "/" if not mount.endswith("/") else mount)
                    for child in device.get("children", []):
                        mount = child.get("mountpoint")
                        if mount and os.path.exists(mount):
                            volumes.append(mount + "/" if not mount.endswith("/") else mount)

            return volumes
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError, Exception):
            return None

    def _psutil_detection(self):
        volumes = []
        for part in psutil.disk_partitions():
            mount = part.mountpoint
            is_removable_path = mount.startswith("/media/") or mount.startswith("/mnt/")
            if is_removable_path or self.detect_fixed:
                if os.path.exists(mount):
                    volumes.append(mount + "/" if not mount.endswith("/") else mount)
        return volumes

    def wait_for_new_volume(self, poll_interval=2.0):
        if HAS_PYUDEV:
            return self._udev_wait()
        return super().wait_for_new_volume(poll_interval)

    def _udev_wait(self):
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem="block", device_type="partition")

        seen = set(self.get_removable_volumes())
        for event in iter(monitor.poll, None):
            if event.action == "add":
                node = event.device_node
                current = set(self.get_removable_volumes())
                new_volumes = current - seen
                seen = current
                if new_volumes:
                    return list(new_volumes)
