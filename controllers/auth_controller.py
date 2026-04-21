"""Authentication (using database and SHA-256 hashing)."""

import hashlib
from database.db import DatabaseManager


class AuthController:
    def __init__(self, db: DatabaseManager):
        self._db = db

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def validate(self, username: str, password: str) -> bool:
        user = self._db.get_usuario_by_username(username)
        if user:
            return user["password_hash"] == self.hash_password(password)
        return False
