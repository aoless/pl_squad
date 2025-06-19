import pytest

from pl_squad.tools import (
    _get_team_squad,
    get_full_team_details,
    get_player_details,
    list_clubs,
    search_player,
)


def test_get_team_squad_dev_mode_found():
    """Test retrieving a team's squad in dev mode with a valid team ID."""
    squad = _get_team_squad(42, dev_mode=True)  # Arsenal
    assert squad
    assert isinstance(squad, list)
    assert "players" in squad[0]


def test_get_team_squad_dev_mode_not_found():
    """Test retrieving a team's squad in dev mode with an invalid team ID."""
    with pytest.raises(KeyError):
        _get_team_squad(9999, dev_mode=True)


def test_get_player_details_dev_mode_found():
    """Test retrieving player details in dev mode with a valid player ID."""
    player_details = get_player_details(19465, dev_mode=True)  # David Raya
    assert player_details
    assert isinstance(player_details, list)
    assert "player" in player_details[0]
    assert player_details[0]["player"]["id"] == 19465


def test_list_clubs_dev_mode():
    """Test listing all clubs in dev mode."""
    clubs = list_clubs(dev_mode=True)
    assert clubs
    assert isinstance(clubs, list)
    assert len(clubs) > 0
    assert "team" in clubs[0]


def test_search_player_dev_mode():
    """Test searching for a player in dev mode."""
    players = search_player("any name", dev_mode=True)
    assert players
    assert isinstance(players, list)


def test_get_full_team_details_dev_mode():
    """Test retrieving full team details in dev mode."""
    team_details = get_full_team_details(42, dev_mode=True)  # Arsenal
    assert team_details
    assert isinstance(team_details, list)
    assert len(team_details) > 0
    # Each item in the list is the response for a single player, which is a list containing a dict
    assert "player" in team_details[0][0]
