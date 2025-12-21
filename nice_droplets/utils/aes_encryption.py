import os
from typing import Optional
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import constant_time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

class AESEncryption:
    def __init__(self, password: str, salt_file: str = "salt.bin", salt_size: int = 16, iterations: int = 100_000, mode="load"):
        """
        Initialize the AES encryption helper.
        
        :param password: Password for encryption
        :param salt_file: Path to the salt file
        :param salt_size: Size of the salt in bytes
        :param iterations: Number of iterations for PBKDF2
        :param mode: "load" to load existing salt, "save" to create new salt
        """
        self.password = password.encode()
        self.salt_file = salt_file
        self.salt_size = salt_size
        self.iterations = iterations
        if mode == "load":
            self.salt = self.load_salt()
        elif mode == "save":
            self.salt = self.create_salt()
        else:
            raise ValueError("Invalid mode")
        self.key = self.derive_key()

    def load_salt(self) -> bytes:
        if os.path.exists(self.salt_file):
            with open(self.salt_file, "rb") as f:
                return f.read()
        return None

    def create_salt(self) -> bytes:
        salt = os.urandom(self.salt_size)
        with open(self.salt_file, "wb") as f:
            f.write(salt)
        return salt

    def derive_key(self) -> bytes:
        if not self.salt:
            raise ValueError("Salt not found")
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=self.iterations,
            backend=default_backend()
        )
        return kdf.derive(self.password)

    def encrypt(self, data: bytes) -> bytes:
        # AES-GCM for authenticated encryption
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, data, None)
        return nonce + ct  # prepend nonce for decryption

    def decrypt(self, token: bytes) -> bytes:
        aesgcm = AESGCM(self.key)
        nonce = token[:12]
        ct = token[12:]
        try:
            return_val = aesgcm.decrypt(nonce, ct, None)
            return return_val
        except InvalidTag:  # wrong pass key
            return None

# Example usage:
# helper = EncryptionHelper(password="mysecret", salt_file="salt.bin")
# encrypted = helper.encrypt(b"secret data")
# decrypted = helper.decrypt(encrypted)
