import base64
import hashlib

from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.crypto import constant_time_compare, get_random_string

class SHA512PasswordHasher(BasePasswordHasher):
    """Hashowanie haseł metodą SHA-512 (solone).

    Format zapisu w bazie: ``sha512$<salt>$<digest>``
    Hasher jest zarejestrowany w settings.PASSWORD_HASHERS, dzięki czemu
    Django (set_password / check_password / authenticate) używa go
    automatycznie i w całym projekcie nie ma żadnych surowych zapytań SQL.
    """

    algorithm = "sha512"

    def salt(self):
        return get_random_string(16)

    def encode(self, password, salt):
        assert password is not None
        assert salt and "$" not in salt
        digest = hashlib.sha512((salt + password).encode("utf-8")).digest()
        digest_b64 = base64.b64encode(digest).decode("ascii").rstrip("=")
        return f"{self.algorithm}${salt}${digest_b64}"

    def _digest_b64(self, password, salt):
        digest = hashlib.sha512((salt + password).encode("utf-8")).digest()
        return base64.b64encode(digest).decode("ascii").rstrip("=")

    def verify(self, password, encoded):
        algorithm, salt, digest = encoded.split("$", 2)
        assert algorithm == self.algorithm
        return constant_time_compare(self._digest_b64(password, salt), digest)

    def safe_summary(self, encoded):
        algorithm, salt, digest = encoded.split("$", 2)
        return {
            "algorithm": algorithm,
            "salt": mask_hash(salt, show=2),
            "hash": mask_hash(digest, show=6),
        }

    def harden_runtime(self, password, encoded):
        pass

    def must_update(self, encoded):
        return False
