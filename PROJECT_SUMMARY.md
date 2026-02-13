# Uptime Monitor - Complete Project Package

## 📦 Package Contents

This package contains a fully-functional desktop Uptime Monitoring application built with Python and CustomTkinter.

### Core Application Files (6 files)
1. **main.py** - Application entry point
2. **database.py** - SQLite database operations and schema management
3. **monitor_engine.py** - Background monitoring engine with threading
4. **notifications.py** - AWS SNS and Webhook notification system
5. **login_screen.py** - Secure login and registration UI
6. **dashboard.py** - Main dashboard with real-time monitor cards

### Configuration & Dependencies
7. **requirements.txt** - Python package dependencies
8. **start.bat** - Windows batch file for easy startup

### Documentation (4 files)
9. **README.md** - Complete documentation and setup guide
10. **QUICKSTART.md** - 5-minute quick start guide
11. **AWS_SNS_SETUP.md** - Detailed AWS SNS configuration guide
12. **database_schema.sql** - Database schema reference

## 🚀 Quick Installation

### Option 1: Using Batch File (Easiest)
```bash
# 1. Install Python 3.11+ from python.org
# 2. Extract all files to a folder
# 3. Open Command Prompt in that folder
# 4. Run:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 5. Double-click start.bat to launch!
```

### Option 2: Command Line
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## 📁 File Organization

```
uptime-monitor/
│
├── Core Application
│   ├── main.py                 # Entry point - starts login screen
│   ├── database.py            # Database layer (SQLite)
│   ├── monitor_engine.py      # Monitoring logic with threading
│   ├── notifications.py       # SNS + Webhook notifications
│   ├── login_screen.py        # Login/Register UI
│   └── dashboard.py           # Main dashboard UI
│
├── Configuration
│   ├── requirements.txt       # Python dependencies
│   └── start.bat             # Windows launcher
│
├── Documentation
│   ├── README.md             # Complete guide
│   ├── QUICKSTART.md         # 5-minute setup
│   ├── AWS_SNS_SETUP.md      # AWS configuration
│   └── database_schema.sql   # Database reference
│
└── Generated (auto-created)
    └── uptime_monitor.db     # SQLite database file
```

## 🎯 Features Overview

### ✅ Implemented Features

**Login System**
- Secure bcrypt password hashing
- SQLite user storage
- Account creation/registration
- Session management

**Monitor Types**
- HTTP: Status code checking (2xx = UP)
- KEYWORD: Content verification (search for text)
- HEARTBEAT: Service ping monitoring

**Dashboard**
- Real-time status cards (Green/Red)
- Auto-refresh on status changes
- Response time tracking
- 24-hour uptime percentage
- Manual check trigger
- Monitor management (add/delete)

**Notifications**
- AWS SNS integration (email/SMS)
- Webhook support (Slack, Discord, Teams)
- Test connection buttons
- Notification logging

**Status Page**
- Overall statistics
- Monitor list with uptime
- Quick overview of all services

**Data Persistence**
- SQLite database
- Monitor configurations
- Status history
- User accounts
- Settings storage

## 🔧 Technical Architecture

### Threading Model
```
Main Thread (GUI)
    └── CustomTkinter Event Loop
        
Background Threads
    ├── Monitor Thread 1 (HTTP checks)
    ├── Monitor Thread 2 (Keyword checks)
    ├── Monitor Thread 3 (Heartbeat checks)
    └── ... (one thread per monitor)
```

### Database Schema
```
users (id, username, password_hash, created_at)
monitors (id, name, type, url, keyword, interval, status, ...)
status_logs (id, monitor_id, status, response_time, error_message, ...)
notifications (id, monitor_id, notification_type, status, message, ...)
settings (key, value)
```

### Module Dependencies
```
main.py
    ├── database.py
    ├── monitor_engine.py
    │       ├── database.py
    │       └── notifications.py
    │               └── database.py
    ├── login_screen.py
    │       └── database.py
    └── dashboard.py
            ├── database.py
            ├── monitor_engine.py
            └── notifications.py
```

## 📊 Python Packages Used

```
customtkinter==5.2.1  # Modern dark-mode UI framework
bcrypt==4.1.2         # Password hashing
requests==2.31.0      # HTTP requests for monitoring
boto3==1.34.34        # AWS SDK for SNS
Pillow==10.2.0        # Image support for CustomTkinter
```

## 🔐 Security Features

1. **Password Security**
   - bcrypt hashing (cost factor 12)
   - Salted passwords
   - No plain-text storage

2. **Data Protection**
   - Local SQLite database (no external server)
   - Database file permissions
   - Secure credential storage

3. **No Admin Rights Required**
   - User-space installation
   - Portable deployment
   - Virtual environment isolation

## 💡 Usage Examples

### Monitor Your Website
```python
Monitor Settings:
  Name: My Company Website
  Type: HTTP
  URL: https://www.mycompany.com
  Interval: 60 seconds
```

### Verify API Response
```python
Monitor Settings:
  Name: API Health Check
  Type: KEYWORD
  URL: https://api.myservice.com/health
  Keyword: "status":"healthy"
  Interval: 120 seconds
```

### Monitor Third-Party Service
```python
Monitor Settings:
  Name: AWS Status
  Type: HTTP
  URL: https://status.aws.amazon.com
  Interval: 300 seconds
```

## 🔔 Notification Examples

### AWS SNS Email Alert
```
Subject: 🚨 Alert: My Website is DOWN

Uptime Monitor Alert
====================

Monitor: My Website
Status: DOWN
Message: HTTP 503
Monitor ID: 1
Time: 2024-01-15 14:30:22

This is an automated alert from your Uptime Monitoring system.
```

### Webhook Payload (Slack/Discord)
```json
{
  "monitor_id": 1,
  "monitor_name": "My Website",
  "status": "DOWN",
  "message": "HTTP 503",
  "timestamp": "2024-01-15 14:30:22"
}
```

## 🎨 UI Components

**Login Screen**
- Modern dark theme
- Username/password fields
- Create account dialog
- Input validation

**Dashboard**
- Sidebar navigation
- Monitor cards (grid layout)
- Status indicators (emoji + color)
- Action buttons
- Scrollable content

**Status Page**
- Statistics boxes
- Monitor list
- Uptime percentages
- Color-coded status

**Settings Dialog**
- AWS SNS configuration
- Webhook configuration
- Test buttons
- Save functionality

## 🚦 Status States

```
UP (Green)      - Service is responding correctly
DOWN (Red)      - Service is not responding or error
UNKNOWN (Gray)  - Not checked yet
ERROR (Gray)    - Check failed due to error
```

## 📈 Performance Considerations

**Optimizations**
- Threaded monitoring (non-blocking)
- Database connection pooling
- Efficient card updates
- Minimal UI refreshes

**Scalability**
- Tested with up to 50 monitors
- Recommended: 10-20 monitors for best performance
- Configurable check intervals
- Database cleanup (30-day retention)

## 🔄 Workflow

1. **Startup**
   - Initialize database
   - Show login screen
   - Authenticate user

2. **Login Success**
   - Load monitors from database
   - Start monitoring threads
   - Display dashboard

3. **Monitoring Loop** (per monitor)
   - Wait for interval
   - Perform check (HTTP/Keyword/Heartbeat)
   - Update database
   - Notify UI
   - Send alerts if DOWN
   - Repeat

4. **Shutdown**
   - Stop all monitoring threads
   - Close database connections
   - Save state

## 🐛 Common Issues & Solutions

### Monitor always shows DOWN
- Check URL includes protocol (https://)
- Verify site is accessible in browser
- Check for rate limiting (increase interval)

### UI freezes
- Ensure monitoring threads are running
- Check database isn't locked
- Restart application

### Notifications not working
- Test connection in Settings
- Verify AWS credentials
- Check webhook URL is correct

## 📝 Future Enhancement Ideas

**Potential Additions** (not currently implemented):
- Multi-user support with permissions
- Historical graphs and charts
- Mobile app companion
- Custom notification templates
- Monitor groups/categories
- Maintenance windows
- Response time alerts
- SSL certificate monitoring
- Port monitoring (TCP/UDP)
- Ping monitoring (ICMP)
- DNS monitoring
- Export reports (PDF/CSV)

## 🎓 Learning Resources

**Python Threading**
- https://docs.python.org/3/library/threading.html

**CustomTkinter**
- https://customtkinter.tomschimansky.com/

**AWS SNS**
- https://docs.aws.amazon.com/sns/

**SQLite**
- https://www.sqlite.org/docs.html

## 📄 License

This code is provided as-is for educational and monitoring purposes.

## 🙏 Credits

**Technologies Used:**
- Python 3.11+
- CustomTkinter (UI)
- SQLite (Database)
- AWS Boto3 (SNS)
- bcrypt (Security)
- requests (HTTP)

---

## 📞 Support

For questions or issues:
1. Check QUICKSTART.md for common setup issues
2. Review README.md troubleshooting section
3. Verify all dependencies installed correctly
4. Check terminal output for error messages

## ✅ Pre-Deployment Checklist

Before using in production:
- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Database created (auto on first run)
- [ ] Test account created
- [ ] Sample monitor added and working
- [ ] Notifications configured and tested
- [ ] Database backup plan in place
- [ ] Documentation reviewed

---

**Built for SRE teams who need reliable, self-hosted uptime monitoring! 🔍**
