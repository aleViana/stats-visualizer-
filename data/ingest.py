"""Builds data/wc_data.json from two free, public-domain GitHub datasets.

Run once (or re-run to refresh):  python data/ingest.py

Sources:
- Tournament summaries (host, winner, runner-up, etc. for all 22 editions):
  https://raw.githubusercontent.com/lightbluetitan/fifa_world_cup_1930_2022/main/data/fifa_world_cup_1930_2022.csv
- Match-level results (all international matches since 1872, filtered to
  tournament == "FIFA World Cup"):
  https://raw.githubusercontent.com/martj42/international_results/master/results.csv
"""

import csv
import io
import json
from pathlib import Path

import requests

SUMMARY_URL = (
    "https://raw.githubusercontent.com/lightbluetitan/fifa_world_cup_1930_2022"
    "/main/data/fifa_world_cup_1930_2022.csv"
)
RESULTS_URL = (
    "https://raw.githubusercontent.com/martj42/international_results"
    "/master/results.csv"
)
OUTPUT_PATH = Path(__file__).parent / "wc_data.json"
LAST_HISTORICAL_YEAR = 2026


def fetch_csv_rows(url: str) -> list[dict]:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return list(csv.DictReader(io.StringIO(response.text)))


def build_tournaments(summary_rows: list[dict]) -> dict[int, dict]:
    tournaments = {}
    for row in summary_rows:
        year = int(row["year"])
        if year > LAST_HISTORICAL_YEAR:
            continue
        tournaments[year] = {
            "year": year,
            "host": row["host_country"],
            "host_continent": row["host_continent"],
            "winner": row["winner"],
            "runner_up": row["second_place"],
            "third": row["third_place"],
            "fourth": row["fourth_place"],
            "teams": int(row["total_teams"]),
            "matches": [],
        }
    return tournaments


def attach_matches(tournaments: dict[int, dict], result_rows: list[dict]) -> None:
    for row in result_rows:
        if row["tournament"] != "FIFA World Cup":
            continue
        year = int(row["date"][:4])
        if year not in tournaments:
            continue
        if row["home_score"] in ("", "NA") or row["away_score"] in ("", "NA"):
            continue
        tournaments[year]["matches"].append(
            {
                "date": row["date"],
                "home_team": row["home_team"],
                "away_team": row["away_team"],
                "home_score": int(row["home_score"]),
                "away_score": int(row["away_score"]),
                "city": row["city"],
                "country": row["country"],
                "neutral": row["neutral"] == "TRUE",
            }
        )
    for tournament in tournaments.values():
        tournament["matches"].sort(key=lambda m: m["date"])


def build_team_index(tournaments: dict[int, dict]) -> dict[str, dict]:
    team_index: dict[str, dict] = {}

    def team(name: str) -> dict:
        return team_index.setdefault(
            name,
            {
                "titles": 0,
                "runner_up": 0,
                "played": 0,
                "won": 0,
                "drawn": 0,
                "lost": 0,
                "goals_for": 0,
                "goals_against": 0,
                "tournaments_played": set(),
            },
        )

    for t in tournaments.values():
        team(t["winner"])["titles"] += 1
        team(t["runner_up"])["runner_up"] += 1
        for m in t["matches"]:
            home, away = team(m["home_team"]), team(m["away_team"])
            home["tournaments_played"].add(t["year"])
            away["tournaments_played"].add(t["year"])
            home["played"] += 1
            away["played"] += 1
            home["goals_for"] += m["home_score"]
            home["goals_against"] += m["away_score"]
            away["goals_for"] += m["away_score"]
            away["goals_against"] += m["home_score"]
            if m["home_score"] > m["away_score"]:
                home["won"] += 1
                away["lost"] += 1
            elif m["home_score"] < m["away_score"]:
                away["won"] += 1
                home["lost"] += 1
            else:
                home["drawn"] += 1
                away["drawn"] += 1

    for stats in team_index.values():
        stats["tournaments_played"] = len(stats["tournaments_played"])

    return team_index


def main() -> None:
    summary_rows = fetch_csv_rows(SUMMARY_URL)
    result_rows = fetch_csv_rows(RESULTS_URL)

    tournaments = build_tournaments(summary_rows)
    attach_matches(tournaments, result_rows)
    team_index = build_team_index(tournaments)

    data = {
        "tournaments": [tournaments[year] for year in sorted(tournaments)],
        "team_index": team_index,
    }
    OUTPUT_PATH.write_text(json.dumps(data, indent=2))
    print(f"Wrote {len(data['tournaments'])} tournaments and "
          f"{len(team_index)} teams to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
