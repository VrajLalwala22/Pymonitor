-- Uptime Monitor Database Schema
-- This file is for reference only - the database is created automatically by the application
-- SQLite database: uptime_monitor.db

-- Users table - stores user credentials with bcrypt hashed passwords
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Monitors table - stores monitor configurations
CREATE TABLE IF NOT EXISTS monitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                    -- Display name of the monitor
    type TEXT NOT NULL,                     -- HTTP, KEYWORD, HEARTBEAT
    url TEXT NOT NULL,                      -- URL to monitor
    keyword TEXT,                           -- Keyword to search for (KEYWORD type only)
    interval INTEGER DEFAULT 60,            -- Check interval in seconds
    status TEXT DEFAULT 'UNKNOWN',          -- Current status: UP, DOWN, UNKNOWN, ERROR
    last_check TIMESTAMP,                   -- Last check timestamp
    response_time REAL,                     -- Response time in milliseconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    enabled INTEGER DEFAULT 1               -- 1 = enabled, 0 = disabled
);

-- Status logs table - historical monitoring data
CREATE TABLE IF NOT EXISTS status_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_id INTEGER NOT NULL,           -- Reference to monitors table
    status TEXT NOT NULL,                   -- Status at check time
    response_time REAL,                     -- Response time in milliseconds
    error_message TEXT,                     -- Error details if status is DOWN/ERROR
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (monitor_id) REFERENCES monitors(id) ON DELETE CASCADE
);

-- Notifications table - log of sent notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_id INTEGER NOT NULL,           -- Reference to monitors table
    notification_type TEXT NOT NULL,        -- SNS, WEBHOOK
    status TEXT NOT NULL,                   -- Status that triggered notification
    message TEXT,                           -- Notification message/response
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (monitor_id) REFERENCES monitors(id) ON DELETE CASCADE
);

-- Settings table - application configuration (key-value pairs)
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,                   -- Setting name
    value TEXT NOT NULL                     -- Setting value
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_monitors_status ON monitors(status);
CREATE INDEX IF NOT EXISTS idx_monitors_enabled ON monitors(enabled);
CREATE INDEX IF NOT EXISTS idx_status_logs_monitor ON status_logs(monitor_id, checked_at);
CREATE INDEX IF NOT EXISTS idx_notifications_monitor ON notifications(monitor_id, sent_at);

-- Sample data (for testing - commented out)
/*
-- Create a test user (password: "admin123")
INSERT INTO users (username, password_hash) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYbSJVcBJj6');

-- Create sample monitors
INSERT INTO monitors (name, type, url, interval) VALUES
('Google', 'HTTP', 'https://www.google.com', 60),
('GitHub Status', 'KEYWORD', 'https://www.githubstatus.com', 120, 'All Systems Operational'),
('My API', 'HTTP', 'https://api.example.com/health', 300);

-- Sample settings
INSERT INTO settings (key, value) VALUES
('aws_region', 'us-east-1'),
('webhook_url', 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL');
*/

-- Views for reporting (optional)

-- View: Monitor summary with latest status
CREATE VIEW IF NOT EXISTS monitor_summary AS
SELECT 
    m.id,
    m.name,
    m.type,
    m.url,
    m.status,
    m.last_check,
    m.response_time,
    m.enabled,
    COUNT(sl.id) as total_checks,
    SUM(CASE WHEN sl.status = 'UP' THEN 1 ELSE 0 END) as up_checks,
    ROUND(100.0 * SUM(CASE WHEN sl.status = 'UP' THEN 1 ELSE 0 END) / COUNT(sl.id), 2) as uptime_percent
FROM monitors m
LEFT JOIN status_logs sl ON m.id = sl.monitor_id
    AND sl.checked_at >= datetime('now', '-24 hours')
GROUP BY m.id;

-- View: Recent status changes
CREATE VIEW IF NOT EXISTS recent_status_changes AS
SELECT 
    m.name as monitor_name,
    sl.status,
    sl.response_time,
    sl.error_message,
    sl.checked_at
FROM status_logs sl
JOIN monitors m ON sl.monitor_id = m.id
ORDER BY sl.checked_at DESC
LIMIT 100;

-- View: Notification history
CREATE VIEW IF NOT EXISTS notification_history AS
SELECT 
    m.name as monitor_name,
    n.notification_type,
    n.status,
    n.message,
    n.sent_at
FROM notifications n
JOIN monitors m ON n.monitor_id = m.id
ORDER BY n.sent_at DESC;

-- Useful queries for monitoring

-- Get uptime percentage for all monitors (last 24 hours)
/*
SELECT 
    m.name,
    m.status as current_status,
    COUNT(sl.id) as total_checks,
    SUM(CASE WHEN sl.status = 'UP' THEN 1 ELSE 0 END) as successful_checks,
    ROUND(100.0 * SUM(CASE WHEN sl.status = 'UP' THEN 1 ELSE 0 END) / COUNT(sl.id), 2) as uptime_percent
FROM monitors m
LEFT JOIN status_logs sl ON m.id = sl.monitor_id
    AND sl.checked_at >= datetime('now', '-24 hours')
WHERE m.enabled = 1
GROUP BY m.id, m.name, m.status
ORDER BY uptime_percent ASC;
*/

-- Find monitors that are currently down
/*
SELECT name, url, last_check, status
FROM monitors
WHERE status = 'DOWN' AND enabled = 1;
*/

-- Get average response time per monitor
/*
SELECT 
    m.name,
    AVG(sl.response_time) as avg_response_time,
    MIN(sl.response_time) as min_response_time,
    MAX(sl.response_time) as max_response_time
FROM monitors m
JOIN status_logs sl ON m.id = sl.monitor_id
WHERE sl.checked_at >= datetime('now', '-24 hours')
    AND sl.response_time IS NOT NULL
GROUP BY m.id, m.name
ORDER BY avg_response_time DESC;
*/

-- Clean up old status logs (keep last 30 days)
/*
DELETE FROM status_logs
WHERE checked_at < datetime('now', '-30 days');
*/
