"""
SportVision Analytics - Main Flask Application
===============================================
A comprehensive sports analytics platform with player statistics,
team analytics, CSV upload, ML predictions, and admin panel.

Author: SportVision Team
Tech Stack: Flask, SQLite, pandas, scikit-learn, Chart.js
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import json

# Machine Learning imports
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pickle

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'sportvision_secret_key_2024'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Database path
DATABASE = 'data/sportvision.db'

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def get_db_connection():
    """Create and return a database connection with row factory."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with all required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Players table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            jersey_number INTEGER,
            age INTEGER,
            nationality TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Player statistics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            season TEXT NOT NULL,
            matches_played INTEGER DEFAULT 0,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            passes_attempted INTEGER DEFAULT 0,
            passes_completed INTEGER DEFAULT 0,
            minutes_played INTEGER DEFAULT 0,
            yellow_cards INTEGER DEFAULT 0,
            red_cards INTEGER DEFAULT 0,
            rating REAL DEFAULT 0.0,
            FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
        )
    ''')
    
    # Matches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_date DATE NOT NULL,
            opponent TEXT NOT NULL,
            venue TEXT NOT NULL,
            team_goals INTEGER DEFAULT 0,
            opponent_goals INTEGER DEFAULT 0,
            possession REAL DEFAULT 50.0,
            shots INTEGER DEFAULT 0,
            shots_on_target INTEGER DEFAULT 0,
            corners INTEGER DEFAULT 0,
            fouls INTEGER DEFAULT 0,
            result TEXT DEFAULT 'Draw',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Match player performance (linking players to matches)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            minutes_played INTEGER DEFAULT 0,
            rating REAL DEFAULT 0.0,
            FOREIGN KEY (match_id) REFERENCES matches (id) ON DELETE CASCADE,
            FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_pass_accuracy(attempted, completed):
    """Calculate pass accuracy percentage."""
    if attempted == 0:
        return 0.0
    return round((completed / attempted) * 100, 2)

def get_team_stats():
    """Calculate comprehensive team statistics."""
    conn = get_db_connection()
    
    # Get all matches
    matches = conn.execute('SELECT * FROM matches ORDER BY match_date DESC').fetchall()
    
    if not matches:
        conn.close()
        return None
    
    total_matches = len(matches)
    wins = sum(1 for m in matches if m['result'] == 'Win')
    losses = sum(1 for m in matches if m['result'] == 'Loss')
    draws = sum(1 for m in matches if m['result'] == 'Draw')
    
    total_goals_scored = sum(m['team_goals'] for m in matches)
    total_goals_conceded = sum(m['opponent_goals'] for m in matches)
    avg_possession = round(sum(m['possession'] for m in matches) / total_matches, 2)
    
    # Last 5 matches for trend
    last_5 = matches[:5] if len(matches) >= 5 else matches
    last_5_results = [m['result'] for m in reversed(last_5)]
    
    conn.close()
    
    return {
        'total_matches': total_matches,
        'wins': wins,
        'losses': losses,
        'draws': draws,
        'win_rate': round((wins / total_matches) * 100, 2),
        'goals_scored': total_goals_scored,
        'goals_conceded': total_goals_conceded,
        'goal_difference': total_goals_scored - total_goals_conceded,
        'avg_goals_per_match': round(total_goals_scored / total_matches, 2),
        'avg_possession': avg_possession,
        'last_5_results': last_5_results
    }

def get_player_full_stats(player_id):
    """Get comprehensive statistics for a specific player."""
    conn = get_db_connection()
    
    player = conn.execute('SELECT * FROM players WHERE id = ?', (player_id,)).fetchone()
    
    if not player:
        conn.close()
        return None
    
    stats = conn.execute('''
        SELECT * FROM player_stats 
        WHERE player_id = ? 
        ORDER BY season DESC
    ''', (player_id,)).fetchall()
    
    # Aggregate stats across all seasons
    total_matches = sum(s['matches_played'] for s in stats) if stats else 0
    total_goals = sum(s['goals'] for s in stats) if stats else 0
    total_assists = sum(s['assists'] for s in stats) if stats else 0
    total_passes_attempted = sum(s['passes_attempted'] for s in stats) if stats else 0
    total_passes_completed = sum(s['passes_completed'] for s in stats) if stats else 0
    
    pass_accuracy = calculate_pass_accuracy(total_passes_attempted, total_passes_completed)
    
    # Get match performances for trend analysis
    performances = conn.execute('''
        SELECT mp.*, m.match_date 
        FROM match_performance mp
        JOIN matches m ON mp.match_id = m.id
        WHERE mp.player_id = ?
        ORDER BY m.match_date DESC
        LIMIT 10
    ''', (player_id,)).fetchall()
    
    conn.close()
    
    return {
        'player': player,
        'stats': stats,
        'total_matches': total_matches,
        'total_goals': total_goals,
        'total_assists': total_assists,
        'pass_accuracy': pass_accuracy,
        'performances': performances
    }

# ============================================================================
# MACHINE LEARNING FUNCTIONS
# ============================================================================

def train_prediction_model():
    """
    Train a logistic regression model to predict match outcomes.
    
    Features used:
    - possession: Ball possession percentage
    - shots: Number of shots taken
    - shots_on_target: Shots on target
    - corners: Number of corners
    - home_advantage: 1 if home, 0 if away
    
    Target: result (Win=2, Draw=1, Loss=0)
    """
    conn = get_db_connection()
    matches = conn.execute('''
        SELECT possession, shots, shots_on_target, corners, 
               CASE venue WHEN 'Home' THEN 1 ELSE 0 END as home_advantage,
               CASE result 
                   WHEN 'Win' THEN 2 
                   WHEN 'Draw' THEN 1 
                   ELSE 0 
               END as outcome
        FROM matches
    ''').fetchall()
    conn.close()
    
    if len(matches) < 10:
        return None, "Not enough data to train model (need at least 10 matches)"
    
    # Convert to DataFrame
    df = pd.DataFrame(matches)
    
    # Features and target
    X = df[['possession', 'shots', 'shots_on_target', 'corners', 'home_advantage']]
    y = df['outcome']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train model
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_scaled, y)
    
    # Calculate accuracy
    accuracy = model.score(X_scaled, y) * 100
    
    # Save model and scaler
    with open('data/model.pkl', 'wb') as f:
        pickle.dump(model, f)
    with open('data/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    return model, f"Model trained successfully! Accuracy: {accuracy:.2f}%"

def predict_match_outcome(possession, shots, shots_on_target, corners, is_home=True):
    """
    Predict match outcome using trained logistic regression model.
    
    Returns:
        dict with prediction, probabilities, and confidence
    """
    try:
        # Load model and scaler
        with open('data/model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('data/scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
    except FileNotFoundError:
        return None
    
    # Prepare input
    home_advantage = 1 if is_home else 0
    input_data = np.array([[possession, shots, shots_on_target, corners, home_advantage]])
    input_scaled = scaler.transform(input_data)
    
    # Predict
    prediction = model.predict(input_scaled)[0]
    probabilities = model.predict_proba(input_scaled)[0]
    
    outcome_map = {0: 'Loss', 1: 'Draw', 2: 'Win'}
    outcome = outcome_map[prediction]
    confidence = round(probabilities[prediction] * 100, 2)
    
    return {
        'prediction': outcome,
        'confidence': confidence,
        'probabilities': {
            'Loss': round(probabilities[0] * 100, 2),
            'Draw': round(probabilities[1] * 100, 2),
            'Win': round(probabilities[2] * 100, 2)
        }
    }

# ============================================================================
# CSV PROCESSING FUNCTIONS
# ============================================================================

def process_players_csv(filepath):
    """Process uploaded players CSV file."""
    try:
        df = pd.read_csv(filepath)
        conn = get_db_connection()
        
        required_cols = ['name', 'position']
        if not all(col in df.columns for col in required_cols):
            return False, "CSV must contain 'name' and 'position' columns"
        
        added_count = 0
        for _, row in df.iterrows():
            conn.execute('''
                INSERT INTO players (name, position, jersey_number, age, nationality)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['name'],
                row['position'],
                row.get('jersey_number', None),
                row.get('age', None),
                row.get('nationality', 'Unknown')
            ))
            added_count += 1
        
        conn.commit()
        conn.close()
        return True, f"Successfully added {added_count} players"
    
    except Exception as e:
        return False, f"Error processing CSV: {str(e)}"

def process_matches_csv(filepath):
    """Process uploaded matches CSV file."""
    try:
        df = pd.read_csv(filepath)
        conn = get_db_connection()
        
        required_cols = ['match_date', 'opponent', 'venue']
        if not all(col in df.columns for col in required_cols):
            return False, "CSV must contain 'match_date', 'opponent', and 'venue' columns"
        
        added_count = 0
        for _, row in df.iterrows():
            # Determine result
            team_goals = row.get('team_goals', 0)
            opponent_goals = row.get('opponent_goals', 0)
            
            if team_goals > opponent_goals:
                result = 'Win'
            elif team_goals < opponent_goals:
                result = 'Loss'
            else:
                result = 'Draw'
            
            conn.execute('''
                INSERT INTO matches (match_date, opponent, venue, team_goals, 
                                   opponent_goals, possession, shots, shots_on_target, 
                                   corners, fouls, result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['match_date'],
                row['opponent'],
                row['venue'],
                team_goals,
                opponent_goals,
                row.get('possession', 50.0),
                row.get('shots', 0),
                row.get('shots_on_target', 0),
                row.get('corners', 0),
                row.get('fouls', 0),
                result
            ))
            added_count += 1
        
        conn.commit()
        conn.close()
        return True, f"Successfully added {added_count} matches"
    
    except Exception as e:
        return False, f"Error processing CSV: {str(e)}"

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def dashboard():
    """Main dashboard showing overview of team and player stats."""
    conn = get_db_connection()
    
    # Get summary statistics
    players_count = conn.execute('SELECT COUNT(*) as count FROM players').fetchone()['count']
    matches_count = conn.execute('SELECT COUNT(*) as count FROM matches').fetchone()['count']
    
    # Get top scorers
    top_scorers = conn.execute('''
        SELECT p.name, p.position, SUM(ps.goals) as total_goals
        FROM players p
        JOIN player_stats ps ON p.id = ps.player_id
        GROUP BY p.id
        ORDER BY total_goals DESC
        LIMIT 5
    ''').fetchall()
    
    # Get recent matches
    recent_matches = conn.execute('''
        SELECT * FROM matches 
        ORDER BY match_date DESC 
        LIMIT 5
    ''').fetchall()
    
    # Get team stats
    team_stats = get_team_stats()
    
    conn.close()
    
    return render_template('dashboard.html',
                         players_count=players_count,
                         matches_count=matches_count,
                         top_scorers=top_scorers,
                         recent_matches=recent_matches,
                         team_stats=team_stats)

@app.route('/players')
def players():
    """Display all players with their statistics."""
    conn = get_db_connection()
    
    players = conn.execute('''
        SELECT p.*, 
               COALESCE(SUM(ps.goals), 0) as total_goals,
               COALESCE(SUM(ps.assists), 0) as total_assists,
               COALESCE(SUM(ps.matches_played), 0) as total_matches
        FROM players p
        LEFT JOIN player_stats ps ON p.id = ps.player_id
        GROUP BY p.id
        ORDER BY p.name
    ''').fetchall()
    
    conn.close()
    
    return render_template('players.html', players=players)

@app.route('/player/<int:player_id>')
def player_detail(player_id):
    """Display detailed statistics for a specific player."""
    stats = get_player_full_stats(player_id)
    
    if not stats:
        flash('Player not found!', 'error')
        return redirect(url_for('players'))
    
    return render_template('player_detail.html', **stats)

@app.route('/team')
def team_analytics():
    """Display team analytics and performance metrics."""
    team_stats = get_team_stats()
    
    if not team_stats:
        flash('No match data available. Add matches to see analytics.', 'warning')
        return render_template('team.html', team_stats=None)
    
    # Get match history for charts
    conn = get_db_connection()
    matches = conn.execute('''
        SELECT * FROM matches 
        ORDER BY match_date ASC
    ''').fetchall()
    conn.close()
    
    # Prepare data for Chart.js
    match_dates = [m['match_date'] for m in matches]
    goals_scored = [m['team_goals'] for m in matches]
    goals_conceded = [m['opponent_goals'] for m in matches]
    possession = [m['possession'] for m in matches]
    
    return render_template('team.html',
                         team_stats=team_stats,
                         match_dates=match_dates,
                         goals_scored=goals_scored,
                         goals_conceded=goals_conceded,
                         possession=possession)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Handle CSV file uploads for players and matches."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        upload_type = request.form.get('upload_type', 'players')
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process based on type
            if upload_type == 'players':
                success, message = process_players_csv(filepath)
            else:
                success, message = process_matches_csv(filepath)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            if success:
                flash(message, 'success')
            else:
                flash(message, 'error')
            
            return redirect(url_for('upload'))
        else:
            flash('Invalid file type. Please upload a CSV file.', 'error')
    
    return render_template('upload.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """Match outcome prediction using ML."""
    prediction = None
    
    if request.method == 'POST':
        possession = float(request.form.get('possession', 50))
        shots = int(request.form.get('shots', 10))
        shots_on_target = int(request.form.get('shots_on_target', 5))
        corners = int(request.form.get('corners', 5))
        venue = request.form.get('venue', 'Home')
        
        is_home = venue == 'Home'
        
        # Check if model exists, if not train it
        if not os.path.exists('data/model.pkl'):
            model, message = train_prediction_model()
            if model is None:
                flash(message, 'warning')
                return render_template('predict.html', prediction=None)
        
        prediction = predict_match_outcome(possession, shots, shots_on_target, corners, is_home)
        
        if prediction is None:
            flash('Error making prediction. Please ensure model is trained.', 'error')
    
    return render_template('predict.html', prediction=prediction)

@app.route('/admin')
def admin():
    """Admin panel main page."""
    conn = get_db_connection()
    
    players = conn.execute('SELECT * FROM players ORDER BY name').fetchall()
    matches = conn.execute('''
        SELECT m.*, 
               COUNT(mp.id) as player_count
        FROM matches m
        LEFT JOIN match_performance mp ON m.id = mp.match_id
        GROUP BY m.id
        ORDER BY m.match_date DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin.html', players=players, matches=matches)

# ============================================================================
# ADMIN API ROUTES
# ============================================================================

@app.route('/admin/add_player', methods=['POST'])
def add_player():
    """Add a new player to the database."""
    name = request.form.get('name')
    position = request.form.get('position')
    jersey_number = request.form.get('jersey_number')
    age = request.form.get('age')
    nationality = request.form.get('nationality')
    
    conn = get_db_connection()
    cursor = conn.execute('''
        INSERT INTO players (name, position, jersey_number, age, nationality)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, position, jersey_number, age, nationality))
    
    player_id = cursor.lastrowid
    
    # Initialize player stats for current season
    current_season = datetime.now().year
    conn.execute('''
        INSERT INTO player_stats (player_id, season)
        VALUES (?, ?)
    ''', (player_id, str(current_season)))
    
    conn.commit()
    conn.close()
    
    flash('Player added successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/add_match', methods=['POST'])
def add_match():
    """Add a new match to the database."""
    match_date = request.form.get('match_date')
    opponent = request.form.get('opponent')
    venue = request.form.get('venue')
    team_goals = int(request.form.get('team_goals', 0))
    opponent_goals = int(request.form.get('opponent_goals', 0))
    possession = float(request.form.get('possession', 50))
    shots = int(request.form.get('shots', 0))
    shots_on_target = int(request.form.get('shots_on_target', 0))
    corners = int(request.form.get('corners', 0))
    fouls = int(request.form.get('fouls', 0))
    
    # Determine result
    if team_goals > opponent_goals:
        result = 'Win'
    elif team_goals < opponent_goals:
        result = 'Loss'
    else:
        result = 'Draw'
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO matches (match_date, opponent, venue, team_goals, 
                           opponent_goals, possession, shots, shots_on_target, 
                           corners, fouls, result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (match_date, opponent, venue, team_goals, opponent_goals, 
          possession, shots, shots_on_target, corners, fouls, result))
    
    conn.commit()
    conn.close()
    
    flash('Match added successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/edit_player/<int:player_id>', methods=['POST'])
def edit_player(player_id):
    """Edit player information."""
    name = request.form.get('name')
    position = request.form.get('position')
    jersey_number = request.form.get('jersey_number')
    age = request.form.get('age')
    nationality = request.form.get('nationality')
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE players 
        SET name = ?, position = ?, jersey_number = ?, age = ?, nationality = ?
        WHERE id = ?
    ''', (name, position, jersey_number, age, nationality, player_id))
    
    conn.commit()
    conn.close()
    
    flash('Player updated successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/edit_stats/<int:player_id>', methods=['POST'])
def edit_player_stats(player_id):
    """Edit player statistics."""
    season = request.form.get('season')
    matches_played = int(request.form.get('matches_played', 0))
    goals = int(request.form.get('goals', 0))
    assists = int(request.form.get('assists', 0))
    passes_attempted = int(request.form.get('passes_attempted', 0))
    passes_completed = int(request.form.get('passes_completed', 0))
    minutes_played = int(request.form.get('minutes_played', 0))
    yellow_cards = int(request.form.get('yellow_cards', 0))
    red_cards = int(request.form.get('red_cards', 0))
    rating = float(request.form.get('rating', 0))
    
    conn = get_db_connection()
    
    # Check if stats exist for this season
    existing = conn.execute('''
        SELECT id FROM player_stats WHERE player_id = ? AND season = ?
    ''', (player_id, season)).fetchone()
    
    if existing:
        conn.execute('''
            UPDATE player_stats 
            SET matches_played = ?, goals = ?, assists = ?, 
                passes_attempted = ?, passes_completed = ?, minutes_played = ?,
                yellow_cards = ?, red_cards = ?, rating = ?
            WHERE player_id = ? AND season = ?
        ''', (matches_played, goals, assists, passes_attempted, passes_completed,
              minutes_played, yellow_cards, red_cards, rating, player_id, season))
    else:
        conn.execute('''
            INSERT INTO player_stats (player_id, season, matches_played, goals, assists,
                                    passes_attempted, passes_completed, minutes_played,
                                    yellow_cards, red_cards, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (player_id, season, matches_played, goals, assists, passes_attempted,
              passes_completed, minutes_played, yellow_cards, red_cards, rating))
    
    conn.commit()
    conn.close()
    
    flash('Player statistics updated successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete_player/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    """Delete a player and all associated data."""
    conn = get_db_connection()
    conn.execute('DELETE FROM players WHERE id = ?', (player_id,))
    conn.commit()
    conn.close()
    
    flash('Player deleted successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete_match/<int:match_id>', methods=['POST'])
def delete_match(match_id):
    """Delete a match and all associated performance data."""
    conn = get_db_connection()
    conn.execute('DELETE FROM matches WHERE id = ?', (match_id,))
    conn.commit()
    conn.close()
    
    flash('Match deleted successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/train_model', methods=['POST'])
def admin_train_model():
    """Train the ML model from admin panel."""
    model, message = train_prediction_model()
    
    if model:
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(url_for('admin'))

# ============================================================================
# API ENDPOINTS FOR AJAX REQUESTS
# ============================================================================

@app.route('/api/player_stats/<int:player_id>')
def api_player_stats(player_id):
    """API endpoint to get player stats for charts."""
    conn = get_db_connection()
    
    stats = conn.execute('''
        SELECT season, goals, assists, matches_played, rating
        FROM player_stats
        WHERE player_id = ?
        ORDER BY season
    ''', (player_id,)).fetchall()
    
    conn.close()
    
    return jsonify([dict(row) for row in stats])

@app.route('/api/team_performance')
def api_team_performance():
    """API endpoint to get team performance data."""
    conn = get_db_connection()
    
    matches = conn.execute('''
        SELECT match_date, team_goals, opponent_goals, possession, result
        FROM matches
        ORDER BY match_date
    ''').fetchall()
    
    conn.close()
    
    return jsonify([dict(row) for row in matches])

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Initialize database on first run
    if not os.path.exists(DATABASE):
        init_database()
        print("First run - database initialized!")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
