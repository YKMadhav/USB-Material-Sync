#!/usr/bin/env python3
"""USB Material Synchronizer - Main entry point."""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.logger import SyncLogger
from src.path_validator import PathValidator
from src.synchronizer import MaterialSynchronizer
from src.watchers import get_watcher

BANNER = r"""
USB Material Synchronizer
"""
DIVIDER = "\u2500" * 30


def print_banner(logger):
    logger.info(BANNER)
    logger.info(DIVIDER)


def get_source_path(logger):
    logger.info("Enter the relative path of the material on the USB:")
    logger.info("(e.g. Quantum Computing/Unit 3)")
    logger.info("")
    while True:
        try:
            raw = input("> ").strip()
            validated = PathValidator.validate_relative_path(raw)
            logger.info(f"Material path: {validated}")
            return validated
        except ValueError as e:
            logger.error(f"Invalid path: {e}")
            logger.info("Try again.")


def get_destination(config, logger):
    default_dest = config["destination"]
    logger.info(f"Destination [{default_dest}]:")
    raw = input("> ").strip()
    if not raw:
        dest = default_dest
    else:
        dest = os.path.expanduser(raw)
    os.makedirs(dest, exist_ok=True)
    logger.info(f"Destination: {dest}")
    return dest


def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    config = Config("config.json")
    logger = SyncLogger("logs")

    print_banner(logger)
    logger.info("Configuration loaded.")
    logger.info(DIVIDER)

    relative_path = get_source_path(logger)
    logger.info("")

    destination = get_destination(config, logger)
    logger.info("")

    logger.info("Configuration accepted.")
    logger.info(DIVIDER)
    logger.info("Status: ARMED")
    drive_type = "removable drive" if not config.get("detect_fixed_drives", False) else "removable or external drive"
    logger.info(f"Waiting for a {drive_type}...")
    logger.info("(Press Ctrl+C to exit)")
    logger.info(DIVIDER)

    watcher = get_watcher(detect_fixed=config.get("detect_fixed_drives", False))
    synchronizer = MaterialSynchronizer(config, logger)
    poll_interval = config.get("poll_interval", 2.0)

    try:
        while True:
            new_volumes = watcher.wait_for_new_volume(poll_interval=poll_interval)

            for volume in new_volumes:
                logger.info(DIVIDER)
                logger.info(f"Removable drive detected: {volume}")
                logger.info(f"Checking: {os.path.join(volume, relative_path)}")

                source = PathValidator.construct_full_path(volume, relative_path)

                if not os.path.exists(source):
                    logger.info("Expected material path not found. Ignoring this drive.")
                    logger.info(DIVIDER)
                    continue

                logger.info("Path found.")
                logger.info("")
                logger.info("Synchronizing material...")
                logger.info("")

                try:
                    stats, dest_dir = synchronizer.sync(source, destination)
                except (OSError, Exception) as e:
                    logger.error(f"Synchronization failed: {e}")
                    logger.info(DIVIDER)
                    continue

                logger.info(DIVIDER)
                logger.info("Synchronization complete.")
                logger.info("")
                logger.info(f"Files discovered: {stats['discovered']}")
                logger.info(f"New files: {stats['new']}")
                logger.info(f"Updated files: {stats['updated']}")
                logger.info(f"Skipped unchanged: {stats['unchanged']}")
                if stats["failed"] > 0:
                    logger.error(f"Failed: {stats['failed']}")
                logger.info("")
                logger.info(f"Destination: {dest_dir}")

                if config.get("verify_hash", True):
                    logger.info("")
                    logger.info("Running integrity verification...")
                    failed = synchronizer.verify_copied_files(source, dest_dir)
                    if failed:
                        logger.error(f"Integrity verification: FAILED ({len(failed)} files)")
                        for name, msg in failed:
                            logger.error(f"  {name}: {msg}")
                    else:
                        logger.info("Integrity verification: PASSED")

                logger.info(DIVIDER)

                if config.get("exit_after_success", False):
                    logger.info("Exiting after successful sync.")
                    return

                logger.info("Waiting for next USB drive...")
                logger.info(DIVIDER)

    except KeyboardInterrupt:
        logger.info("")
        logger.info("Interrupted by user. Exiting.")
        return


if __name__ == "__main__":
    main()
