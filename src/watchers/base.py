import time
from abc import ABC, abstractmethod


class BaseUSBWatcher(ABC):
    def __init__(self):
        self.detect_fixed = False

    @abstractmethod
    def get_removable_volumes(self):
        """Return list of currently mounted removable volume root paths."""
        pass

    def wait_for_new_volume(self, poll_interval=2.0):
        seen = set(self.get_removable_volumes())
        while True:
            time.sleep(poll_interval)
            current = set(self.get_removable_volumes())
            new_volumes = current - seen
            if new_volumes:
                return list(new_volumes)
            seen = current
