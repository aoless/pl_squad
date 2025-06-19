from typing import Any, Dict, List

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

    params: Dict[str, Any] = {"team": team_id}
    if season is None:
        params["season"] = 2024

    return request_json("players/squads", params)


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
