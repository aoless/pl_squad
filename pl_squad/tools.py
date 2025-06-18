from typing import Any, Dict, List

from pl_squad.api.api_football_wrapper import request_json
from pl_squad.config import PLAYER_CACHE, SQUAD_CACHE
from pl_squad.utils import Json, load_json_cache


def get_team_squad(
    team_id: int, season: int | None = None, dev_mode: bool = True
) -> List[Json]:
    if dev_mode:
        squads = load_json_cache(SQUAD_CACHE)
        key = f"{team_id}" + (f"_{season}" if season is not None else "")
        if key not in squads:
            raise KeyError(f"No squad data for team {key} in cache.")
        return [squads[key][0]]

    params: Dict[str, Any] = {"team": team_id}
    if season is not None:
        params["season"] = season
    return request_json("players/squads", params)


def get_player_details(player_id: int, dev_mode: bool = True) -> List[Json]:
    if dev_mode:
        players = load_json_cache(PLAYER_CACHE)
        key = str(player_id)
        if key not in players:
            raise KeyError(f"No player data for ID {key} in cache.")
        return players[key]

    return request_json("players/profiles", {"player": player_id})


def get_full_team_details(
    team_id: int, season: int | None = None, dev_mode: bool = True
) -> List[List[Json]]:
    squad = get_team_squad(team_id, season, dev_mode)
    players = squad[0].get("players", [])[:10] if squad else []
    return [get_player_details(p["id"], dev_mode) for p in players]


def search_team(team_name: str) -> str:
    """
    Placeholder for searching for a team by name and returning the team ID.
    """
    team_mapping = {
        "Manchester United": 33,
        "Arsenal": 42,
        "Liverpool": 35,
        "Chelsea": 45,
        "Manchester City": 36,
        "Barcelona": 132,
    }
    return team_mapping.get(team_name, "Team not found")
