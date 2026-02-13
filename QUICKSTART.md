# Quick Start Guide - Uptime Monitor

## Installation in 5 Minutes

### Prerequisites
- Windows computer
- Internet connection
- No admin rights required

### Step 1: Install Python (2 minutes)
1. Download Python 3.11+ from https://www.python.org/downloads/
2. Run installer
3. ✅ Check "Add Python to PATH"
4. ✅ Select "Install for current user only"
5. Click Install

### Step 2: Setup Application (2 minutes)
```bash
# Open Command Prompt (Win + R, type "cmd", press Enter)

# Navigate to the application folder
cd C:\Users\YourUsername\Desktop\uptime-monitor

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run Application (1 minute)
```bash
python main.py
```

That's it! The application will open.

## First Time Use

### Create Account
1. Click "Create Account"
2. Username: your_name (min 3 chars)
3. Password: your_password (min 6 chars)
4. Click "Create Account"
5. Login with your credentials

### Add Your First Monitor
1. Click "➕ Add Monitor"
2. Fill in:
   - Name: "Google"
   - Type: HTTP
   - URL: https://www.google.com
   - Interval: 60
3. Click "Add Monitor"

You'll immediately see a green card showing Google is UP!

## Monitor Types Quick Reference

### HTTP - Basic Uptime Check
```
Use when: You want to check if a website is online
Example: Monitor your company website
Settings:
  - Name: My Website
  - Type: HTTP
  - URL: https://mysite.com
  - Interval: 60 (checks every minute)
```

### KEYWORD - Content Verification
```
Use when: You need to verify specific content appears
Example: Check if login page shows "Sign In"
Settings:
  - Name: Login Page Check
  - Type: KEYWORD
  - URL: https://mysite.com/login
  - Keyword: Sign In
  - Interval: 120
```

### HEARTBEAT - Service Ping
```
Use when: Your service sends regular pings
Example: Monitor a background job
Settings:
  - Name: Data Sync Job
  - Type: HEARTBEAT
  - URL: https://myservice.com/heartbeat
  - Interval: 300
Note: Simplified - checks if last update was recent
```

## Notification Setup (Optional)

### Quick Webhook Test (Discord/Slack)

**Slack:**
```
1. Go to: https://api.slack.com/messaging/webhooks
2. Create webhook → Copy URL
3. In app: Settings → Webhook URL → Paste → Save
4. Click "Test Webhook" - you should get a message!
```

**Discord:**
```
1. Server Settings → Integrations → Webhooks → New
2. Copy Webhook URL
3. In app: Settings → Webhook URL → Paste → Save
4. Click "Test Webhook" - you should get a message!
```

### AWS SNS (Email/SMS Alerts)

See `AWS_SNS_SETUP.md` for detailed guide, but quick version:

1. Create AWS account: https://aws.amazon.com
2. Go to SNS → Create Topic → Copy ARN
3. Create Subscription → Email → Confirm
4. IAM → Create User → Get Access Keys
5. In app: Settings → Enter AWS details → Test → Save

## Common Tasks

### Check Monitor Manually
Click "Check Now" button on any monitor card

### Delete Monitor
Click "Delete" button on monitor card

### View Uptime Stats
Click "📈 Status Page" - shows 24h uptime percentages

### Change Settings
Click "⚙️ Settings" to configure notifications

## Troubleshooting

### Monitor shows DOWN but site is UP
- Check URL is correct (include https://)
- Try in browser first
- Increase interval to reduce rate limiting

### Application won't start
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Try again
python main.py
```

### Lost password
The database stores hashed passwords. If you forget your password:
```bash
# Delete database (WARNING: Loses all data)
del uptime_monitor.db

# Restart app and create new account
python main.py
```

## Tips for Best Results

1. **Start Simple**: Begin with 2-3 monitors
2. **Use Longer Intervals**: 60-300 seconds prevents rate limiting
3. **Test Notifications**: Always test before relying on alerts
4. **Monitor Critical Only**: Don't overload - focus on important services
5. **Check Status Page**: Review uptime trends regularly

## Example Monitor Configurations

### Monitor Your Website
```
Name: Company Website
Type: HTTP
URL: https://mycompany.com
Interval: 60
```

### Monitor API Endpoint
```
Name: API Health
Type: KEYWORD
URL: https://api.myservice.com/health
Keyword: "status":"ok"
Interval: 120
```

### Monitor Database Status Page
```
Name: Database Status
Type: KEYWORD
URL: https://status.mongodb.com
Keyword: All Systems Operational
Interval: 300
```

### Monitor Third-Party Service
```
Name: AWS Status
Type: HTTP
URL: https://status.aws.amazon.com
Interval: 300
```

## Running on Startup (Optional)

### Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Uptime Monitor"
4. Trigger: At log on
5. Action: Start a program
6. Program: `C:\Users\YourName\Desktop\uptime-monitor\venv\Scripts\python.exe`
7. Arguments: `main.py`
8. Start in: `C:\Users\YourName\Desktop\uptime-monitor`
9. Finish

Now it starts automatically when you login!

## Database Backup

Your data is in `uptime_monitor.db`. Back it up regularly:

```bash
# Copy database
copy uptime_monitor.db uptime_monitor_backup.db

# Or use Windows Explorer to copy the file
```

Restore by replacing the file and restarting the app.

## Next Steps

- Read full `README.md` for detailed information
- Set up AWS SNS following `AWS_SNS_SETUP.md`
- Customize monitor intervals based on your needs
- Add all critical services you want to monitor
- Set up notifications so you know when issues occur

## Support

For issues:
1. Check terminal output for error messages
2. Verify Python and dependencies installed correctly
3. Review README.md Troubleshooting section
4. Ensure internet connection is working

---

**Happy Monitoring! 🔍**
