import os

from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = "cache"
SQUAD_CACHE = os.path.join(CACHE_DIR, "cache_squads.json")
PLAYER_CACHE = os.path.join(CACHE_DIR, "cache_players.json")
LEAGUE_CACHE = os.path.join(CACHE_DIR, "cache_premier_league.json")
SINGLE_PLAYER_CACHE = os.path.join(CACHE_DIR, "cache_single_player.json")


RAPIDAPI_API_KEY = os.getenv("RAPIDAPI_KEY")
if not RAPIDAPI_API_KEY:
    raise RuntimeError(
        "Environment variable RAPIDAPI_KEY is missing. "
        "Create a .env file or export the key before importing this module."
    )
