import hashlib
import os


CHUNK_SIZE = 65536


class FileVerifier:
    @staticmethod
    def get_size(path):
        return os.path.getsize(path)

    @staticmethod
    def compute_sha256(path):
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def verify_full(source, destination):
        if not os.path.exists(destination):
            return False, "Destination file does not exist."

        src_size = FileVerifier.get_size(source)
        dst_size = FileVerifier.get_size(destination)
        if src_size != dst_size:
            return False, f"Size mismatch: source={src_size}, dest={dst_size}"

        src_hash = FileVerifier.compute_sha256(source)
        dst_hash = FileVerifier.compute_sha256(destination)
        if src_hash != dst_hash:
            return False, f"Hash mismatch"

        return True, "Verification passed."

    @staticmethod
    def verify_quick(source, destination):
        if not os.path.exists(destination):
            return False, "Destination file does not exist."

        src_size = FileVerifier.get_size(source)
        dst_size = FileVerifier.get_size(destination)
        if src_size != dst_size:
            return False, f"Size mismatch: source={src_size}, dest={dst_size}"

        return True, "Quick verification passed."
