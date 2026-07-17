import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import app as app_module


def test_2022_final_result():
    tournament = app_module.TOURNAMENTS_BY_YEAR[2022]
    assert tournament["winner"] == "Argentina"
    assert tournament["runner_up"] == "France"
    assert len(tournament["matches"]) == 64


def test_brazil_has_most_titles():
    assert app_module.TEAM_INDEX["Brazil"]["titles"] == 5
    most_titled = max(app_module.TEAM_INDEX, key=lambda n: app_module.TEAM_INDEX[n]["titles"])
    assert most_titled == "Brazil"


def test_team_goal_difference_consistent_with_matches():
    stats = app_module.TEAM_INDEX["Brazil"]
    assert stats["won"] + stats["drawn"] + stats["lost"] == stats["played"]





