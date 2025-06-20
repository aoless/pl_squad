from typing import Any, Dict, List

from loguru import logger

from pl_squad.api.api_football_wrapper import request_json
from pl_squad.config import (
    LEAGUE_CACHE,
    PLAYER_CACHE,
    SINGLE_PLAYER_CACHE,
    SQUAD_CACHE,
)
from pl_squad.utils import Json, load_json_cache


def get_full_team_details(
    team_id: int, season: int | None = None, dev_mode: bool = True
) -> List[List[Json]]:
    """
    Retrieve detailed information for all players from a given team's squad.
    """
    squad = _get_team_squad(team_id, season, dev_mode)
    players = squad[0].get("players", []) if squad else []
    return [get_player_details(p["id"], dev_mode) for p in players]


def _get_team_squad(
    team_id: int, season: int | None = None, dev_mode: bool = True
) -> List[Json]:
    """
    Retrieve the squad of a given team (optionally for a specific season).
    Uses local cache in dev mode, or queries the API in production.
    """
    if dev_mode:
        squads = load_json_cache(SQUAD_CACHE)
        key = f"{team_id}"
        if key not in squads:
            raise KeyError(f"No squad data for team {key} in cache.")
        return squads[key]

    return request_json("players/squads", {"team": team_id})


def get_player_details(player_id: int, dev_mode: bool = True) -> List[Json]:
    """
    Retrieve detailed information for a specific player.
    Uses local cache in dev mode, or queries the API in production.
    """
    if dev_mode:
        players = load_json_cache(PLAYER_CACHE)
        key = str(player_id)
        if key not in players:
            raise KeyError(f"No player data for ID {key} in cache.")
        return players[key]

    return request_json("players/profiles", {"player": player_id})


def list_clubs(season: int | None = None, dev_mode: bool = True) -> List[Json]:
    """
    List all clubs in the Premier League for a given season.
    Uses local cache in dev mode, or queries the API in production.
    """
    if dev_mode:
        league_data = load_json_cache(LEAGUE_CACHE)
        return league_data

    params: Dict[str, Any] = {"league": "39"}
    if season is not None:
        params["season"] = season

    return request_json("teams", params)


def search_player(player_name: str, dev_mode: bool = True) -> List[Json]:
    """
    Search for a player by name and return a list of player profiles.
    Uses local cache in dev mode, or queries the API in production.
    """
    if dev_mode:
        player_data = load_json_cache(SINGLE_PLAYER_CACHE)
        return player_data

    return request_json("players/profiles", {"search": player_name})


if __name__ == "__main__":
    TEAM_ID = 42  # Arsenal
    PLAYER_ID = 19465  # David Raya

    dev_mode = False

    logger.info("Fetching squad for team {}", TEAM_ID)
    squad = _get_team_squad(TEAM_ID, dev_mode=dev_mode)
    logger.info("Squad size: {}", len(squad[0]["players"]))

    # logger.info("Fetching details for player {}", PLAYER_ID)
    # player_details = get_player_details(PLAYER_ID, dev_mode=dev_mode)
    # logger.info(player_details)

    # logger.info("Fetching full team details...")
    # profiles = get_full_team_details(TEAM_ID, dev_mode=True)
    # logger.info("Fetched {} player profiles", len(profiles))

    # logger.info("Listing all clubs from Premier League...")
    # team_data = list_clubs(2024, dev_mode=dev_mode)
    # logger.info("Premier League clubs: {}", team_data)

    # logger.info("Searching for player by name...")
    # player_data = search_player("Robert Lewandowski", dev_mode=dev_mode)
    # logger.info("Player data: {}", player_data)
