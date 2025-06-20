from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from pl_squad.tools import _get_team_squad, get_player_details

CLUBS: Dict[int, str] = {
    42: "Arsenal",
    33: "Manchester United",
}

SQUAD_CACHE_FILE = Path("cache/cache_squads.json")
PLAYER_CACHE_FILE = Path("cache/cache_players.json")


def _load_cache(path: Path) -> Dict:
    return json.loads(path.read_text()) if path.exists() else {}


def _save_cache(obj: Dict, path: Path) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2))


def fetch() -> None:
    squad_cache = _load_cache(SQUAD_CACHE_FILE)
    player_cache = _load_cache(PLAYER_CACHE_FILE)

    for team_id, club_name in CLUBS.items():
        if str(team_id) in squad_cache:
            print(f"✅ {club_name}: squad from cache")
            squad_payload = squad_cache[str(team_id)]
        else:
            print(f"🌐 {club_name}: fetching squad …")
            squad_payload = _get_team_squad(team_id, dev_mode=False)
            squad_cache[str(team_id)] = squad_payload
            _save_cache(squad_cache, SQUAD_CACHE_FILE)

        players: List[Dict] = squad_payload[0]["players"]
        for p in players:
            pid = str(p["id"])
            if pid in player_cache:
                print(f"   • {p['name']:<20}  ▶ details from cache")
            else:
                print(f"   • {p['name']:<20}  🌐 fetching details …")
                player_cache[pid] = get_player_details(p["id"], dev_mode=False)
                _save_cache(player_cache, PLAYER_CACHE_FILE)

    print("\n🏁 All done — caches are up to date.")


if __name__ == "__main__":
    fetch()
