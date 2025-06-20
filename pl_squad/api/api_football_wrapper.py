from __future__ import annotations

import os
import time
from typing import Any, Dict

import requests
from pyrate_limiter import Duration, Limiter, Rate
from tenacity import retry, stop_after_attempt, wait_random_exponential

from pl_squad.config import RAPIDAPI_KEY

HOST = "api-football-v1.p.rapidapi.com"
BASE_URL = f"https://{HOST}/v3"
TIMEOUT_S = 15

session = requests.Session()
session.headers.update(
    {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": HOST,
        "Accept": "application/json",
    }
)

limiter = Limiter(
    Rate(
        int(os.getenv("API_RATE_MAX", 20)),
        int(os.getenv("API_RATE_WINDOW", 60)) * Duration.SECOND,
    ),
    raise_when_fail=False,
)


def _respect_retry_after(resp: requests.Response) -> None:
    """Sleep if the server asked us to (HTTP 429 Retry-After)."""
    if resp.status_code != 429:
        return
    time.sleep(float(resp.headers.get("Retry-After", 1)) + 0.05)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_random_exponential(multiplier=1, max=10),
    reraise=True,
)
def _get(url: str, params: Dict[str, Any] | None = None) -> requests.Response:
    while not limiter.try_acquire(RAPIDAPI_KEY):
        time.sleep(1.0)
    resp = session.get(url, params=params, timeout=TIMEOUT_S)
    _respect_retry_after(resp)
    resp.raise_for_status()  # re-raises 429
    return resp


def request_json(endpoint: str, params: Dict[str, Any] | None = None) -> Any:
    """GET `/endpoint` and return `payload["response"]`."""
    payload = _get(f"{BASE_URL}/{endpoint.lstrip('/')}", params).json()
    return payload.get("response", payload)
