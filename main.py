"""
Main Application Entry Point
Uptime Monitor Desktop Application
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database
from monitor_engine import MonitorEngine
from notifications import NotificationManager
from login_screen import LoginScreen
from dashboard import Dashboard

def main():
    """Main application entry point"""
    # Initialize database
    db = Database()
    
    # Initialize notification manager
    notification_manager = NotificationManager(db)
    
    # Initialize monitor engine
    monitor_engine = MonitorEngine(db, notification_manager)
    
    # Define login success callback
    def on_login_success(username):
        """Called when user successfully logs in"""
        # Show dashboard
        dashboard = Dashboard(db, monitor_engine, notification_manager, username)
        dashboard.show()
    
    # Show login screen
    login = LoginScreen(db, on_login_success)
    login.show()

if __name__ == "__main__":
    main()
