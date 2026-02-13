# AWS SNS Configuration Guide

## Step-by-Step Setup for SNS Notifications

### 1. Create an AWS Account (if you don't have one)

1. Go to https://aws.amazon.com
2. Click "Create an AWS Account"
3. Follow the signup process
4. Enter payment information (free tier available)

### 2. Create an SNS Topic

1. **Login to AWS Console**: https://console.aws.amazon.com
2. **Search for SNS**: In the top search bar, type "SNS" and click on "Simple Notification Service"
3. **Select Region**: In the top-right corner, select your preferred region (e.g., US East 1)
4. **Create Topic**:
   - Click "Topics" in the left sidebar
   - Click "Create topic"
   - Type: Select "Standard"
   - Name: Enter a name like "uptime-monitor-alerts"
   - Display name (optional): "Uptime Alerts"
   - Click "Create topic"
5. **Copy the ARN**: You'll see something like:
   ```
   arn:aws:sns:us-east-1:123456789012:uptime-monitor-alerts
   ```
   Save this ARN - you'll need it for the application settings.

### 3. Create Subscriptions (Email/SMS)

1. **On the Topic page**, click "Create subscription"
2. **For Email Notifications**:
   - Protocol: Select "Email"
   - Endpoint: Enter your email address (e.g., admin@example.com)
   - Click "Create subscription"
   - **Important**: Check your email and confirm the subscription
3. **For SMS Notifications** (optional):
   - Click "Create subscription" again
   - Protocol: Select "SMS"
   - Endpoint: Enter phone number with country code (e.g., +12345678900)
   - Click "Create subscription"

### 4. Create IAM User for Application

**Security Best Practice**: Don't use your root AWS credentials. Create a dedicated IAM user.

1. **Navigate to IAM**:
   - Search for "IAM" in AWS Console
   - Click "Identity and Access Management (IAM)"
2. **Create User**:
   - Click "Users" in left sidebar
   - Click "Add users"
   - User name: "uptime-monitor-app"
   - Access type: Select "Access key - Programmatic access"
   - Click "Next: Permissions"
3. **Attach Permissions**:
   - Click "Attach existing policies directly"
   - Search for "SNS"
   - Select "AmazonSNSFullAccess" (or create custom policy - see below)
   - Click "Next: Tags"
   - Click "Next: Review"
   - Click "Create user"
4. **Save Credentials**:
   - **IMPORTANT**: On the success page, you'll see:
     - Access key ID (e.g., AKIAIOSFODNN7EXAMPLE)
     - Secret access key (e.g., wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY)
   - Click "Download .csv" or copy these values
   - **You can only see the secret key once!**

### 5. Configure Application Settings

1. Open the Uptime Monitor application
2. Login to your account
3. Click "⚙️ Settings" in the sidebar
4. Enter the following:
   - **AWS Access Key ID**: Paste the Access key ID from step 4
   - **AWS Secret Access Key**: Paste the Secret access key from step 4
   - **AWS Region**: Enter the region (e.g., "us-east-1")
   - **SNS Topic ARN**: Paste the ARN from step 2
5. Click "Test SNS Connection" to verify
6. Click "Save Settings"

### 6. Custom IAM Policy (Recommended for Production)

Instead of AmazonSNSFullAccess, use this minimal policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sns:Publish"
            ],
            "Resource": "arn:aws:sns:us-east-1:123456789012:uptime-monitor-alerts"
        }
    ]
}
```

**To create custom policy**:
1. In IAM, click "Policies" → "Create policy"
2. Click "JSON" tab
3. Paste the policy above (replace ARN with your topic ARN)
4. Click "Next: Tags" → "Next: Review"
5. Name: "UptimeMonitorSNSPublish"
6. Click "Create policy"
7. Attach this policy to your IAM user instead of AmazonSNSFullAccess

## Testing

### Test from Application
1. In Settings, click "Test SNS Connection"
2. Check your email/phone for test message

### Test from AWS Console
1. Go to SNS → Topics
2. Click on your topic
3. Click "Publish message"
4. Subject: "Test"
5. Message: "This is a test"
6. Click "Publish message"
7. Check your email/phone

## Troubleshooting

### "Access Denied" Error
- Verify IAM user has SNS permissions
- Check the Topic ARN is correct
- Ensure credentials are entered correctly

### Email Not Received
- Check spam folder
- Verify subscription is confirmed (check AWS Console → SNS → Subscriptions)
- Ensure email address is correct

### SMS Not Received
- Verify phone number format includes country code: +1234567890
- Check AWS SNS SMS spending limit (default is $1/month for new accounts)
- Increase SMS spending limit: SNS → Text messaging (SMS) → Settings

### "Invalid Topic ARN" Error
- ARN format: arn:aws:sns:REGION:ACCOUNT_ID:TOPIC_NAME
- Verify region matches (e.g., us-east-1)
- Check for typos

## Cost Considerations

### Free Tier (First 12 months)
- First 1,000 SNS publishes per month: FREE
- First 100 SNS email deliveries per month: FREE
- First 100 SNS SMS deliveries per month: FREE

### After Free Tier
- SNS Publishes: $0.50 per 1 million requests
- Email: $2 per 100,000 emails
- SMS: Varies by country ($0.00645/message in US)

**For typical uptime monitoring**:
- 10 monitors checking every 60 seconds
- 1 alert per day on average
- Estimated cost: < $1/month

## Best Practices

1. **Use Multiple Subscriptions**: Add both email and SMS for critical alerts
2. **Topic per Environment**: Create separate topics for Production, Staging, etc.
3. **Rotate Credentials**: Change AWS access keys periodically
4. **Monitor AWS Costs**: Enable billing alerts in AWS
5. **Test Regularly**: Use the test button monthly to ensure it works
6. **Backup Credentials**: Store AWS credentials securely (password manager)

## Alternative Notification Methods

If you prefer not to use AWS SNS, you can use webhooks instead:

### Slack Webhook
1. Go to https://api.slack.com/messaging/webhooks
2. Create Incoming Webhook
3. Copy Webhook URL
4. Paste in Settings → Webhook URL

### Discord Webhook
1. Server Settings → Integrations → Webhooks
2. New Webhook
3. Copy Webhook URL
4. Paste in Settings → Webhook URL

### Microsoft Teams Webhook
1. Channel → Connectors → Incoming Webhook
2. Configure
3. Copy URL
4. Paste in Settings → Webhook URL

## Security Checklist

- [ ] Created dedicated IAM user (not using root account)
- [ ] Using minimal IAM permissions (custom policy)
- [ ] AWS credentials stored securely
- [ ] uptime_monitor.db file protected with proper permissions
- [ ] Email subscriptions confirmed
- [ ] Test notifications working
- [ ] Billing alerts enabled in AWS
- [ ] Credentials not shared or committed to version control

---

**Need Help?** AWS has detailed SNS documentation: https://docs.aws.amazon.com/sns/
