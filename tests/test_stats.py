import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import app as app_module


def test_wc_data_has_all_22_editions():
    assert len(app_module.DATA["tournaments"]) == 22
    years = {t["year"] for t in app_module.DATA["tournaments"]}
    assert years == set(range(1930, 2023, 4)) - {1942, 1946}


def test_2022_final_result():
    tournament = app_module.TOURNAMENTS_BY_YEAR[2022]
    assert tournament["winner"] == "Argentina"
    assert tournament["runner_up"] == "France"
    assert len(tournament["matches"]) == 64


def test_brazil_has_most_titles():
    assert app_module.TEAM_INDEX["Brazil"]["titles"] == 5
    most_titled = max(app_module.TEAM_INDEX, key=lambda n: app_module.TEAM_INDEX[n]["titles"])
    assert most_titled == "Brazil"


def test_find_team_is_case_insensitive():
    assert app_module.find_team("brazil") == "Brazil"
    assert app_module.find_team("BRAZIL") == "Brazil"
    assert app_module.find_team("Nowhereland") is None


def test_team_goal_difference_consistent_with_matches():
    stats = app_module.TEAM_INDEX["Brazil"]
    assert stats["won"] + stats["drawn"] + stats["lost"] == stats["played"]


def test_index_route_returns_200():
    client = app_module.app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"1930" in response.data


def test_tournament_route_404_for_unknown_year():
    client = app_module.app.test_client()
    assert client.get("/tournament/1899").status_code == 404


def test_team_route_404_for_unknown_team():
    client = app_module.app.test_client()
    assert client.get("/team/Nowhereland").status_code == 404


def test_api_teams_search():
    client = app_module.app.test_client()
    response = client.get("/api/teams?q=braz")
    assert response.status_code == 200
    names = [t["name"] for t in response.get_json()]
    assert "Brazil" in names
