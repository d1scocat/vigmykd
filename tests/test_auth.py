from auth.server import ServerAuthenticator
from event import EventManager
from network import ApiClient

import logging

from pathlib import Path


logger = logging.getLogger("test")
em = EventManager(logger)
client = ApiClient("https://vigmykd.runderscore.com/api/v1", em)
path = Path("D:/test.dat")
auth = ServerAuthenticator(client, path)

token = "abc"

def test_auth():
    auth.set_token(token)
    assert path.read_text() == token