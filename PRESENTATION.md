# Sports-Vision Analytics - Project Presentation

---

## 1. PROJECT TITLE

**Sports-Vision Analytics: A Web-Based Sports Performance Analysis System**

---

## 2. INTRODUCTION

Sports analytics has become crucial in modern football for making data-driven decisions. Teams generate vast amounts of data from matches, training sessions, and player performance metrics.

**Sports-Vision Analytics** is a comprehensive web application that addresses the need for centralized sports data management and visualization, providing:

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
| **Sports-Vision** | ML predictions, open-source | Limited to web |

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
│   └── main.py         # Main pages
├── services/
│   ├── prediction.py   # ML prediction service
│   └── csv_processor.py
├── models/
│   └── __init__.py     # Database class
└── templates/          # HTML templates
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

### 6.4 Key Features Explained (ML)

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

### 6.5 Entity-Relationship Diagram (ERD)

```
┌─────────────────┐       ┌─────────────────┐
│     users       │       │    players      │
├─────────────────┤       ├─────────────────┤
│ pk  id          │       │ pk  id          │
│    username     │       │    name         │
│    email        │       │    position     │
│    password_hash│       │    jersey_num   │
│    role         │       │    age         │
│    created_at   │       │    nationality │
└─────────────────┘       │    created_at  │
         │               └────────┬────────┘
         │                        │
         │                        │ 1:N
         │                        ▼
         │               ┌─────────────────────┐
         │               │    player_stats     │
         │               ├─────────────────────┤
         │               │ pk  id              │
         │               │ fk  player_id       │
         │               │    season           │
         │               │    matches_played  │
         │               │    goals            │
         │               │    assists         │
         │               │    passes_attempted│
         │               │    passes_completed│
         │               │    minutes_played  │
         │               │    rating          │
         │               └─────────┬───────────┘
         │                         │
         │                         │ N:N (via match_performance)
         │                         ▼
         │               ┌─────────────────────┐
         └──────────────▶│      matches       │
                         ├─────────────────────┤
                         │ pk  id              │
                         │    match_date       │
                         │    opponent         │
                         │    venue            │
                         │    team_goals       │
                         │    opponent_goals   │
                         │    possession       │
                         │    shots            │
                         │    shots_on_target  │
                         │    corners          │
                         │    fouls            │
                         │    result           │
                         └─────────┬───────────┘
                                   │
                                   │ 1:N
                                   ▼
                         ┌─────────────────────┐
                         │match_performance   │
                         ├─────────────────────┤
                         │ pk  id              │
                         │ fk  match_id        │
                         │ fk  player_id      │
                         │    goals            │
                         │    assists          │
                         │    minutes_played   │
                         │    rating           │
                         └─────────────────────┘
```

**Relationships:**
- `users` → (1) → can manage system (admin role)
- `players` → (1) → has many `player_stats` (one-to-many)
- `players` → (1) → has many `match_performance` (one-to-many)
- `matches` → (1) → has many `match_performance` (one-to-many)

---

### 6.6 Use Case Diagram

```
                                    ┌──────────────────┐
                                    │  TEAM MANAGER    │
                                    │    (Admin)       │
                                    └────────┬────────┘
                                             │
           ┌────────────────────────────────┼────────────────────────────────┐
           │                                │                                │
           ▼                                ▼                                ▼
┌─────────────────────┐          ┌─────────────────────┐          ┌─────────────────────┐
│   MANAGE PLAYERS    │          │    VIEW DASHBOARD   │          │   MANAGE MATCHES    │
├─────────────────────┤          ├─────────────────────┤          ├─────────────────────┤
│ • Add player        │          │ • View KPIs        │          │ • Add match         │
│ • Edit player       │          │ • View charts      │          │ • Edit match        │
│ • Delete player     │          │ • View form        │          │ • Delete match      │
│ • View all players  │          │ • View stats       │          │ • View matches      │
└─────────┬───────────┘          └─────────┬───────────┘          └─────────┬───────────┘
          │                                │                                │
          │                                │                                │
          ▼                                ▼                                ▼
┌─────────────────────┐          ┌─────────────────────┐          ┌─────────────────────┐
│  MANAGE PLAYER      │          │    VIEW TEAM        │          │  ML PREDICTIONS    │
│  STATISTICS         │          │    ANALYTICS       │          ├─────────────────────┤
├─────────────────────┤          ├─────────────────────┤          │ • Train model      │
│ • Add stats         │          │ • View formation   │          │ • Predict outcome  │
│ • Edit stats        │          │ • Select starting XI│         │ • View confidence  │
│ • View by season    │          │ • View squad       │          └─────────────────────┘
└─────────────────────┘          │ • View scorers     │
                                └─────────────────────┘
                                        │
                                        ▼
┌─────────────────────┐          ┌─────────────────────┐
│   CSV UPLOAD       │          │    REST API        │
├─────────────────────┤          ├─────────────────────┤
│ • Upload players   │          │ • Get players      │
│ • Upload matches   │          │ • Get matches      │
│ • Validate data    │          │ • Get team stats   │
│ • Auto-process     │          │ • API key auth     │
└─────────────────────┘          └─────────────────────┘
```

---

### 6.7 Actor Descriptions

| Actor | Real-World Role | Description |
|-------|-----------------|-------------|
| **Team Manager** | Admin | Full system access - manages team data, players, matches, statistics |
| **Coach** | Regular User | Tactical decisions - views analytics, selects starting XI, makes predictions |
| **External System** | API Consumer | Third-party integration - accesses data via REST API |

### 6.8 Use Case Descriptions

| Use Case | Actor | Description | Steps |
|----------|-------|-------------|-------|
| Login | Coach/Team Manager | Authenticate to access system | 1. Enter credentials → 2. Validate → 3. Create session |
| View Dashboard | Coach | View overall team statistics | 1. Navigate to dashboard → 2. View KPIs & charts |
| Manage Players | Team Manager | CRUD operations on players | 1. Go to admin → 2. Add/Edit/Delete player |
| View Team Analytics | Coach | View formation & tactics | 1. Go to team page → 2. Select formation → 3. View starting XI |
| Select Starting XI | Coach | Choose players for match | 1. Click players in pool → 2. Formation auto-adjusts → 3. View lineup |
| Upload CSV | Team Manager | Bulk import data | 1. Select file → 2. Validate → 3. Import to database |
| ML Prediction | Coach | Predict match outcome | 1. Enter match details → 2. Model predicts → 3. View confidence |
| REST API Access | External System | Programmatic data access | 1. Send API key → 2. Request endpoint → 3. Receive JSON |

---

## 8. IMPLEMENTATION

### 8.1 User Authentication
         │               │    matches_played  │
         │               │    goals            │
         │               │    assists         │
         │               │    passes_attempted│
         │               │    passes_completed│
         │               │    minutes_played  │
         │               │    rating          │
         │               └─────────┬───────────┘
         │                         │
         │                         │ N:N (via match_performance)
         │                         ▼
         │               ┌─────────────────────┐
         └──────────────▶│      matches        │
                         ├─────────────────────┤
                         │ pk  id              │
                         │    match_date       │
                         │    opponent         │
                         │    venue            │
                         │    team_goals       │
                         │    opponent_goals   │
                         │    possession       │
                         │    shots            │
                         │    shots_on_target  │
                         │    corners          │
                         │    fouls            │
                         │    result           │
                         └─────────┬───────────┘
                                   │
                                   │ 1:N
                                   ▼
                         ┌─────────────────────┐
                         │match_performance   │
                         ├─────────────────────┤
                         │ pk  id              │
                         │ fk  match_id        │
                         │ fk  player_id       │
                         │    goals            │
                         │    assists          │
                         │    minutes_played   │
                         │    rating           │
                         └─────────────────────┘
```

**Relationships:**
- `users` → (1) → can manage system (admin role)
- `players` → (1) → has many `player_stats` (one-to-many)
- `players` → (1) → has many `match_performance` (one-to-many)
- `matches` → (1) → has many `match_performance` (one-to-many)
- `player_stats` → (N) → belongs to `players` (many-to-one)

---

### 7.2 Use Case Diagram

```
                                    ┌──────────────────┐
                                    │    ADMIN        │
                                    │    USER         │
                                    └────────┬────────┘
                                             │
           ┌────────────────────────────────┼────────────────────────────────┐
           │                                │                                │
           ▼                                ▼                                ▼
┌─────────────────────┐          ┌─────────────────────┐          ┌─────────────────────┐
│   MANAGE PLAYERS    │          │    VIEW DASHBOARD   │          │   MANAGE MATCHES    │
├─────────────────────┤          ├─────────────────────┤          ├─────────────────────┤
│ • Add player        │          │ • View KPIs        │          │ • Add match         │
│ • Edit player       │          │ • View charts      │          │ • Edit match        │
│ • Delete player     │          │ • View form        │          │ • Delete match      │
│ • View all players  │          │ • View stats       │          │ • View matches      │
└─────────┬───────────┘          └─────────┬───────────┘          └─────────┬───────────┘
          │                                │                                │
          │                                │                                │
          ▼                                ▼                                ▼
┌─────────────────────┐          ┌─────────────────────┐          ┌─────────────────────┐
│  MANAGE PLAYER      │          │    VIEW TEAM        │          │  ML PREDICTIONS    │
│  STATISTICS         │          │    ANALYTICS       │          ├─────────────────────┤
├─────────────────────┤          ├─────────────────────┤          │ • Train model      │
│ • Add stats         │          │ • View formation   │          │ • Predict outcome  │
│ • Edit stats        │          │ • Select starting XI│         │ • View confidence  │
│ • View by season    │          │ • View squad       │          └─────────────────────┘
└─────────────────────┘          │ • View scorers     │
                                └─────────────────────┘
                                        │
                                        ▼
┌─────────────────────┐          ┌─────────────────────┐
│   CSV UPLOAD       │          │    REST API        │
├─────────────────────┤          ├─────────────────────┤
│ • Upload players   │          │ • Get players      │
│ • Upload matches   │          │ • Get matches      │
│ • Validate data    │          │ • Get team stats   │
│ • Auto-process     │          │ • API key auth     │
└─────────────────────┘          └─────────────────────┘
```

---

### 7.3 Use Case Descriptions

| Use Case | Actor | Description | Steps |
|----------|-------|-------------|-------|
| Login | User | Authenticate to access system | 1. Enter credentials → 2. Validate → 3. Create session |
| View Dashboard | User | View overall team statistics | 1. Navigate to dashboard → 2. View KPIs & charts |
| Manage Players | Admin | CRUD operations on players | 1. Go to admin → 2. Add/Edit/Delete player |
| View Team Analytics | User | View formation & tactics | 1. Go to team page → 2. Select formation → 3. View starting XI |
| Select Starting XI | User | Choose players for match | 1. Click players in pool → 2. Formation auto-adjusts → 3. View lineup |
| Upload CSV | Admin | Bulk import data | 1. Select file → 2. Validate → 3. Import to database |
| ML Prediction | User | Predict match outcome | 1. Enter match details → 2. Model predicts → 3. View confidence |
| REST API Access | External | Programmatic data access | 1. Send API key → 2. Request endpoint → 3. Receive JSON |

---

## 8. IMPLEMENTATION

### 8.1 User Authentication
- **Registration**: Username, email, password (hashed with Werkzeug)
- **Login**: Session-based with role assignment
- **Access Control**: Decorators (@login_required, @admin_required)

### 8.2 Dashboard
- Key Performance Indicators (KPIs)
- Win rate, goals per match, possession stats
- Interactive charts (goals scored vs conceded)
- Recent match form visualization

### 8.3 Team Analytics
- **Formation Selection**: Dropdown to select 4-3-3, 4-4-2, 3-5-2, etc.
- **Starting XI**: Dynamic display based on formation
- **Substitutes**: Bench players with stats
- **Squad Composition**: Position breakdown chart

### 8.4 Player Profiles
- Personal info (name, position, jersey number, age)
- Season-by-season statistics
- Performance charts (goals vs assists)
- Recent match performances

### 8.5 REST API
- Endpoints: /api/players, /api/matches, /api/team_performance
- Authentication: X-API-Key header
- Format: JSON responses

---

## 9. TESTING

### 9.1 Unit Testing (pytest)
- Database operations
- Authentication flows
- API endpoints
- ML model predictions

### 9.2 Manual Testing
| Feature | Test Case | Result |
|---------|-----------|--------|
| Login | Valid credentials | ✅ Success |
| Login | Invalid password | ✅ Rejected |
| Admin | Access admin panel | ✅ Only admin |
| Player | View player details | ✅ Charts load |
| Team | Change formation | ✅ XI updates |
| API | Request without key | ✅ Rejected |

---

## 10. CHALLENGES & SOLUTIONS

| Challenge | Solution |
|-----------|----------|
| Chart.js not loading | Added Chart.js CDN, checked conditional blocks |
| API auth failing | Added X-API-Key header to fetch requests |
| Missing tables | Added db.initialize() to create tables |
| Formation display | JavaScript to dynamically update DOM |

---

## 11. CONCLUSION

Sports-Vision Analytics successfully provides:
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

## 13. FUTURE WORK

1. **Real-time Data** - WebSocket integration for live updates
2. **More ML Models** - Random Forest, Neural Networks
3. **Cloud Deployment** - Heroku, AWS, or Azure
4. **Mobile App** - React Native or Flutter
5. **Advanced Analytics** - Player heatmaps, pass maps
6. **Multi-team Support** - Support for league management

---

## 13. REFERENCES

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
