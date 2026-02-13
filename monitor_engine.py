"""
Monitoring Engine
Handles background monitoring of HTTP, Keyword, and Heartbeat monitors
"""

import requests
import threading
import time
from datetime import datetime
from typing import Callable, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitorEngine:
    def __init__(self, database, notification_manager):
        self.db = database
        self.notification_manager = notification_manager
        self.monitoring_threads = {}
        self.stop_flags = {}
        self.status_callbacks = []
        self.running = False
    
    def add_status_callback(self, callback: Callable):
        """Add a callback to be notified of status changes"""
        self.status_callbacks.append(callback)
    
    def notify_status_change(self, monitor_id: int, status: str):
        """Notify all callbacks of a status change"""
        for callback in self.status_callbacks:
            try:
                callback(monitor_id, status)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")
    
    def start_all_monitors(self):
        """Start monitoring all enabled monitors"""
        self.running = True
        monitors = self.db.get_all_monitors()
        
        for monitor in monitors:
            if monitor['enabled']:
                self.start_monitor(monitor['id'])
    
    def stop_all_monitors(self):
        """Stop all monitoring threads"""
        self.running = False
        
        for monitor_id in list(self.stop_flags.keys()):
            self.stop_monitor(monitor_id)
        
        # Wait for all threads to finish
        for thread in list(self.monitoring_threads.values()):
            if thread.is_alive():
                thread.join(timeout=5)
    
    def start_monitor(self, monitor_id: int):
        """Start monitoring a specific monitor"""
        if monitor_id in self.monitoring_threads:
            logger.warning(f"Monitor {monitor_id} is already running")
            return
        
        monitor = self.db.get_monitor(monitor_id)
        if not monitor:
            logger.error(f"Monitor {monitor_id} not found")
            return
        
        self.stop_flags[monitor_id] = threading.Event()
        
        thread = threading.Thread(
            target=self._monitor_loop,
            args=(monitor,),
            daemon=True,
            name=f"Monitor-{monitor_id}"
        )
        
        self.monitoring_threads[monitor_id] = thread
        thread.start()
        logger.info(f"Started monitoring: {monitor['name']} (ID: {monitor_id})")
    
    def stop_monitor(self, monitor_id: int):
        """Stop monitoring a specific monitor"""
        if monitor_id in self.stop_flags:
            self.stop_flags[monitor_id].set()
            
            # Wait for thread to finish
            if monitor_id in self.monitoring_threads:
                thread = self.monitoring_threads[monitor_id]
                if thread.is_alive():
                    thread.join(timeout=5)
                
                del self.monitoring_threads[monitor_id]
            
            del self.stop_flags[monitor_id]
            logger.info(f"Stopped monitoring: {monitor_id}")
    
    def _monitor_loop(self, monitor: Dict):
        """Main monitoring loop for a single monitor"""
        monitor_id = monitor['id']
        interval = monitor['interval']
        previous_status = monitor.get('status', 'UNKNOWN')
        
        while not self.stop_flags[monitor_id].is_set() and self.running:
            try:
                # Perform the check based on monitor type
                status, response_time, error_message = self._check_monitor(monitor)
                
                # Update database
                self.db.update_monitor_status(
                    monitor_id, status, response_time, error_message
                )
                
                # Notify UI
                self.notify_status_change(monitor_id, status)
                
                # Check if status changed and send notifications
                if status != previous_status:
                    logger.info(f"Monitor {monitor['name']} status changed: {previous_status} -> {status}")
                    
                    if status == 'DOWN':
                        self.notification_manager.send_notifications(
                            monitor_id,
                            monitor['name'],
                            status,
                            error_message or "Service is down"
                        )
                    
                    previous_status = status
                
            except Exception as e:
                logger.error(f"Error monitoring {monitor['name']}: {e}")
                self.db.update_monitor_status(
                    monitor_id, 'ERROR', None, str(e)
                )
            
            # Wait for next check interval
            self.stop_flags[monitor_id].wait(timeout=interval)
    
    def _check_monitor(self, monitor: Dict) -> tuple:
        """
        Perform the actual monitor check
        Returns: (status, response_time, error_message)
        """
        monitor_type = monitor['type']
        url = monitor['url']
        
        try:
            if monitor_type == 'HTTP':
                return self._check_http(url)
            
            elif monitor_type == 'KEYWORD':
                keyword = monitor.get('keyword', '')
                return self._check_keyword(url, keyword)
            
            elif monitor_type == 'HEARTBEAT':
                return self._check_heartbeat(monitor)
            
            else:
                return 'ERROR', None, f"Unknown monitor type: {monitor_type}"
        
        except Exception as e:
            logger.error(f"Check failed for {monitor['name']}: {e}")
            return 'DOWN', None, str(e)
    
    def _check_http(self, url: str, timeout: int = 10) -> tuple:
        """Check HTTP endpoint for 2xx status code"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if 200 <= response.status_code < 300:
                return 'UP', response_time, None
            else:
                return 'DOWN', response_time, f"HTTP {response.status_code}"
        
        except requests.exceptions.Timeout:
            return 'DOWN', None, "Connection timeout"
        
        except requests.exceptions.ConnectionError as e:
            return 'DOWN', None, f"Connection error: {str(e)[:100]}"
        
        except Exception as e:
            return 'DOWN', None, f"Error: {str(e)[:100]}"
    
    def _check_keyword(self, url: str, keyword: str, timeout: int = 10) -> tuple:
        """Check if keyword exists in page HTML"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code >= 400:
                return 'DOWN', response_time, f"HTTP {response.status_code}"
            
            if keyword and keyword in response.text:
                return 'UP', response_time, None
            elif keyword:
                return 'DOWN', response_time, f"Keyword '{keyword}' not found"
            else:
                return 'DOWN', response_time, "No keyword specified"
        
        except requests.exceptions.Timeout:
            return 'DOWN', None, "Connection timeout"
        
        except requests.exceptions.ConnectionError as e:
            return 'DOWN', None, f"Connection error: {str(e)[:100]}"
        
        except Exception as e:
            return 'DOWN', None, f"Error: {str(e)[:100]}"
    
    def _check_heartbeat(self, monitor: Dict) -> tuple:
        """
        Check heartbeat monitor
        For heartbeat, we check if the last_check is within acceptable range
        This is a simplified implementation - in production, you'd have a listener
        """
        last_check = monitor.get('last_check')
        interval = monitor.get('interval', 60)
        
        if not last_check:
            # First check - assume UP
            return 'UP', 0, None
        
        try:
            last_check_time = datetime.fromisoformat(last_check)
            time_diff = (datetime.now() - last_check_time).total_seconds()
            
            # If no heartbeat received in 2x the interval, consider it DOWN
            if time_diff > (interval * 2):
                return 'DOWN', None, f"No heartbeat for {int(time_diff)}s"
            else:
                return 'UP', 0, None
        
        except Exception as e:
            return 'ERROR', None, str(e)
    
    def manual_check(self, monitor_id: int) -> Dict:
        """Manually trigger a check for a monitor"""
        monitor = self.db.get_monitor(monitor_id)
        if not monitor:
            return {'error': 'Monitor not found'}
        
        status, response_time, error_message = self._check_monitor(monitor)
        
        self.db.update_monitor_status(
            monitor_id, status, response_time, error_message
        )
        
        self.notify_status_change(monitor_id, status)
        
        return {
            'status': status,
            'response_time': response_time,
            'error_message': error_message
        }
