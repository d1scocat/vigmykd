import jwt

from pathlib import Path
from typing import Any, Dict
from uuid import UUID

from auth.base import Authenticator
from network import ApiClient


class ServerAuthenticator(Authenticator):
    def __init__(self, client: ApiClient, auth_path: Path):
        super().__init__()

        self._client = client
        self._auth_path = auth_path
        self._token = None

        if self._auth_path.exists():
            data = self._auth_path.read_text().strip()
            if data:
                self._token = data

    def login(self, creds: Dict[str, str]) -> UUID:
        login = creds.get("login", None)
        password = creds.get("password", None)

        if not login or not password:
            missing = [k for k in [login, password] if not k]
            raise AttributeError(f"Missing fields {missing}")

        return self._client.post("/auth/login", params={
            "login": login, "password": password
        })

    def logout(self):
        pass

    def set_token(self, token: str):
        print("Setting token:", token)
        print("auth path:", self._auth_path.absolute())
        self._auth_path.write_text(token)
        self._token = token

    def clear_token(self):
        self._auth_path.write_text("")
        self._token = None

    def get_token(self) -> str | None:
        return self._token

    def get_current_user(self) -> Dict[str, Any] | None:
        if not self._token:
            return None

        try:
            return jwt.JWT().decode(self._token, algorithms={"HS256"}, do_verify=True)
        except Exception:
            self.clear_token()
            return None

    def get_user_id(self) -> UUID | None:
        payload = self.get_current_user()
        if not payload:
            return None
        return UUID(payload["uid"])
