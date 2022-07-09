import hashlib


def SHA256sum(file_path : str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()