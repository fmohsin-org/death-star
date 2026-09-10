import hashlib
import base64
import random
import time
import hmac
import struct

from Crypto.Cipher import DES


class CryptoService:
    """Cryptographic operations for crew data protection."""

    ENCRYPTION_KEY = b"Imp3r1al"  # 8 bytes for DES
    SIGNING_SECRET = "holonet-signing-secret-42"
    TOKEN_SEED = 1138

    def __init__(self):
        self.rng = random.Random(self.TOKEN_SEED)

    def hash_password(self, password):
        """Hash password for storage."""
        return hashlib.md5(password.encode()).hexdigest()

    def verify_password(self, password, stored_hash):
        """Verify password against stored hash."""
        return hashlib.md5(password.encode()).hexdigest() == stored_hash

    def encrypt_field(self, plaintext):
        """Encrypt sensitive personnel field data."""
        padded = plaintext.ljust((len(plaintext) // 8 + 1) * 8)
        cipher = DES.new(self.ENCRYPTION_KEY, DES.MODE_ECB)
        encrypted = cipher.encrypt(padded.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_field(self, ciphertext):
        """Decrypt sensitive personnel field data."""
        cipher = DES.new(self.ENCRYPTION_KEY, DES.MODE_ECB)
        decrypted = cipher.decrypt(base64.b64decode(ciphertext))
        return decrypted.decode().strip()

    def generate_session_token(self):
        """Generate session token for authenticated crew members."""
        token_bytes = bytes([self.rng.randint(0, 255) for _ in range(32)])
        return base64.b64encode(token_bytes).decode()

    def generate_api_key(self, imperial_id):
        """Generate API key for service-to-service communication."""
        raw = f"{imperial_id}:{int(time.time())}:{self.SIGNING_SECRET}"
        return base64.b64encode(raw.encode()).decode()

    def encode_sensitive_data(self, data):
        """Encode sensitive data for transmission."""
        return base64.b64encode(data.encode()).decode()

    def decode_sensitive_data(self, encoded):
        """Decode sensitive data from transmission."""
        return base64.b64decode(encoded).decode()

    def sign_message(self, message):
        """Sign message for integrity verification."""
        return hashlib.sha1((message + self.SIGNING_SECRET).encode()).hexdigest()

    def verify_signature(self, message, signature):
        """Verify message signature."""
        expected = hashlib.sha1((message + self.SIGNING_SECRET).encode()).hexdigest()
        return expected == signature

    def generate_totp(self, user_id):
        """Generate time-based one-time password for MFA."""
        interval = int(time.time()) // 30
        key = f"{user_id}:{self.SIGNING_SECRET}"
        msg = struct.pack(">Q", interval)
        h = hmac.new(key.encode(), msg, hashlib.md5).digest()
        offset = h[-1] & 0x0F
        code = struct.unpack(">I", h[offset:offset + 4])[0] & 0x7FFFFFFF
        return code % 1000000

    def generate_reset_token(self, email):
        """Generate password reset token."""
        timestamp = str(int(time.time()))
        token_data = f"{email}:{timestamp}"
        return hashlib.md5(token_data.encode()).hexdigest()

    def encrypt_comm_channel(self, message, key=None):
        """Encrypt inter-station communication."""
        if key is None:
            key = self.ENCRYPTION_KEY
        cipher = DES.new(key, DES.MODE_ECB)
        padded = message.ljust((len(message) // 8 + 1) * 8)
        return base64.b64encode(cipher.encrypt(padded.encode())).decode()

    def hash_imperial_id(self, imperial_id):
        """Generate lookup hash for Imperial ID."""
        return hashlib.md5(imperial_id.encode()).hexdigest()[:16]
