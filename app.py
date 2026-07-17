from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request

from data.head_to_head import WINNERS, compute_head_to_head, compute_summary

DATA_PATH = Path(__file__).parent / "data" / "wc_data.json"

app = Flask(__name__)


def load_data() -> dict:
    return json.loads(DATA_PATH.read_text())


DATA = load_data()
TOURNAMENTS_BY_YEAR = {t["year"]: t for t in DATA["tournaments"]}
TEAM_INDEX = DATA["team_index"]


def find_team(name: str) -> str | None:
    """Case-insensitive lookup, returns the canonical team name or None."""
    lower = name.lower()
    for team_name in TEAM_INDEX:
        if team_name.lower() == lower:
            return team_name
    return None


@app.route("/")
def index():
    return render_template("index.html", tournaments=DATA["tournaments"])


@app.route("/tournament/<int:year>")
def tournament_detail(year: int):
    tournament = TOURNAMENTS_BY_YEAR.get(year)
    if tournament is None:
        abort(404)
    return render_template("tournament.html", tournament=tournament)


@app.route("/stats")
def stats():
    matches = [m for t in DATA["tournaments"] for m in t["matches"]]
    table = compute_head_to_head(matches, WINNERS)
    summary = compute_summary(table)
    return render_template("stats.html", teams=WINNERS, table=table, summary=summary)


@app.route("/team/<name>")
def team_detail(name: str):
    canonical = find_team(name)
    if canonical is None:
        abort(404)
    return render_template(
        "team.html", team_name=canonical, stats=TEAM_INDEX[canonical]
    )


@app.route("/api/tournaments")
def api_tournaments():
    summaries = [
        {k: v for k, v in t.items() if k != "matches"} for t in DATA["tournaments"]
    ]
    return jsonify(summaries)


@app.route("/api/tournaments/<int:year>")
def api_tournament_detail(year: int):
    tournament = TOURNAMENTS_BY_YEAR.get(year)
    if tournament is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(tournament)


@app.route("/api/teams")
def api_teams():
    query = request.args.get("q", "").lower()
    names = [name for name in TEAM_INDEX if query in name.lower()]
    names.sort(key=lambda n: (-TEAM_INDEX[n]["titles"], n))
    return jsonify([{"name": name, **TEAM_INDEX[name]} for name in names])


@app.route("/api/teams/<name>")
def api_team_detail(name: str):
    canonical = find_team(name)
    if canonical is None:
        return jsonify({"error": "not found"}), 404
    return jsonify({"name": canonical, **TEAM_INDEX[canonical]})


if __name__ == "__main__":
    app.run(debug=True)
