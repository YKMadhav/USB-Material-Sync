# USB Material Synchronizer

> **Plug in. Sync. Study.** A cross-platform desktop utility that
> automatically detects authorized USB drives and copies lecture
> material to a local study directory.

## Overview

**USB Material Synchronizer** is a lightweight Python application
that watches for removable USB storage and synchronizes a
user-specified directory of lecture material to your local machine.

Enter the relative path once, arm the program, and plug in the USB
when class begins. The utility detects the removable volume, validates
the configured path, copies the requested files, preserves
directory structure, avoids duplicates, and verifies file integrity
with SHA-256 hashing.

> The program operates **only** on removable volumes and **only** on
> the user-specified relative path. It never scans the entire USB
> indiscriminately.

## Why I Built This

This project came from a simple situation I have experienced as a student.

Sometimes lecture notes or study materials are not shared immediately. There can be delays in collecting the material, uploading it, or getting it from the teacher to the students. When exams are approaching, even a small delay can become inconvenient.

I wanted a simple way to make the material available without depending on everyone having to manually copy files or wait for them to be shared digitally.

With **USB-Material-Sync**, the required study material can be placed on a removable drive, and the tool can automatically detect the drive and synchronize the material to the intended location.

The idea is simple:

> **Put the material on the removable drive → connect it → let the tool handle the copying.**

This also makes it useful beyond my original use case. Anyone can prepare a removable drive with the required files and use the tool to quickly transfer the material to a computer without manually navigating through folders and copying everything one by one.

It started as a small solution to a problem I personally encountered, but the same idea can be useful anywhere **materials need to be distributed quickly through a removable drive**.

## Features

-   Automatic removable-volume detection (Windows, macOS, Linux)
-   Interactive relative-path input with traversal protection
-   Syncs any file format (`.py`, `.mp4`, `.pdf`, `.mp3`, and more)
-   Recursive directory traversal with structure preservation
-   Intelligent duplicate detection and incremental updates
-   SHA-256 integrity verification after every copy
-   Graceful handling of USB removal mid-sync
-   File and console logging with timestamps
-   Clean modular architecture for future platform extensions

## Project Structure

``` text
usb-material-sync/
├── main.py                  Entry point and state machine
├── config.json              User configuration
├── requirements.txt         Python dependencies
├── src/
│   ├── config.py            Configuration loader
│   ├── logger.py            File and console logging
│   ├── path_validator.py    Safe path input validation
│   ├── synchronizer.py      File sync engine
│   ├── verifier.py          SHA-256 integrity checks
│   └── watchers/
│       ├── __init__.py      Platform auto-detection factory
│       ├── base.py          Abstract watcher interface
│       ├── windows.py       Windows (psutil / ctypes)
│       ├── macos.py         macOS (diskutil / psutil)
│       └── linux.py         Linux (lsblk / pyudev)
└── tests/
    ├── test_path_validator.py
    ├── test_synchronizer.py
    └── test_verifier.py
```

## Installation

``` bash
git clone https://github.com/YKMadhav/usb-material-sync.git
cd usb-material-sync

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Run

``` bash
python main.py
```

Enter the relative path of your material on the USB when prompted
(e.g. `Quantum Computing/Unit 3`), then insert the USB drive when
class begins.

## Configuration

Edit `config.json` to customize behavior:

``` json
{
    "destination": "~/Quantum_Materials",
    "recursive": true,
    "verify_hash": true,
    "exit_after_success": true,
    "poll_interval": 2.0,
    "copy_entire_directory": false
}
```

| Option | Description |
|---|---|
| `destination` | Local directory for copied material (`~` expands to home) |
| `recursive` | Search subdirectories of the source path |
| `verify_hash` | SHA-256 verify after each copy |
| `exit_after_success` | Quit after first successful sync |
| `poll_interval` | Seconds between removable-volume checks |
| `copy_entire_directory` | Legacy option; all file formats are copied |

With `exit_after_success` enabled, the app terminates after the first
successful sync instead of waiting for another USB drive.


## Architecture

``` text
User Input (relative path)
        |
   Path Validation
        |
   ARMED State
        |
  USB Detection Layer ─── watches for removable volumes
        |
  Mount-Volume Abstraction ─── platform-independent root paths
        |
  Path Construction ─── usb_root + relative_path
        |
  Material Discovery ─── accepts all file formats, recurses dirs
        |
  Synchronization Engine ─── dedup, update, copy
        |
  Integrity Verification ─── SHA-256 source vs dest
        |
  Logging ─── file + console
```

### USB Detection (Windows)

On Windows the watcher uses `psutil.disk_partitions()` and filters
entries whose options string contains `removable`. If `psutil` is
unavailable, it falls back to `ctypes.windll.kernel32.GetDriveTypeW`
which returns `DRIVE_REMOVABLE = 2` for USB drives.

### USB Detection (macOS)

On macOS the watcher runs `diskutil list -plist` and looks for
partitions mounted under `/Volumes/`. It falls back to `psutil`
filtering mount points that start with `/Volumes/` excluding the
system volume.

### USB Detection (Linux)

On Linux the watcher runs `lsblk -J` and checks the `rm` (removable)
flag. If available, it uses `pyudev` for event-driven detection.
Falls back to `psutil` filtering mount points under `/media/` or
`/mnt/`.

## Testing

``` bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

Or:

``` bash
python -m unittest discover tests/ -v
```

## Logging

All activity is written locally to `logs/sync.log` with timestamps.
The log directory is created automatically and is excluded from version control:

``` text
[14:02:11] Application started
[14:02:15] Material path: Quantum Computing/Unit 3
[14:02:15] Status: ARMED
[14:47:03] Removable drive detected: E:\
[14:47:03] Path found.
[14:47:04] 12 files discovered
[14:47:06] New files: 10
[14:47:06] Updated files: 2
[14:47:07] Integrity verification: PASSED
```

## Tech Stack

-   **Python** --- core language
-   **psutil** --- cross-platform disk partition detection
-   **ctypes** --- Windows `GetDriveTypeW` fallback
-   **shutil** --- file copying and metadata preservation
-   **hashlib** --- SHA-256 integrity verification
-   **diskutil** (macOS) / **lsblk** (Linux) --- removable volume
    detection
-   **pyudev** (Linux, optional) --- event-driven volume arrival

## Author

**Khatwang Madhav Yippili**

B.S. (Hons.) in Mathematical Sciences and Computing

Sri Sathya Sai Institute of Higher Learning
