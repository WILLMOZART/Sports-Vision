# SportVision Analytics - Project Presentation

---

## 1. PROJECT TITLE

**SportVision Analytics: A Web-Based Sports Performance Analysis System**

---

## 2. INTRODUCTION

Sports analytics has become crucial in modern football for making data-driven decisions. Teams generate vast amounts of data from matches, training sessions, and player performance metrics.

**SportVision Analytics** is a comprehensive web application that addresses the need for centralized sports data management and visualization, providing:

- Player statistics tracking across seasons
- Team performance analytics with interactive visualizations
- Machine learning-powered match outcome predictions
- Role-based access control for team management

---

## 3. PROBLEM STATEMENT

### 3.1 The Problem

Modern sports teams face several challenges:

1. **Fragmented Data** - Player statistics scattered across multiple spreadsheets
2. **Lack of Visualization** - Difficulty in interpreting raw numbers
3. **Manual Analysis** - No automated insights or predictions
4. **Limited Access Control** - No distinction between admin/users
5. **No Predictive Capability** - Unable to forecast match outcomes

### 3.2 Proposed Solution

A centralized web platform that:
- Consolidates all player and team data
- Provides interactive charts and dashboards
- Uses machine learning for predictions
- Offers REST API for external integration

---

## 4. OBJECTIVES

### 4.1 Main Objective
To develop a web-based sports analytics platform that enables efficient data management, visualization, and predictive analysis for sports teams.

### 4.2 Specific Objectives

| # | Objective | How It's Achieved |
|---|-----------|-------------------|
| 1 | User Authentication | Login/Register with password hashing (Werkzeug) |
| 2 | Player Management | CRUD operations via Admin Panel |
| 3 | Match Data Tracking | Store and visualize match statistics |
| 4 | Performance Visualization | Interactive Chart.js charts |
| 5 | Formation Analysis | Dynamic starting XI based on formation selection |
| 6 | ML Predictions | Logistic Regression for match outcomes |
| 7 | REST API | API key-protected endpoints for external access |

---

## 5. LITERATURE REVIEW

### 5.1 Similar Systems

| System | Features | Limitations |
|--------|----------|-------------|
| Wyscout | Video analysis | Expensive, no ML |
| StatsBomb | Event data | No custom predictions |
| Opta | Professional tracking | Proprietary, costly |
| **SportVision** | ML predictions, open-source | Limited to web |

### 5.2 Technologies Used

| Component | Technology | Reason |
|-----------|------------|--------|
| Backend | Python Flask | Lightweight, easy to learn |
| Database | SQLite | No setup required, file-based |
| Frontend | HTML/CSS/JS | Universal web standards |
| Charts | Chart.js | Interactive, lightweight |
| ML | scikit-learn | Python-native, easy integration |
| Auth | Werkzeug | Secure password hashing |

---

## 6. SYSTEM DESIGN

### 6.1 Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│  Flask App  │────▶│   SQLite    │
│  (Client)   │◀────│  (Server)   │◀────│  Database   │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                    ┌─────┴─────┐
                    │  ML Model │
                    │  (sklearn)│
                    └───────────┘
```

### 6.2 Project Structure

```
sportvision_analytics/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── routes/
│   ├── admin.py        # Admin panel routes
│   ├── api.py          # REST API routes
│   ├── auth.py         # Authentication routes
│   └── main.py         # Main pages (dashboard, team, players)
├── services/
│   ├── prediction.py   # ML prediction service
│   └── csv_processor.py # Data import service
├── models/
│   └── __init__.py     # Database class
├── utils/
│   └── helpers.py      # Helper functions
├── templates/           # HTML templates
│   ├── dashboard.html
│   ├── team.html
│   ├── players.html
│   └── admin.html
└── static/
    └── css/style.css   # Stylesheet
```

### 6.3 Database Schema

```
┌─────────────┐     ┌───────────────┐
│   players   │────▶│ player_stats  │
│  (1)────────│◀────│    (Many)     │
└─────────────┘     └───────────────┘
       │
       ▼
┌─────────────┐
│   matches   │
└─────────────┘

┌─────────────┐
│    users    │
│  (Auth)     │
└─────────────┘
```

### 6.4 Key Features Explained

#### Authentication Flow
```
User Login
    │
    ▼
Check credentials (password hash)
    │
    ▼
Create session + Set role (admin/user)
    │
    ▼
@login_required decorator protects routes
@admin_required decorator for admin-only pages
```

#### ML Prediction Model
```
Input Features:
- Match date
- Venue (Home/Away)
- Team goals history
- Possession %
- Shots, Shots on target
- Corners, Fouls

Process:
1. Feature scaling (StandardScaler)
2. Train Logistic Regression
3. Predict: Win / Draw / Loss
4. Return confidence probability

Output:
{
  "prediction": "Win",
  "confidence": 0.78,
  "probabilities": {"Win": 0.78, "Draw": 0.15, "Loss": 0.07}
}
```

---

## 7. IMPLEMENTATION

### 7.1 User Authentication
- **Registration**: Username, email, password (hashed with Werkzeug)
- **Login**: Session-based with role assignment
- **Access Control**: Decorators (@login_required, @admin_required)

### 7.2 Dashboard
- Key Performance Indicators (KPIs)
- Win rate, goals per match, possession stats
- Interactive charts (goals scored vs conceded)
- Recent match form visualization

### 7.3 Team Analytics
- **Formation Selection**: Dropdown to select 4-3-3, 4-4-2, 3-5-2, etc.
- **Starting XI**: Dynamic display based on formation
- **Substitutes**: Bench players with stats
- **Squad Composition**: Position breakdown chart

### 7.4 Player Profiles
- Personal info (name, position, jersey number, age)
- Season-by-season statistics
- Performance charts (goals vs assists)
- Recent match performances

### 7.5 REST API
- Endpoints: /api/players, /api/matches, /api/team_performance
- Authentication: X-API-Key header
- Format: JSON responses

---

## 8. TESTING

### 8.1 Unit Testing (pytest)
- Database operations
- Authentication flows
- API endpoints
- ML model predictions

### 8.2 Manual Testing
| Feature | Test Case | Result |
|---------|-----------|--------|
| Login | Valid credentials | ✅ Success |
| Login | Invalid password | ✅ Rejected |
| Admin | Access admin panel | ✅ Only admin |
| Player | View player details | ✅ Charts load |
| Team | Change formation | ✅ XI updates |
| API | Request without key | ✅ Rejected |

---

## 9. CHALLENGES & SOLUTIONS

| Challenge | Solution |
|-----------|----------|
| Chart.js not loading | Added Chart.js CDN, checked conditional blocks |
| API auth failing | Added X-API-Key header to fetch requests |
| Missing tables | Added db.initialize() to create tables |
| Formation display | JavaScript to dynamically update DOM |

---

## 10. CONCLUSION

SportVision Analytics successfully provides:
- ✅ Centralized data management
- ✅ Interactive visualizations
- ✅ ML-powered predictions
- ✅ Role-based access control
- ✅ REST API for integration

The system demonstrates understanding of:
- Web development (Flask, HTML/CSS/JS)
- Database management (SQLite)
- Machine learning (scikit-learn)
- Security (password hashing, API keys)
- Software engineering (modular architecture)

---

## 11. FUTURE WORK

1. **Real-time Data** - WebSocket integration for live updates
2. **More ML Models** - Random Forest, Neural Networks
3. **Cloud Deployment** - Heroku, AWS, or Azure
4. **Mobile App** - React Native or Flutter
5. **Advanced Analytics** - Player heatmaps, pass maps
6. **Multi-team Support** - Support for league management

---

## 12. REFERENCES

1. Flask Documentation - https://flask.palletsprojects.com/
2. Chart.js Documentation - https://www.chartjs.org/
3. scikit-learn Documentation - https://scikit-learn.org/
4. Werkzeug Security - https://werkzeug.palletsprojects.com/

---

## QUESTIONS?

Prepared for: [University Name]
Student: [Your Name]
Supervisor: [Supervisor Name]
Date: [Defense Date]
