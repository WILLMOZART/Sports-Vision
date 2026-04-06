# Sports-Vision Analytics Documentation

---

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Guide](#user-guide)
4. [Admin Panel](#admin-panel)
5. [ML Predictions](#ml-predictions)
6. [API Documentation](#api-documentation)
7. [Development](#development)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

Sports-Vision Analytics is a comprehensive sports analytics platform that provides:
- Player statistics and performance tracking
- Team analytics and performance metrics
- CSV data upload for bulk imports
- Machine learning-based match outcome predictions
- REST API for programmatic access
- User authentication with role-based access

---

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/WILLMOZART/Sports-Vision.git
   cd Sports-Vision
   ```

2. **Create virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the app**
   Open http://localhost:5000 in your browser

### First Time Setup

1. Register a new account at `/auth/register`
2. Contact admin to get admin access
3. Log in with your credentials
4. Start adding players and matches

---

## User Guide

### Dashboard
The main dashboard shows:
- Total players count
- Total matches count
- Top scorers
- Recent match results
- Team statistics overview

### Players
View all players with their:
- Goals
- Assists
- Matches played
- Position
- Detailed stats per season

### Team Analytics
- Win rate calculation
- Goals per match average
- Possession statistics
- Interactive performance charts

### Match Predictions
Input match parameters to predict outcomes:
- Expected possession (%)
- Expected shots
- Shots on target
- Expected corners
- Venue (Home/Away)

The ML model will predict:
- Win/Draw/Loss
- Confidence percentage
- Probability breakdown

---

## Admin Panel

### Access
Admin panel is available at `/admin` for users with admin role.

### Features

#### Player Management
- Add new players
- Edit player details (name, position, jersey number, age, nationality)
- Delete players
- Edit player statistics per season

#### Match Management
- Add match results
- Delete matches
- View match history

#### ML Model Training
- Manual model retraining
- View model accuracy
- Cross-validation scores

---

## ML Predictions

### How It Works

The prediction system uses **Logistic Regression** to predict match outcomes.

#### Features Used
| Feature | Description |
|---------|-------------|
| Possession | Ball possession percentage |
| Shots | Total shots attempted |
| Shots on Target | Shots that hit the goal |
| Corners | Number of corner kicks |
| Venue | Home (1) or Away (0) |

#### Output Classes
- **Win** (class 2)
- **Draw** (class 1)
- **Loss** (class 0)

#### Training Requirements
- Minimum 10 matches required
- More data = better predictions
- Both home and away matches recommended

### Model Performance
- Training accuracy displayed in admin panel
- Cross-validation scores shown
- Model can be retrained anytime

---

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### Get All Players
```
GET /api/players
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "John Smith",
    "position": "Forward",
    "jersey_number": 9,
    "age": 25,
    "nationality": "England",
    "total_goals": 15,
    "total_assists": 8,
    "total_matches": 30
  }
]
```

#### Get Single Player Stats
```
GET /api/player_stats/<player_id>
```

#### Get All Matches
```
GET /api/matches
```

#### Get Team Performance
```
GET /api/team_performance
```

#### Create Player (POST)
```
POST /api/players
Content-Type: application/json

{
  "name": "New Player",
  "position": "Midfielder",
  "jersey_number": 10,
  "age": 22,
  "nationality": "Spain"
}
```

#### Create Match (POST)
```
POST /api/matches
Content-Type: application/json

{
  "match_date": "2024-01-15",
  "opponent": "Team A",
  "venue": "Home",
  "team_goals": 3,
  "opponent_goals": 1,
  "possession": 58.5,
  "shots": 12,
  "shots_on_target": 8,
  "corners": 6,
  "fouls": 10
}
```

---

## Development

### Project Structure
```
sportvision_analytics/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── models/
│   └── __init__.py        # Database models
├── routes/
│   ├── main.py            # Main routes (dashboard, players, team)
│   ├── admin.py           # Admin routes
│   ├── auth.py            # Authentication routes
│   ├── upload.py          # File upload routes
│   ├── predict.py         # ML prediction routes
│   └── api.py             # REST API routes
├── services/
│   ├── prediction.py      # ML prediction service
│   └── csv_processor.py   # CSV processing service
├── utils/
│   └── helpers.py         # Helper functions
├──             templates/ # HTML templates
├── static/               # CSS, images, sample data
├── tests/                 # Unit tests
├── Dockerfile            # Docker configuration
└── requirements.txt      # Python dependencies
```

### Running Tests
```bash
pytest tests/
```

### Adding New Features

1. Create route in appropriate route file
2. Create template in templates/
3. Add navigation link in base.html
4. Add tests in tests/
5. Update documentation

---

## Troubleshooting

### Common Issues

#### "Not enough data to train model"
- Add at least 10 matches
- Upload match data via CSV

#### "Database locked"
- Close any database viewers
- Restart Flask server

#### Charts not displaying
- Check internet connection (Chart.js loads from CDN)
- Check browser console for JavaScript errors

#### Login issues
- Clear browser cookies
- Try incognito/private mode

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests if applicable
5. Push to your fork
6. Create a pull request

---

## License

MIT License

---

## Contact

For questions or support, contact the development team.

---

*Last updated: March 2026*
