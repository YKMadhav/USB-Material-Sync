import json
import os

DEFAULT_CONFIG = {
    "destination": "~/Quantum_Materials",
    "recursive": True,
    "verify_hash": True,
    "exit_after_success": True,
    "poll_interval": 2.0,
    "copy_entire_directory": False,
    "detect_fixed_drives": False,
}


class Config:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.data = dict(DEFAULT_CONFIG)
        self._load()

    def _load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                user_config = json.load(f)
            for key, value in user_config.items():
                self.data[key] = value
        self.data["destination"] = os.path.expanduser(self.data["destination"])

    def save(self):
        export = dict(self.data)
        home = os.path.expanduser("~")
        if export["destination"].startswith(home):
            export["destination"] = "~" + export["destination"][len(home):]
        with open(self.config_path, "w") as f:
            json.dump(export, f, indent=4)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)
