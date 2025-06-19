from loguru import logger

from pl_squad.tools import (
    get_full_team_details,
    get_player_details,
    get_team_squad,
    list_clubs,
    search_player,
)

if __name__ == "__main__":
    TEAM_ID = 42  # Arsenal
    PLAYER_ID = 19465  # David Raya

    dev_mode = False

    logger.info("Fetching squad for team {}", TEAM_ID)
    squad = get_team_squad(TEAM_ID, dev_mode=dev_mode)
    logger.info("Squad size: {}", len(squad[0]["players"]))

    logger.info("Fetching details for player {}", PLAYER_ID)
    player_details = get_player_details(PLAYER_ID, dev_mode=dev_mode)
    logger.info(player_details)

    logger.info("Fetching full team details...")
    profiles = get_full_team_details(TEAM_ID, dev_mode=True)
    logger.info("Fetched {} player profiles", len(profiles))

    logger.info("Listing all clubs from Premier League...")
    team_data = list_clubs(2024, dev_mode=dev_mode)
    logger.info("Premier League clubs: {}", team_data)

    logger.info("Searching for player by name...")
    player_data = search_player("Robert Lewandowski", dev_mode=dev_mode)
    logger.info("Player data: {}", player_data)
