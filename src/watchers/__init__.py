import platform
from .base import BaseUSBWatcher


def get_watcher(detect_fixed=False) -> BaseUSBWatcher:
    system = platform.system()
    if system == "Windows":
        from .windows import WindowsUSBWatcher
        w = WindowsUSBWatcher()
    elif system == "Darwin":
        from .macos import MacOSUSBWatcher
        w = MacOSUSBWatcher()
    elif system == "Linux":
        from .linux import LinuxUSBWatcher
        w = LinuxUSBWatcher()
    else:
        raise RuntimeError(f"Unsupported platform: {system}")
    w.detect_fixed = detect_fixed
    return w
