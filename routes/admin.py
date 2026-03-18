from flask import Blueprint, render_template, redirect, url_for, flash, request
from datetime import datetime
from models import db
from utils.helpers import login_required, admin_required
from services.prediction import PredictionService

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("")
@login_required
@admin_required
def index():
    with db.get_connection() as conn:
        players = conn.execute("SELECT * FROM players ORDER BY name").fetchall()
        matches = conn.execute("""
            SELECT m.*, COUNT(mp.id) as player_count
            FROM matches m
            LEFT JOIN match_performance mp ON m.id = mp.match_id
            GROUP BY m.id
            ORDER BY m.match_date DESC
        """).fetchall()

    model_info = PredictionService.get_model_info()

    return render_template(
        "admin.html", players=players, matches=matches, model_info=model_info
    )


@admin.route("/add_player", methods=["POST"])
@login_required
@admin_required
def add_player():
    name = request.form.get("name")
    position = request.form.get("position")
    jersey_number = request.form.get("jersey_number")
    age = request.form.get("age")
    nationality = request.form.get("nationality")

    if not name or not position:
        flash("Name and position are required", "error")
    return redirect(url_for("admin.index"))


@admin.route("/delete_all_players", methods=["POST"])
@login_required
@admin_required
def delete_all_players():
    with db.get_connection() as conn:
        conn.execute("DELETE FROM player_stats")
        conn.execute("DELETE FROM match_performance")
        conn.execute("DELETE FROM players")
        conn.commit()

    flash("All players deleted successfully!", "success")
    return redirect(url_for("admin.index"))


@admin.route("/delete_all_matches", methods=["POST"])
@login_required
@admin_required
def delete_all_matches():
    with db.get_connection() as conn:
        conn.execute("DELETE FROM match_performance")
        conn.execute("DELETE FROM matches")
        conn.commit()

    flash("All matches deleted successfully!", "success")
    return redirect(url_for("admin.index"))

    with db.get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO players (name, position, jersey_number, age, nationality)
            VALUES (?, ?, ?, ?, ?)
        """,
            (name, position, jersey_number, age, nationality),
        )

        player_id = cursor.lastrowid
        current_season = datetime.now().year
        conn.execute(
            """
            INSERT INTO player_stats (player_id, season)
            VALUES (?, ?)
        """,
            (player_id, str(current_season)),
        )

        conn.commit()

    flash("Player added successfully!", "success")
    return redirect(url_for("admin.index"))


@admin.route("/add_match", methods=["POST"])
@login_required
@admin_required
def add_match():
    match_date = request.form.get("match_date")
    opponent = request.form.get("opponent")
    venue = request.form.get("venue")
    team_goals = int(request.form.get("team_goals", 0))
    opponent_goals = int(request.form.get("opponent_goals", 0))
    possession = float(request.form.get("possession", 50))
    shots = int(request.form.get("shots", 0))
    shots_on_target = int(request.form.get("shots_on_target", 0))
    corners = int(request.form.get("corners", 0))
    fouls = int(request.form.get("fouls", 0))

    if team_goals > opponent_goals:
        result = "Win"
    elif team_goals < opponent_goals:
        result = "Loss"
    else:
        result = "Draw"

    with db.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO matches (match_date, opponent, venue, team_goals, 
                               opponent_goals, possession, shots, shots_on_target, 
                               corners, fouls, result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                match_date,
                opponent,
                venue,
                team_goals,
                opponent_goals,
                possession,
                shots,
                shots_on_target,
                corners,
                fouls,
                result,
            ),
        )

        conn.commit()

    flash("Match added successfully!", "success")
    return redirect(url_for("admin.index"))


@admin.route("/edit_player/<int:player_id>", methods=["POST"])
@login_required
@admin_required
def edit_player(player_id):
    name = request.form.get("name")
    position = request.form.get("position")
    jersey_number = request.form.get("jersey_number")
    age = request.form.get("age")
    nationality = request.form.get("nationality")

    with db.get_connection() as conn:
        conn.execute(
            """
            UPDATE players 
            SET name = ?, position = ?, jersey_number = ?, age = ?, nationality = ?
            WHERE id = ?
        """,
            (name, position, jersey_number, age, nationality, player_id),
        )

        conn.commit()

    flash("Player updated successfully!", "success")
    return redirect(url_for("admin.index"))


@admin.route("/edit_stats/<int:player_id>", methods=["POST"])
@login_required
@admin_required
def edit_player_stats(player_id):
    season = request.form.get("season")
    matches_played = int(request.form.get("matches_played", 0))
    goals = int(request.form.get("goals", 0))
    assists = int(request.form.get("assists", 0))
    passes_attempted = int(request.form.get("passes_attempted", 0))
    passes_completed = int(request.form.get("passes_completed", 0))
    minutes_played = int(request.form.get("minutes_played", 0))
    yellow_cards = int(request.form.get("yellow_cards", 0))
    red_cards = int(request.form.get("red_cards", 0))
    rating = float(request.form.get("rating", 0))

    with db.get_connection() as conn:
        existing = conn.execute(
            """
            SELECT id FROM player_stats WHERE player_id = ? AND season = ?
        """,
            (player_id, season),
        ).fetchone()

        if existing:
            conn.execute(
                """
                UPDATE player_stats 
                SET matches_played = ?, goals = ?, assists = ?, 
                    passes_attempted = ?, passes_completed = ?, minutes_played = ?,
                    yellow_cards = ?, red_cards = ?, rating = ?
                WHERE player_id = ? AND season = ?
            """,
                (
                    matches_played,
                    goals,
                    assists,
                    passes_attempted,
                    passes_completed,
                    minutes_played,
                    yellow_cards,
                    red_cards,
                    rating,
                    player_id,
                    season,
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO player_stats (player_id, season, matches_played, goals, assists,
                                        passes_attempted, passes_completed, minutes_played,
                                        yellow_cards, red_cards, rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    player_id,
                    season,
                    matches_played,
                    goals,
                    assists,
                    passes_attempted,
                    passes_completed,
                    minutes_played,
                    yellow_cards,
                    red_cards,
                    rating,
                ),
            )

        conn.commit()

    flash("Player statistics updated successfully!", "success")
    return redirect(url_for("admin.index"))


@admin.route("/delete_player/<int:player_id>", methods=["POST"])
@login_required
@admin_required
def delete_player(player_id):
    with db.get_connection() as conn:
        conn.execute("DELETE FROM players WHERE id = ?", (player_id,))
        conn.commit()

    flash("Player deleted successfully!", "success")
    return redirect(url_for("admin.index"))


@admin.route("/delete_match/<int:match_id>", methods=["POST"])
@login_required
@admin_required
def delete_match(match_id):
    with db.get_connection() as conn:
        conn.execute("DELETE FROM matches WHERE id = ?", (match_id,))
        conn.commit()

    flash("Match deleted successfully!", "success")
    return redirect(url_for("admin.index"))


@admin.route("/train_model", methods=["POST"])
@login_required
@admin_required
def train_model():
    result, message = PredictionService.train_model()

    if result:
        flash(message, "success")
    else:
        flash(message, "warning")

    return redirect(url_for("admin.index"))


@admin.route("/delete_model", methods=["POST"])
@login_required
@admin_required
def delete_model():
    PredictionService.delete_model()
    flash("Model deleted successfully!", "success")
    return redirect(url_for("admin.index"))
