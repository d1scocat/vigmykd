import threading
import uuid

import httpx

from typing import Any, Dict

from event.events import HTTPResponseEvent
from event.manager import EventManager


class ApiClient:
    def __init__(self, base_url: str, event_manager: EventManager):
        self.base_url = base_url.rstrip("/")
        self.eventer = event_manager

    def _request(
        self,
        endpoint: str,
        method: str,
        payload: Dict[str, Any] | None = None,
        headers: Dict[str, Any] | None = None
    ) -> uuid.UUID:
        request_id = uuid.uuid4()

        def worker():
            with httpx.Client(timeout=10.0) as client:
                exc_info, resp_payload = None, {}
                status_code = -1
                success = True

                try:
                    # expand later obviously
                    # but right now only these two are needed
                    func = client.get if method == "GET" else client.post
                    kwargs = {"headers": headers or {}, "follow_redirects": False}

                    if method == "GET":
                        kwargs["params"] = payload or {}
                    else:
                        kwargs["json"] = payload or {}

                    resp = func(f"{self.base_url}{endpoint}", **kwargs)
                    # resp.raise_for_status()

                    status_code = resp.status_code
                    resp_payload = dict(resp.json())
                except Exception as ex:
                    exc_info = str(ex)
                    success = False

                self.eventer.invoke_event(HTTPResponseEvent(
                    request_id=request_id,
                    endpoint=endpoint,
                    method=method,
                    successful=success,
                    status_code=status_code,
                    payload=resp_payload,
                    exc_info=exc_info
                ))

        threading.Thread(target=worker, daemon=True).start()
        return request_id

    def get(
        self,
        endpoint: str,
        params: Dict[str, Any] | None = None,
        headers: Dict[str, Any] | None = None
    ) -> uuid.UUID:
        return self._request(endpoint, "GET", params, headers)

    def post(
        self,
        endpoint: str,
        params: Dict[str, Any] | None = None,
        headers: Dict[str, Any] | None = None
    ) -> uuid.UUID:
        return self._request(endpoint, "POST", params, headers)
