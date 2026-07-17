"""Head-to-head comparison between the 8 nations that have won the FIFA World Cup.

Run directly to print the table:  python data/head_to_head.py
"""

from __future__ import annotations

import json
from pathlib import Path

DATA_PATH = Path(__file__).parent / "wc_data.json"

# West Germany's titles (1954, 1974, 1990); treat them
# as the same nation as "Germany" for head-to-head purposes.
NAME_ALIASES = {"West Germany": "Germany"}

WINNERS = [
    "Brazil",
    "Germany",
    "Italy",
    "Argentina",
    "Uruguay",
    "France",
    "England",
    "Spain",
]

# Returns the canonical name for a team, handling aliases.
def _canonical(name: str) -> str:
    return NAME_ALIASES.get(name, name)

#Loads the matches from JSON file
def load_matches() -> list[dict]:
    data = json.loads(DATA_PATH.read_text())
    matches = []
    for tournament in data["tournaments"]:
        matches.extend(tournament["matches"])
    return matches

#Find matches between the teams and compute the head-to-head statistics 
def compute_head_to_head(
    matches: list[dict], teams: list[str] = WINNERS
) -> dict[str, dict[str, dict]]:
    """Returns table[a][b] = {"played", "won", "drawn", "lost", "win_pct"}.

    win_pct is a's win percentage in matches played against b; None if the
    two teams never met at a World Cup.
    """
    team_set = set(teams)
    table = {
        a: {b: {"played": 0, "won": 0, "drawn": 0, "lost": 0} for b in teams if b != a}
        for a in teams
    }

    for m in matches:
        home, away = _canonical(m["home_team"]), _canonical(m["away_team"])
        if home not in team_set or away not in team_set or home == away:
            continue
        home_score, away_score = m["home_score"], m["away_score"]
        for a, b, gf, ga in (
            (home, away, home_score, away_score),
            (away, home, away_score, home_score),
        ):
            cell = table[a][b]
            cell["played"] += 1
            if gf > ga:
                cell["won"] += 1
            elif gf < ga:
                cell["lost"] += 1

            else:
                cell["drawn"] += 1

    for a in teams:
        for cell in table[a].values():
            cell["win_pct"] = (
                round(100 * (cell["won"] + cell["drawn"] * 0.5) / cell["played"], 1) if cell["played"] else None
            )

    return table


def compute_summary(table: dict[str, dict[str, dict]]) -> list[dict]:
    """Aggregates each team's record against all other winners into one row,
    ranked by win percentage (descending, ties broken by matches won)."""
    summary = []
    for team, opponents in table.items():
        played = sum(c["played"] for c in opponents.values())
        won = sum(c["won"] for c in opponents.values())
        drawn = sum(c["drawn"] for c in opponents.values())
        lost = sum(c["lost"] for c in opponents.values())
        summary.append(
            {
                "team": team,
                "played": played,
                "won": won,
                "drawn": drawn,
                "lost": lost,
                "win_pct": round(100 * won / played, 1) if played else None,
            }
        )
    summary.sort(key=lambda r: (r["win_pct"] or -1, r["won"]), reverse=True)
    return summary


def print_table(table: dict[str, dict[str, dict]]) -> None:
    teams = list(table.keys())
    col_width = 10
    print("".ljust(12) + "".join(t[:9].rjust(col_width) for t in teams))
    for a in teams:
        row = a.ljust(12)
        for b in teams:
            if a == b:
                row += "—".rjust(col_width)
            else:
                pct = table[a][b]["win_pct"]
                row += ("n/a" if pct is None else f"{pct}%").rjust(col_width)
        print(row)


def print_summary(summary: list[dict]) -> None:
    print(f"\n{'Team':<12}{'P':>5}{'W':>5}{'D':>5}{'L':>5}{'Win%':>8}")
    for row in summary:
        pct = "n/a" if row["win_pct"] is None else f"{row['win_pct']}%"
        print(
            f"{row['team']:<12}{row['played']:>5}{row['won']:>5}"
            f"{row['drawn']:>5}{row['lost']:>5}{pct:>8}"
        )


def main() -> None:
    table = compute_head_to_head(load_matches())
    print_table(table)
    print_summary(compute_summary(table))


if __name__ == "__main__":
    main()
