#!/usr/bin/env python3
"""
SportVision Analytics - Quick Start Script
==========================================
Run this script to start the application.
"""

import os
import sys

# Check if running in the correct directory
if not os.path.exists('app.py'):
    print("Error: Please run this script from the sportvision_analytics directory")
    sys.exit(1)

# Import and run the app
from app import app, init_database, DATABASE

# Initialize database if it doesn't exist
if not os.path.exists(DATABASE):
    print("Initializing database...")
    init_database()
    print("Database initialized!")

print("\n" + "="*50)
print("SportVision Analytics")
print("="*50)
print("Starting server on http://localhost:5000")
print("Press CTRL+C to stop")
print("="*50 + "\n")

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
