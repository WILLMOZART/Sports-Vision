from functools import wraps
from flask import Blueprint, jsonify, request, current_app
from models import db

api = Blueprint("api", __name__, url_prefix="/api")


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config.get("API_ENABLED", True):
            return jsonify({"error": "API is disabled"}), 503

        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return jsonify({"error": "Missing API key. Add 'X-API-Key' header"}), 401

        if api_key != current_app.config.get("API_KEY"):
            return jsonify({"error": "Invalid API key"}), 403

        return f(*args, **kwargs)

    return decorated_function


@api.route("/player_stats/<int:player_id>")
@require_api_key
def player_stats(player_id):
    with db.get_connection() as conn:
        stats = conn.execute(
            """
            SELECT season, goals, assists, matches_played, rating
            FROM player_stats
            WHERE player_id = ?
            ORDER BY season
        """,
            (player_id,),
        ).fetchall()

    return jsonify([dict(row) for row in stats])


@api.route("/team_performance")
@require_api_key
def team_performance():
    with db.get_connection() as conn:
        matches = conn.execute("""
            SELECT match_date, team_goals, opponent_goals, possession, result
            FROM matches
            ORDER BY match_date
        """).fetchall()

    return jsonify([dict(row) for row in matches])


@api.route("/players")
@require_api_key
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

    return jsonify([dict(row) for row in players_list])


@api.route("/matches")
@require_api_key
def matches():
    with db.get_connection() as conn:
        matches = conn.execute("""
            SELECT * FROM matches ORDER BY match_date DESC
        """).fetchall()

    return jsonify([dict(row) for row in matches])


@api.route("/matches", methods=["POST"])
@require_api_key
def create_match():
    data = request.get_json()

    required = ["match_date", "opponent", "venue"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    team_goals = data.get("team_goals", 0)
    opponent_goals = data.get("opponent_goals", 0)

    if team_goals > opponent_goals:
        result = "Win"
    elif team_goals < opponent_goals:
        result = "Loss"
    else:
        result = "Draw"

    with db.get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO matches (match_date, opponent, venue, team_goals, 
                               opponent_goals, possession, shots, shots_on_target, 
                               corners, fouls, result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["match_date"],
                data["opponent"],
                data["venue"],
                team_goals,
                opponent_goals,
                data.get("possession", 50),
                data.get("shots", 0),
                data.get("shots_on_target", 0),
                data.get("corners", 0),
                data.get("fouls", 0),
                result,
            ),
        )
        conn.commit()
        match_id = cursor.lastrowid

    return jsonify({"id": match_id, "result": result}), 201


@api.route("/players", methods=["POST"])
@require_api_key
def create_player():
    data = request.get_json()

    required = ["name", "position"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    with db.get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO players (name, position, jersey_number, age, nationality)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                data["name"],
                data["position"],
                data.get("jersey_number"),
                data.get("age"),
                data.get("nationality", "Unknown"),
            ),
        )
        conn.commit()
        player_id = cursor.lastrowid

    return jsonify({"id": player_id}), 201


@api.route("/info")
def api_info():
    """Get API information"""
    return jsonify(
        {
            "name": "SportVision Analytics API",
            "version": "1.0.0",
            "endpoints": [
                "/api/players",
                "/api/matches",
                "/api/player_stats/<id>",
                "/api/team_performance",
            ],
            "authentication": "X-API-Key header required",
        }
    )
