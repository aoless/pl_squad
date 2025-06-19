from __future__ import annotations

import os
import time
from typing import Any, Dict

import requests
from loguru import logger
from pyrate_limiter import Duration, Limiter, Rate
from tenacity import (
    retry,
    retry_any,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from pl_squad.config import RAPIDAPI_API_KEY
from pl_squad.utils import Json

__all__ = [
    "request_json",
]

RAPIDAPI_HOST = "api-football-v1.p.rapidapi.com"
BASE_URL = f"https://{RAPIDAPI_HOST}/v3"

TIMEOUT_S: int = 15

# Base plan: 30 req/min.
MAX_CALLS = int(os.getenv("API_RATE_MAX", "20"))
WINDOW_SECS = int(os.getenv("API_RATE_WINDOW", "60"))

rate = Rate(MAX_CALLS, WINDOW_SECS * Duration.SECOND)
limiter = Limiter(rate, raise_when_fail=False)

GLOBAL_KEY = RAPIDAPI_API_KEY

session = requests.Session()
session.headers.update(
    {
        "x-rapidapi-key": RAPIDAPI_API_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
        "Accept": "application/json",
    }
)


def _respect_retry_after(resp: requests.Response) -> bool:
    """Sleep for the duration suggested by the upstream `Retry-After` header.

    Returns ``True`` if the function slept, so the caller may decide to retry.
    """
    if resp.status_code != 429:
        return False

    retry_after = float(resp.headers.get("Retry-After", "1"))
    logger.warning("Upstream 429 – sleeping %.2fs", retry_after)
    time.sleep(retry_after + 0.05)  # add a small safety margin
    return True


@retry(
    retry=retry_any(
        retry_if_exception_type(requests.exceptions.RequestException),
        retry_if_exception_type(requests.HTTPError),  # we re‑raise 429s below
    ),
    wait=wait_random_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(5),
    reraise=True,
)
def _http_get(url: str, params: Dict[str, Any] | None = None) -> requests.Response:  # noqa: D401, E501
    """Low‑level GET with automatic retries for *network* errors **and** 429s."""
    resp = session.get(url, params=params or {}, timeout=TIMEOUT_S)

    if resp.status_code == 429 and _respect_retry_after(resp):
        resp.raise_for_status()

    resp.raise_for_status()
    return resp


def request_json(endpoint: str, params: Dict[str, Any] | None = None) -> Json:
    """GET ``/endpoint`` → parsed JSON (``payload["response"]``) while honouring
    both a *local* rate limit and any server‑side 429 responses.
    """
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    params = params or {}

    while True:
        _, remaining_time = limiter.try_acquire(GLOBAL_KEY)
        if remaining_time is not None:
            logger.warning("Rate limit reached – sleeping %.2fs", remaining_time)
            time.sleep(remaining_time + 0.05)  # safety margin
            continue

        try:
            response = _http_get(url, params)
            payload = response.json()

            if "response" not in payload:
                raise ValueError(f"Malformed API reply: {payload!r}")

            return payload["response"]

        except requests.HTTPError as exc:
            if exc.response.status_code == 429:
                continue
            raise
