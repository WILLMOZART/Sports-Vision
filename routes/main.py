from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db
from utils.helpers import (
    get_team_stats,
    get_player_full_stats,
    login_required,
    get_formation_stats,
    get_squad_with_formation,
)
from config import Config

main = Blueprint("main", __name__)


@main.route("/dashboard")
@login_required
def dashboard():
    with db.get_connection() as conn:
        players_count = conn.execute(
            "SELECT COUNT(*) as count FROM players"
        ).fetchone()["count"]
        matches_count = conn.execute(
            "SELECT COUNT(*) as count FROM matches"
        ).fetchone()["count"]

        top_scorers = conn.execute("""
            SELECT p.name, p.position, SUM(ps.goals) as total_goals
            FROM players p
            JOIN player_stats ps ON p.id = ps.player_id
            GROUP BY p.id
            ORDER BY total_goals DESC
            LIMIT 5
        """).fetchall()

        recent_matches = conn.execute("""
            SELECT * FROM matches 
            ORDER BY match_date DESC 
            LIMIT 5
        """).fetchall()

        team_stats = get_team_stats()

    return render_template(
        "dashboard.html",
        players_count=players_count,
        matches_count=matches_count,
        top_scorers=top_scorers,
        recent_matches=recent_matches,
        team_stats=team_stats,
    )


@main.route("/players")
def players():
    with db.get_connection() as conn:
        players_list = conn.execute("""
            SELECT p.*, 
                   COALESCE(SUM(ps.goals), 0) as total_goals,
                   COALESCE(SUM(ps.assists), 0) as total_assists,
                   COALESCE(SUM(ps.matches_played), 0) as total_matches
            FROM players p
            LEFT JOIN player_stats ps ON p.id = ps.player_id
            GROUP BY p.id
            ORDER BY p.name
        """).fetchall()

    return render_template("players.html", players=players_list)


@main.route("/player/<int:player_id>")
def player_detail(player_id):
    stats = get_player_full_stats(player_id)

    if not stats:
        flash("Player not found!", "error")
        return redirect(url_for("main.players"))

    return render_template("player_detail.html", api_key=Config.API_KEY, **stats)


@main.route("/team")
def team_analytics():
    team_stats = get_team_stats()
    formation_stats = get_formation_stats()
    squad = get_squad_with_formation()

    if not team_stats:
        flash("No match data available. Add matches to see analytics.", "warning")
        return render_template(
            "team.html", team_stats=None, formation_stats=formation_stats, squad=squad
        )

    with db.get_connection() as conn:
        matches = conn.execute(
            "SELECT * FROM matches ORDER BY match_date ASC"
        ).fetchall()

    return render_template(
        "team.html",
        team_stats=team_stats,
        formation_stats=formation_stats,
        squad=squad,
        match_dates=[m["match_date"] for m in matches],
        goals_scored=[m["team_goals"] for m in matches],
        goals_conceded=[m["opponent_goals"] for m in matches],
        possession=[m["possession"] for m in matches],
    )
