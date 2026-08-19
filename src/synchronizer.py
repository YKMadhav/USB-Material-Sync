import os
import shutil

from .verifier import FileVerifier


class MaterialSynchronizer:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def discover_files(self, source_dir):
        if os.path.isfile(source_dir):
            return [source_dir]

        files = []
        if self.config.get("recursive", True):
            for root, _dirs, filenames in os.walk(source_dir):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        else:
            for item in os.listdir(source_dir):
                full = os.path.join(source_dir, item)
                if os.path.isfile(full):
                    files.append(full)

        return sorted(files)

    def discover_all_files(self, source_dir):
        if os.path.isfile(source_dir):
            return [source_dir]

        files = []
        for root, _dirs, filenames in os.walk(source_dir):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return sorted(files)

    def sync(self, source_dir, destination_base):
        stats = {"discovered": 0, "new": 0, "updated": 0, "unchanged": 0, "failed": 0}

        source_name = os.path.basename(source_dir)
        dest_dir = destination_base if os.path.isfile(source_dir) else os.path.join(destination_base, source_name)
        os.makedirs(dest_dir, exist_ok=True)

        if self.config.get("copy_entire_directory", False):
            files = self.discover_all_files(source_dir)
        else:
            files = self.discover_files(source_dir)

        stats["discovered"] = len(files)
        self.logger.info(f"Files discovered: {stats['discovered']}")

        if stats["discovered"] == 0:
            self.logger.warn("No files found in source path.")
            return stats, dest_dir

        verify = self.config.get("verify_hash", True)

        for src_file in files:
            rel_path = os.path.basename(src_file) if os.path.isfile(source_dir) else os.path.relpath(src_file, source_dir)
            dst_file = os.path.join(dest_dir, rel_path)

            try:
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            except OSError as e:
                self.logger.error(f"Cannot create directory for {rel_path}: {e}")
                stats["failed"] += 1
                continue

            try:
                result = self._sync_file(src_file, dst_file, verify)
                stats[result] += 1
            except (OSError, shutil.Error) as e:
                self.logger.error(f"Failed to copy {rel_path}: {e}")
                stats["failed"] += 1

        return stats, dest_dir

    def _sync_file(self, src, dst, verify):
        if not os.path.exists(dst):
            self._do_copy(src, dst)
            return "new"

        try:
            src_size = os.path.getsize(src)
            dst_size = os.path.getsize(dst)
        except OSError:
            self._do_copy(src, dst)
            return "updated"

        if src_size == dst_size:
            if verify:
                src_hash = FileVerifier.compute_sha256(src)
                dst_hash = FileVerifier.compute_sha256(dst)
                if src_hash == dst_hash:
                    return "unchanged"
            else:
                return "unchanged"

        self._do_copy(src, dst)
        return "updated"

    def _do_copy(self, src, dst):
        shutil.copy2(src, dst)

    def verify_copied_files(self, source_dir, dest_dir, files=None):
        if files is None:
            if self.config.get("copy_entire_directory", False):
                files = self.discover_all_files(source_dir)
            else:
                files = self.discover_files(source_dir)

        failed = []
        for src_file in files:
            rel_path = os.path.basename(src_file) if os.path.isfile(source_dir) else os.path.relpath(src_file, source_dir)
            dst_file = os.path.join(dest_dir, rel_path)
            passed, msg = FileVerifier.verify_full(src_file, dst_file)
            if not passed:
                failed.append((rel_path, msg))

        return failed
