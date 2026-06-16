from abc import ABC, abstractmethod
from uuid import UUID
from typing import Any


class Authenticator(ABC):
    @abstractmethod
    def login(self, creds: dict[str, str]) -> UUID:
        """Returns the HTTP request UUID, not the player UUID."""
        pass

    @abstractmethod
    def logout(self):
        pass

    @abstractmethod
    def set_token(self, token: str):
        pass

    @abstractmethod
    def clear_token(self):
        pass

    @abstractmethod
    def get_token(self) -> str | None:
        pass

    @abstractmethod
    def get_current_user(self) -> dict[str, Any] | None:
        pass

    @abstractmethod
    def get_user_id(self) -> UUID | None:
        pass
