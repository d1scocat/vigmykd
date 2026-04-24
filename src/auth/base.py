from abc import ABC, abstractmethod
from uuid import UUID


class Authenticator(ABC):
    @abstractmethod
    def login(self, creds) -> UUID:
        pass

    @abstractmethod
    def register(self, creds) -> UUID:
        pass

    @abstractmethod
    def get_current_user(self, creds) -> UUID | None:
        pass
