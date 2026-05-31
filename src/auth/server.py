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
        self._auth_path = Path("D:/test.dat")#auth_path.resolve()
        self._token = None

        self._cached_payload = None

        if self._auth_path.exists():
            print(1)
            data = self._auth_path.read_text().strip()
            print("data", len(data), "end data")
            if data:
                self._token = data

    def _set_key(self, key: str):
        self.key = jwt.jwk_from_pem(key.encode())

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
        self._auth_path.write_text(str(token))
        self._token = token
        self._cached_payload = None

    def clear_token(self):
        self._auth_path.write_text("")
        self._token = None
        self._cached_payload = None

    def get_token(self) -> str | None:
        return self._token

    def get_current_user(self) -> Dict[str, Any] | None:
        if not hasattr(self, "key"):
            return None  # wait for it to appear
        if not self._token:
            return None

        if self._cached_payload is not None:
            return self._cached_payload

        try:
            self._cached_payload = jwt.JWT().decode(
                self._token,
                self.key,
                algorithms={"RS256"}, 
                do_verify=True
            )
            return self._cached_payload
        except Exception as ex:
            self.clear_token()
            return None

    def get_user_id(self) -> UUID | None:
        payload = self.get_current_user()
        if not payload:
            return None
        return UUID(payload["uid"])
