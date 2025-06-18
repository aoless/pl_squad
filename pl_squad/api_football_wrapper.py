from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Union

import requests
from dotenv import load_dotenv
from loguru import logger
from pyrate_limiter import BucketFullException, Duration, Limiter, Rate
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

Json = Union[Dict[str, Any], List[Any]]

### Configuration

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY")
if not API_KEY:
    raise RuntimeError(
        "Environment variable RAPIDAPI_KEY is missing. "
        "Create a .env file or export the key before importing this module."
    )

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
def _http_get(url: str, params: Dict[str, Any] | None = None) -> requests.Response:
    """Low-level GET with automatic retries for networking errors & timeouts."""
    resp = session.get(url, params=params or {}, timeout=TIMEOUT_S)
    resp.raise_for_status()
    return resp


def _request_json(endpoint: str, params: Dict[str, Any] | None = None) -> Json:
    """GET ``/endpoint`` → parsed JSON, while honouring the rate-limit."""
    limiter_key = f"pl-{id(session)}"

    while True:
        try:
            limiter.try_acquire(limiter_key)

            url = f"{BASE_URL}/{endpoint.lstrip('/')}"
            response = _http_get(url, params)
            payload = response.json()

            if "response" not in payload:
                raise ValueError(f"Malformed API reply: {payload!r}")

            return payload["response"]

        except BucketFullException as exc:
            sleep_for = exc.meta_info["remaining_time"]
            logger.warning("Rate limit reached – sleeping {:.2f}s", sleep_for)
            time.sleep(sleep_for)


def get_team_squad(team_id: int, season: int | None = None) -> List[Json]:
    params: Dict[str, Any] = {"team": team_id}
    if season is not None:
        params["season"] = season
    return _request_json("players/squads", params)


def get_player_details(player_id: int) -> List[Json]:
    return _request_json("players/profiles", {"player": player_id})


def get_team_details(team_id: int, season: int | None = None) -> List[List[Json]]:
    squad = get_team_squad(team_id, season)
    players = squad[0].get("players", []) if squad else []
    return [get_player_details(p["id"]) for p in players]


if __name__ == "__main__":
    TEAM_ID = 33  # PSG
    PLAYER_ID = 50132  # Altay Bayındır

    logger.info("Fetching squad for team {}", TEAM_ID)
    squad = get_team_squad(TEAM_ID)
    logger.info("Squad size: {}", len(squad[0]["players"]))

    logger.info("Fetching details for player {}", PLAYER_ID)
    player_details = get_player_details(PLAYER_ID)
    logger.info(player_details)

    logger.info("Fetching full team details...")
    profiles = [1, 2, 3]  # get_team_details(TEAM_ID)
    logger.info("Fetched {} player profiles", len(profiles))
