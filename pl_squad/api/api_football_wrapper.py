from __future__ import annotations

import os
import time
from typing import Any, Dict

import requests
from loguru import logger
from pyrate_limiter import BucketFullException, Duration, Limiter, Rate
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from pl_squad.config import API_KEY
from pl_squad.utils import Json

RAPIDAPI_HOST = "api-football-v1.p.rapidapi.com"
BASE_URL = f"https://{RAPIDAPI_HOST}/v3"

TIMEOUT_S: int = 15

# Base plan of api-football allows for max 30 req/min, but we can override the rate-limit values in the environment
MAX_CALLS = int(os.getenv("API_RATE_MAX", "20"))
WINDOW_SECS = int(os.getenv("API_RATE_WINDOW", "60"))

rate = Rate(MAX_CALLS, Duration.SECOND * WINDOW_SECS)
limiter = Limiter(rate)

session = requests.Session()
session.headers.update(
    {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
        "Accept": "application/json",
    }
)


@retry(
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    wait=wait_random_exponential(multiplier=1, max=3),
    stop=stop_after_attempt(3),
    reraise=True,
)
def http_get(url: str, params: Dict[str, Any] | None = None) -> requests.Response:
    """Low-level GET with automatic retries for networking errors & timeouts."""
    resp = session.get(url, params=params or {}, timeout=TIMEOUT_S)
    resp.raise_for_status()
    return resp


def request_json(endpoint: str, params: Dict[str, Any] | None = None) -> Json:
    """GET ``/endpoint`` → parsed JSON, while honouring the rate-limit."""
    limiter_key = f"pl-{id(session)}"

    while True:
        try:
            limiter.try_acquire(limiter_key)

            url = f"{BASE_URL}/{endpoint.lstrip('/')}"
            response = http_get(url, params)
            payload = response.json()

            if "response" not in payload:
                raise ValueError(f"Malformed API reply: {payload!r}")

            return payload["response"]

        except BucketFullException as exc:
            sleep_for = exc.meta_info["remaining_time"]
            logger.warning("Rate limit reached – sleeping {:.2f}s", sleep_for)
            time.sleep(sleep_for)
