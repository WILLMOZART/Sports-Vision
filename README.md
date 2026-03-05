# SportVision Analytics

A comprehensive sports analytics web application built with Python Flask, featuring player statistics, team analytics, CSV data upload, machine learning match predictions, and an admin panel.

![SportVision Analytics](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

### 1. Player Statistics Dashboard
- View all players with key metrics (goals, assists, matches played)
- Detailed player profiles with performance trends
- Pass accuracy calculation
- Season-by-season statistics
- Interactive charts using Chart.js

### 2. Team Analytics
- Win rate calculation
- Goals per match average
- Possession statistics
- Last 5 match performance visualization
- Results distribution charts

### 3. CSV Upload System
- Upload player datasets
- Upload match datasets
- Automatic data validation
- Sample CSV files included

### 4. Machine Learning Prediction
- Logistic Regression model for match outcome prediction
- Predicts Win/Draw/Loss based on key metrics
- Confidence scores and probability breakdown
- Automatic model training on data upload

### 5. Admin Panel
- Add/Edit/Delete players
- Add/Delete matches
- Edit player statistics
- Manual ML model retraining

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python Flask |
| Frontend | HTML5, CSS3, JavaScript |
| Charts | Chart.js (CDN) |
| Database | SQLite |
| Data Processing | pandas, NumPy |
| Machine Learning | scikit-learn |

## Project Structure

```
sportvision_analytics/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── data/                  # Database folder
│   └── sportvision.db     # SQLite database (created on first run)
├── uploads/               # Temporary upload folder
├── static/                # Static assets
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── sample_players.csv # Sample player data
│   └── sample_matches.csv # Sample match data
└── templates/             # Jinja2 HTML templates
    ├── base.html         # Base template
    ├── dashboard.html    # Main dashboard
    ├── players.html      # Player list
    ├── player_detail.html # Player profile
    ├── team.html         # Team analytics
    ├── upload.html       # CSV upload
    ├── predict.html      # ML prediction
    └── admin.html        # Admin panel
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download
```bash
cd sportvision_analytics
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

### Step 5: Access the Application
Open your browser and navigate to:
```
http://localhost:5000
```

## Usage Guide

### Getting Started

1. **Add Players**: Go to Admin Panel → Players → Add Player
2. **Add Matches**: Go to Admin Panel → Matches → Add Match
3. **Upload CSV**: Use the Upload Data page for bulk imports
4. **View Analytics**: Check Dashboard and Team Analytics pages
5. **Make Predictions**: Use the Predict page after adding 10+ matches

### CSV Upload Format

#### Players CSV
```csv
name,position,jersey_number,age,nationality
John Smith,Forward,9,25,England
Mike Johnson,Midfielder,8,28,Spain
```

#### Matches CSV
```csv
match_date,opponent,venue,team_goals,opponent_goals,possession,shots,shots_on_target,corners,fouls
2024-01-15,Team A,Home,3,1,58.5,12,8,6,10
```

### Machine Learning Model

The application uses **Logistic Regression** to predict match outcomes.

#### How It Works:
1. **Feature Extraction**: The model uses 5 features:
   - Ball possession percentage
   - Number of shots
   - Shots on target
   - Corner kicks
   - Home/Away venue

2. **Training**: The model trains automatically when you have 10+ matches
   - Data is standardized using StandardScaler
   - Logistic Regression learns patterns from historical data
   - Model is saved to disk for future predictions

3. **Prediction**: For new matches, the model outputs:
   - Predicted outcome (Win/Draw/Loss)
   - Confidence percentage
   - Probability distribution across all outcomes

#### Improving Accuracy:
- Add more match data (20+ matches recommended)
- Ensure data quality and consistency
- Include both home and away matches

## Key Routes

| Route | Description |
|-------|-------------|
| `/` | Dashboard |
| `/players` | Player list |
| `/player/<id>` | Player profile |
| `/team` | Team analytics |
| `/upload` | CSV upload |
| `/predict` | ML prediction |
| `/admin` | Admin panel |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/player_stats/<id>` | Get player stats JSON |
| `/api/team_performance` | Get team performance JSON |

## Customization

### Changing Colors
Edit CSS variables in `static/css/style.css`:
```css
:root {
    --primary-color: #3b82f6;    /* Main blue */
    --secondary-color: #10b981;   /* Success green */
    --danger-color: #ef4444;      /* Error red */
    /* ... */
}
```

### Adding New Statistics
1. Update database schema in `init_database()`
2. Modify forms in admin templates
3. Update calculation functions

## Troubleshooting

### Common Issues

**"Not enough data to train model"**
- Add at least 10 matches before using predictions

**"Database locked"**
- Close any database viewers while running the app
- Restart the Flask server

**Charts not displaying**
- Check internet connection (Chart.js loads from CDN)
- Check browser console for JavaScript errors

## Development

### Adding New Features
1. Create route in `app.py`
2. Create template in `templates/`
3. Add navigation link in `base.html`
4. Add styles in `style.css`

### Database Migrations
Since SQLite is used, schema changes require:
1. Delete existing database file
2. Modify `init_database()` function
3. Restart the application

## License

This project is open source and available under the MIT License.

## Credits

Built with:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Chart.js](https://www.chart.js/) - Interactive charts
- [pandas](https://pandas.pydata.org/) - Data manipulation
- [scikit-learn](https://scikit-learn.org/) - Machine learning

---

**Happy Analyzing!** &#9917;
