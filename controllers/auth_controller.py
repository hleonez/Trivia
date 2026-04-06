"""Authentication (prototype: fixed credentials)."""


class AuthController:
    _USER = "admin"
    _PASS = "admin"

    def validate(self, username: str, password: str) -> bool:
        return username == self._USER and password == self._PASS
