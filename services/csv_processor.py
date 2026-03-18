import pandas as pd
from models import db


class CSVService:
    REQUIRED_PLAYER_COLS = ["name", "position"]
    REQUIRED_MATCH_COLS = ["match_date", "opponent", "venue"]

    @classmethod
    def validate_player_csv(cls, filepath):
        try:
            df = pd.read_csv(filepath)
            missing = [col for col in cls.REQUIRED_PLAYER_COLS if col not in df.columns]

            if missing:
                return False, f"Missing columns: {', '.join(missing)}"

            return True, None
        except Exception as e:
            return False, str(e)

    @classmethod
    def validate_match_csv(cls, filepath):
        try:
            df = pd.read_csv(filepath)
            missing = [col for col in cls.REQUIRED_MATCH_COLS if col not in df.columns]

            if missing:
                return False, f"Missing columns: {', '.join(missing)}"

            return True, None
        except Exception as e:
            return False, str(e)

    @classmethod
    def process_players_csv(cls, filepath):
        try:
            valid, error = cls.validate_player_csv(filepath)
            if not valid:
                return False, error

            df = pd.read_csv(filepath)
            added = 0

            with db.get_connection() as conn:
                for _, row in df.iterrows():
                    conn.execute(
                        """
                        INSERT INTO players (name, position, jersey_number, age, nationality)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            row["name"],
                            row["position"],
                            row.get("jersey_number"),
                            row.get("age"),
                            row.get("nationality", "Unknown"),
                        ),
                    )
                    added += 1

                conn.commit()

            return True, f"Added {added} players"

        except Exception as e:
            return False, f"Error: {str(e)}"

    @classmethod
    def process_matches_csv(cls, filepath):
        try:
            valid, error = cls.validate_match_csv(filepath)
            if not valid:
                return False, error

            df = pd.read_csv(filepath)
            df = df.fillna(0)
            added = 0

            with db.get_connection() as conn:
                for _, row in df.iterrows():
                    team_goals = int(row.get("team_goals", 0))
                    opponent_goals = int(row.get("opponent_goals", 0))

                    if team_goals > opponent_goals:
                        result = "Win"
                    elif team_goals < opponent_goals:
                        result = "Loss"
                    else:
                        result = "Draw"

                    conn.execute(
                        """
                        INSERT INTO matches (match_date, opponent, venue, team_goals, 
                                           opponent_goals, possession, shots, shots_on_target, 
                                           corners, fouls, result)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            row["match_date"],
                            row["opponent"],
                            row["venue"],
                            team_goals,
                            opponent_goals,
                            row.get("possession", 50.0),
                            row.get("shots", 0),
                            row.get("shots_on_target", 0),
                            row.get("corners", 0),
                            row.get("fouls", 0),
                            result,
                        ),
                    )
                    added += 1

                conn.commit()

            return True, f"Added {added} matches"

        except Exception as e:
            return False, f"Error: {str(e)}"
