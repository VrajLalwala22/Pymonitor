"""
Notification Manager
Handles AWS SNS and Webhook notifications
"""

import boto3
import requests
import logging
from typing import Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, database):
        self.db = database
        self.sns_client = None
        self.sns_topic_arn = None
        self.webhook_url = None
        self.load_settings()
    
    def load_settings(self):
        """Load notification settings from database"""
        # AWS SNS Settings
        aws_access_key = self.db.get_setting('aws_access_key')
        aws_secret_key = self.db.get_setting('aws_secret_key')
        aws_region = self.db.get_setting('aws_region', 'us-east-1')
        self.sns_topic_arn = self.db.get_setting('sns_topic_arn')
        
        if aws_access_key and aws_secret_key:
            try:
                self.sns_client = boto3.client(
                    'sns',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=aws_region
                )
                logger.info("AWS SNS client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize AWS SNS: {e}")
        
        # Webhook Settings
        self.webhook_url = self.db.get_setting('webhook_url')
    
    def update_settings(self, aws_access_key: str = None, aws_secret_key: str = None,
                       aws_region: str = None, sns_topic_arn: str = None,
                       webhook_url: str = None):
        """Update notification settings"""
        if aws_access_key:
            self.db.set_setting('aws_access_key', aws_access_key)
        
        if aws_secret_key:
            self.db.set_setting('aws_secret_key', aws_secret_key)
        
        if aws_region:
            self.db.set_setting('aws_region', aws_region)
        
        if sns_topic_arn:
            self.db.set_setting('sns_topic_arn', sns_topic_arn)
        
        if webhook_url:
            self.db.set_setting('webhook_url', webhook_url)
        
        # Reload settings
        self.load_settings()
    
    def send_notifications(self, monitor_id: int, monitor_name: str, 
                          status: str, message: str):
        """Send all configured notifications"""
        # Send SNS notification
        if self.sns_client and self.sns_topic_arn:
            self._send_sns(monitor_id, monitor_name, status, message)
        
        # Send Webhook notification
        if self.webhook_url:
            self._send_webhook(monitor_id, monitor_name, status, message)
    
    def _send_sns(self, monitor_id: int, monitor_name: str, 
                  status: str, message: str) -> bool:
        """Send AWS SNS notification"""
        try:
            subject = f"🚨 Alert: {monitor_name} is {status}"
            
            body = f"""
Uptime Monitor Alert
====================

Monitor: {monitor_name}
Status: {status}
Message: {message}
Monitor ID: {monitor_id}
Time: {self._get_timestamp()}

This is an automated alert from your Uptime Monitoring system.
"""
            
            response = self.sns_client.publish(
                TopicArn=self.sns_topic_arn,
                Subject=subject,
                Message=body
            )
            
            logger.info(f"SNS notification sent for {monitor_name}: {response['MessageId']}")
            
            self.db.log_notification(
                monitor_id, 'SNS', status, 
                f"MessageId: {response['MessageId']}"
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to send SNS notification: {e}")
            self.db.log_notification(
                monitor_id, 'SNS', 'FAILED', str(e)
            )
            return False
    
    def _send_webhook(self, monitor_id: int, monitor_name: str, 
                     status: str, message: str) -> bool:
        """Send webhook notification"""
        try:
            payload = {
                'monitor_id': monitor_id,
                'monitor_name': monitor_name,
                'status': status,
                'message': message,
                'timestamp': self._get_timestamp()
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            response.raise_for_status()
            
            logger.info(f"Webhook notification sent for {monitor_name}: {response.status_code}")
            
            self.db.log_notification(
                monitor_id, 'WEBHOOK', status,
                f"Status: {response.status_code}"
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            self.db.log_notification(
                monitor_id, 'WEBHOOK', 'FAILED', str(e)
            )
            return False
    
    def test_sns_connection(self) -> tuple:
        """Test AWS SNS connection"""
        if not self.sns_client or not self.sns_topic_arn:
            return False, "SNS not configured"
        
        try:
            response = self.sns_client.publish(
                TopicArn=self.sns_topic_arn,
                Subject="Test Notification from Uptime Monitor",
                Message="This is a test notification. Your SNS integration is working correctly!"
            )
            return True, f"Test message sent! MessageId: {response['MessageId']}"
        
        except Exception as e:
            return False, str(e)
    
    def test_webhook_connection(self) -> tuple:
        """Test webhook connection"""
        if not self.webhook_url:
            return False, "Webhook URL not configured"
        
        try:
            payload = {
                'test': True,
                'message': 'This is a test notification from Uptime Monitor',
                'timestamp': self._get_timestamp()
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            response.raise_for_status()
            return True, f"Test webhook sent! Status: {response.status_code}"
        
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp as string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
