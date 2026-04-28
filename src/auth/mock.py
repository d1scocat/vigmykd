import uuid
from pathlib import Path
from typing import Any

from auth.base import Authenticator


class MockAuthenticator(Authenticator):
    def __init__(self, auth_path: Path) -> None:
        super().__init__()
        self.auth_path = auth_path

    def login(self, creds) -> uuid.UUID:
        id = uuid.uuid4()
        self._save(id)
        return id

    def register(self, creds) -> uuid.UUID:
        id = uuid.uuid4()
        self._save(id)
        return id

    def get_current_user(self, creds: Any) -> uuid.UUID | None:
        if not self.auth_path.exists():
            return None

        return uuid.UUID(self.auth_path.read_text())

    def _save(self, id: uuid.UUID):
        self.auth_path.write_text(str(id))
