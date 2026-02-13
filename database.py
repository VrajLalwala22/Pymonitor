"""
Database module for Uptime Monitor
Handles all SQLite operations for users, monitors, and status logs
"""

import sqlite3
import bcrypt
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import threading

class Database:
    def __init__(self, db_path: str = "uptime_monitor.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()
    
    def get_connection(self):
        """Create a new database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database schema"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Monitors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    url TEXT NOT NULL,
                    keyword TEXT,
                    interval INTEGER DEFAULT 60,
                    status TEXT DEFAULT 'UNKNOWN',
                    last_check TIMESTAMP,
                    response_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    enabled INTEGER DEFAULT 1
                )
            """)
            
            # Status logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS status_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    monitor_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    response_time REAL,
                    error_message TEXT,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (monitor_id) REFERENCES monitors(id) ON DELETE CASCADE
                )
            """)
            
            # Notifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    monitor_id INTEGER NOT NULL,
                    notification_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (monitor_id) REFERENCES monitors(id) ON DELETE CASCADE
                )
            """)
            
            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            conn.commit()
            conn.close()
    
    # User Management
    def create_user(self, username: str, password: str) -> bool:
        """Create a new user with hashed password"""
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            with self.lock:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                conn.commit()
                conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()
        
        if result:
            stored_hash = result['password_hash']
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
        return False
    
    def user_exists(self, username: str) -> bool:
        """Check if a user exists"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()
        return result['count'] > 0
    
    # Monitor Management
    def add_monitor(self, name: str, monitor_type: str, url: str, 
                    keyword: str = None, interval: int = 60) -> int:
        """Add a new monitor"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO monitors (name, type, url, keyword, interval, status)
                VALUES (?, ?, ?, ?, ?, 'UNKNOWN')
            """, (name, monitor_type, url, keyword, interval))
            monitor_id = cursor.lastrowid
            conn.commit()
            conn.close()
        return monitor_id
    
    def get_all_monitors(self) -> List[Dict]:
        """Get all monitors"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM monitors ORDER BY created_at DESC
            """)
            monitors = [dict(row) for row in cursor.fetchall()]
            conn.close()
        return monitors
    
    def get_monitor(self, monitor_id: int) -> Optional[Dict]:
        """Get a specific monitor"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM monitors WHERE id = ?", (monitor_id,))
            result = cursor.fetchone()
            conn.close()
        return dict(result) if result else None
    
    def update_monitor_status(self, monitor_id: int, status: str, 
                             response_time: float = None, error_message: str = None):
        """Update monitor status and log it"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Update monitor
            cursor.execute("""
                UPDATE monitors 
                SET status = ?, last_check = ?, response_time = ?
                WHERE id = ?
            """, (status, datetime.now(), response_time, monitor_id))
            
            # Log status
            cursor.execute("""
                INSERT INTO status_logs (monitor_id, status, response_time, error_message)
                VALUES (?, ?, ?, ?)
            """, (monitor_id, status, response_time, error_message))
            
            conn.commit()
            conn.close()
    
    def delete_monitor(self, monitor_id: int):
        """Delete a monitor"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM monitors WHERE id = ?", (monitor_id,))
            conn.commit()
            conn.close()
    
    def toggle_monitor(self, monitor_id: int, enabled: bool):
        """Enable or disable a monitor"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE monitors SET enabled = ? WHERE id = ?", 
                         (1 if enabled else 0, monitor_id))
            conn.commit()
            conn.close()
    
    # Status Logs
    def get_monitor_logs(self, monitor_id: int, limit: int = 100) -> List[Dict]:
        """Get recent logs for a monitor"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM status_logs 
                WHERE monitor_id = ?
                ORDER BY checked_at DESC
                LIMIT ?
            """, (monitor_id, limit))
            logs = [dict(row) for row in cursor.fetchall()]
            conn.close()
        return logs
    
    def get_uptime_percentage(self, monitor_id: int, hours: int = 24) -> float:
        """Calculate uptime percentage for a monitor"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'UP' THEN 1 ELSE 0 END) as up_count
                FROM status_logs
                WHERE monitor_id = ?
                AND checked_at >= datetime('now', '-' || ? || ' hours')
            """, (monitor_id, hours))
            result = cursor.fetchone()
            conn.close()
        
        if result and result['total'] > 0:
            return (result['up_count'] / result['total']) * 100
        return 0.0
    
    # Notifications
    def log_notification(self, monitor_id: int, notification_type: str, 
                        status: str, message: str):
        """Log a sent notification"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notifications (monitor_id, notification_type, status, message)
                VALUES (?, ?, ?, ?)
            """, (monitor_id, notification_type, status, message))
            conn.commit()
            conn.close()
    
    # Settings
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """Get a setting value"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            result = cursor.fetchone()
            conn.close()
        return result['value'] if result else default
    
    def set_setting(self, key: str, value: str):
        """Set a setting value"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
            """, (key, value))
            conn.commit()
            conn.close()
