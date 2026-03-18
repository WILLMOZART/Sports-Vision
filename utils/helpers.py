import os
import re
from functools import wraps
from flask import session, redirect, url_for, flash
from models import db


def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        from config import Config

        allowed_extensions = Config.ALLOWED_EXTENSIONS

    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def calculate_pass_accuracy(attempted, completed):
    if attempted == 0:
        return 0.0
    return round((completed / attempted) * 100, 2)


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_username(username):
    return len(username) >= 3 and bool(re.match(r"^[a-zA-Z0-9_]+$", username))


def validate_password(password):
    return len(password) >= 6


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") != "admin":
            flash("Admin access required", "error")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)

    return decorated_function


def get_formation_stats():
    with db.get_connection() as conn:
        players = conn.execute("""
            SELECT p.id, p.name, p.position,
                   COALESCE(SUM(ps.goals), 0) as total_goals,
                   COALESCE(SUM(ps.assists), 0) as total_assists
            FROM players p
            LEFT JOIN player_stats ps ON p.id = ps.player_id
            GROUP BY p.id
            ORDER BY total_goals DESC
        """).fetchall()

    if not players:
        return None

    positions = {"Goalkeeper": 0, "Defender": 0, "Midfielder": 0, "Forward": 0}
    top_players = []

    for p in players:
        if p["position"] in positions:
            positions[p["position"]] += 1
        top_players.append(
            {"name": p["name"], "position": p["position"], "goals": p["total_goals"]}
        )

    formations = [
        {
            "name": "4-3-3",
            "defenders": 4,
            "midfielders": 3,
            "forwards": 3,
            "description": "Attacking formation",
            "best_for": "Strong attacking options",
        },
        {
            "name": "4-4-2",
            "defenders": 4,
            "midfielders": 4,
            "forwards": 2,
            "description": "Classic balanced",
            "best_for": "Good midfield control",
        },
        {
            "name": "3-5-2",
            "defenders": 3,
            "midfielders": 5,
            "forwards": 2,
            "description": "Aggressive with 5 midfielders",
            "best_for": "Control the midfield",
        },
        {
            "name": "5-4-1",
            "defenders": 5,
            "midfielders": 4,
            "forwards": 1,
            "description": "Defensive setup",
            "best_for": "Strong defense",
        },
        {
            "name": "4-2-3-1",
            "defenders": 4,
            "midfielders": 5,
            "forwards": 1,
            "description": "Modern formation",
            "best_for": "Balanced play",
        },
        {
            "name": "5-3-2",
            "defenders": 5,
            "midfielders": 3,
            "forwards": 2,
            "description": "Defensive with 2 forwards",
            "best_for": "Counter-attack",
        },
        {
            "name": "4-1-4-1",
            "defenders": 4,
            "midfielders": 5,
            "forwards": 1,
            "description": "Deep midfield",
            "best_for": "Extra protection",
        },
    ]

    defenders = positions.get("Defender", 0)
    midfielders = positions.get("Midfielder", 0)
    forwards = positions.get("Forward", 0)

    valid_formations = []
    for f in formations:
        if (
            defenders >= f["defenders"]
            and midfielders >= f["midfielders"]
            and forwards >= f["forwards"]
        ):
            valid_formations.append(f)

    if not valid_formations:
        valid_formations = [formations[0]]

    return {
        "positions": positions,
        "formations": valid_formations[:4],
        "top_scorers": top_players[:5],
    }


def get_squad_with_formation():
    with db.get_connection() as conn:
        players = conn.execute("""
            SELECT p.id, p.name, p.position,
                   COALESCE(SUM(ps.goals), 0) as total_goals,
                   COALESCE(SUM(ps.assists), 0) as total_assists,
                   COALESCE(AVG(ps.rating), 0) as avg_rating
            FROM players p
            LEFT JOIN player_stats ps ON p.id = ps.player_id
            GROUP BY p.id
            ORDER BY total_goals DESC, avg_rating DESC
        """).fetchall()

    if not players:
        return None

    by_position = {"Goalkeeper": [], "Defender": [], "Midfielder": [], "Forward": []}

    for p in players:
        if p["position"] in by_position:
            by_position[p["position"]].append(
                {
                    "id": p["id"],
                    "name": p["name"],
                    "goals": p["total_goals"],
                    "assists": p["total_assists"],
                    "rating": round(p["avg_rating"], 1),
                }
            )

    formations = [
        {"name": "4-3-3", "defenders": 4, "midfielders": 3, "forwards": 3},
        {"name": "4-4-2", "defenders": 4, "midfielders": 4, "forwards": 2},
        {"name": "3-5-2", "defenders": 3, "midfielders": 5, "forwards": 2},
        {"name": "5-4-1", "defenders": 5, "midfielders": 4, "forwards": 1},
        {"name": "4-2-3-1", "defenders": 4, "midfielders": 5, "forwards": 1},
    ]

    valid_formations = []
    for f in formations:
        if (
            len(by_position["Defender"]) >= f["defenders"]
            and len(by_position["Midfielder"]) >= f["midfielders"]
            and len(by_position["Forward"]) >= f["forwards"]
            and len(by_position["Goalkeeper"]) >= 1
        ):
            valid_formations.append(f)

    if not valid_formations:
        valid_formations = formations[:1]

    best_formation = valid_formations[0]

    lineup = {
        "formation": best_formation["name"],
        "goalkeeper": by_position["Goalkeeper"][0]
        if by_position["Goalkeeper"]
        else None,
        "defenders": by_position["Defender"][: best_formation["defenders"]],
        "midfielders": by_position["Midfielder"][: best_formation["midfielders"]],
        "forwards": by_position["Forward"][: best_formation["forwards"]],
        "substitutes": {
            "Goalkeeper": by_position["Goalkeeper"][1:3]
            if len(by_position["Goalkeeper"]) > 1
            else [],
            "Defenders": by_position["Defender"][
                best_formation["defenders"] : best_formation["defenders"] + 3
            ],
            "Midfielders": by_position["Midfielder"][
                best_formation["midfielders"] : best_formation["midfielders"] + 3
            ],
            "Forwards": by_position["Forward"][
                best_formation["forwards"] : best_formation["forwards"] + 3
            ],
        },
    }

    return lineup


def get_team_stats():
    with db.get_connection() as conn:
        matches = conn.execute(
            "SELECT * FROM matches ORDER BY match_date DESC"
        ).fetchall()

        if not matches:
            return None

        total = len(matches)
        wins = sum(1 for m in matches if m["result"] == "Win")
        losses = sum(1 for m in matches if m["result"] == "Loss")
        draws = sum(1 for m in matches if m["result"] == "Draw")

        return {
            "total_matches": total,
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "win_rate": round((wins / total) * 100, 2),
            "goals_scored": sum(m["team_goals"] for m in matches),
            "goals_conceded": sum(m["opponent_goals"] for m in matches),
            "goal_difference": sum(m["team_goals"] for m in matches)
            - sum(m["opponent_goals"] for m in matches),
            "avg_goals_per_match": round(
                sum(m["team_goals"] for m in matches) / total, 2
            ),
            "avg_possession": round(sum(m["possession"] for m in matches) / total, 2),
            "last_5_results": [m["result"] for m in reversed(matches[:5])],
        }


def get_player_full_stats(player_id):
    from models import db

    with db.get_connection() as conn:
        player = conn.execute(
            "SELECT * FROM players WHERE id = ?", (player_id,)
        ).fetchone()

        if not player:
            return None

        stats = conn.execute(
            """
            SELECT * FROM player_stats 
            WHERE player_id = ? 
            ORDER BY season DESC
        """,
            (player_id,),
        ).fetchall()

        total_matches = sum(s["matches_played"] for s in stats) if stats else 0
        total_goals = sum(s["goals"] for s in stats) if stats else 0
        total_assists = sum(s["assists"] for s in stats) if stats else 0
        total_passes_attempted = (
            sum(s["passes_attempted"] for s in stats) if stats else 0
        )
        total_passes_completed = (
            sum(s["passes_completed"] for s in stats) if stats else 0
        )

        performances = conn.execute(
            """
            SELECT mp.*, m.match_date 
            FROM match_performance mp
            JOIN matches m ON mp.match_id = m.id
            WHERE mp.player_id = ?
            ORDER BY m.match_date DESC
            LIMIT 10
        """,
            (player_id,),
        ).fetchall()

        return {
            "player": player,
            "stats": stats,
            "total_matches": total_matches,
            "total_goals": total_goals,
            "total_assists": total_assists,
            "pass_accuracy": calculate_pass_accuracy(
                total_passes_attempted, total_passes_completed
            ),
            "performances": performances,
        }
