"""
Main Dashboard using CustomTkinter
Shows monitor cards with real-time status updates
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from datetime import datetime

class Dashboard:
    def __init__(self, database, monitor_engine, notification_manager, username):
        self.db = database
        self.monitor_engine = monitor_engine
        self.notification_manager = notification_manager
        self.username = username
        self.window = None
        self.monitor_cards = {}
        self.current_view = "monitors"
    
    def show(self):
        """Display the main dashboard"""
        self.window = ctk.CTk()
        self.window.title("Uptime Monitor Dashboard")
        self.window.geometry("1200x800")
        
        # Set color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure grid
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Show monitors view by default
        self.show_monitors_view()
        
        # Register status callback
        self.monitor_engine.add_status_callback(self.on_status_change)
        
        # Start monitoring
        threading.Thread(target=self.monitor_engine.start_all_monitors, daemon=True).start()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.window.mainloop()
    
    def create_sidebar(self):
        """Create the navigation sidebar"""
        sidebar = ctk.CTkFrame(self.window, width=200)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(20, 0), pady=20)
        sidebar.grid_propagate(False)
        
        # Logo/Title
        title = ctk.CTkLabel(
            sidebar,
            text="🔍 Uptime\nMonitor",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(30, 5))
        
        # User info
        user_label = ctk.CTkLabel(
            sidebar,
            text=f"👤 {self.username}",
            font=ctk.CTkFont(size=12)
        )
        user_label.pack(pady=(0, 30))
        
        # Navigation buttons
        monitors_btn = ctk.CTkButton(
            sidebar,
            text="📊 Monitors",
            command=self.show_monitors_view,
            height=40
        )
        monitors_btn.pack(pady=5, padx=20, fill="x")
        
        add_btn = ctk.CTkButton(
            sidebar,
            text="➕ Add Monitor",
            command=self.show_add_monitor_dialog,
            height=40
        )
        add_btn.pack(pady=5, padx=20, fill="x")
        
        status_btn = ctk.CTkButton(
            sidebar,
            text="📈 Status Page",
            command=self.show_status_page,
            height=40
        )
        status_btn.pack(pady=5, padx=20, fill="x")
        
        settings_btn = ctk.CTkButton(
            sidebar,
            text="⚙️ Settings",
            command=self.show_settings,
            height=40
        )
        settings_btn.pack(pady=5, padx=20, fill="x")
        
        # Spacer
        ctk.CTkLabel(sidebar, text="").pack(expand=True)
        
        # Logout button
        logout_btn = ctk.CTkButton(
            sidebar,
            text="🚪 Logout",
            command=self.logout,
            height=40,
            fg_color="transparent",
            border_width=2
        )
        logout_btn.pack(pady=(5, 20), padx=20, fill="x")
    
    def clear_main_frame(self):
        """Clear the main content area"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_monitors_view(self):
        """Show the main monitors view with cards"""
        self.current_view = "monitors"
        self.clear_main_frame()
        
        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Monitors",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            command=self.refresh_monitors,
            width=100
        )
        refresh_btn.pack(side="right", padx=5)
        
        # Scrollable frame for monitor cards
        self.cards_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.cards_frame.pack(fill="both", expand=True)
        
        # Load and display monitors
        self.refresh_monitors()
    
    def refresh_monitors(self):
        """Refresh the monitor cards"""
        # Clear existing cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        self.monitor_cards.clear()
        
        monitors = self.db.get_all_monitors()
        
        if not monitors:
            no_monitors = ctk.CTkLabel(
                self.cards_frame,
                text="No monitors configured.\nClick 'Add Monitor' to get started!",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            no_monitors.pack(pady=100)
            return
        
        # Create cards in a grid
        row = 0
        col = 0
        max_cols = 2
        
        for monitor in monitors:
            card = self.create_monitor_card(monitor)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            self.monitor_cards[monitor['id']] = card
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configure grid columns
        for i in range(max_cols):
            self.cards_frame.grid_columnconfigure(i, weight=1)
    
    def create_monitor_card(self, monitor):
        """Create a monitor status card"""
        status = monitor['status']
        
        # Determine color based on status
        if status == 'UP':
            bg_color = "#1a5f1a"
            status_color = "#4ade80"
            status_emoji = "✅"
        elif status == 'DOWN':
            bg_color = "#5f1a1a"
            status_color = "#ef4444"
            status_emoji = "❌"
        else:
            bg_color = "#3f3f46"
            status_color = "#a1a1aa"
            status_emoji = "❔"
        
        # Card frame
        card = ctk.CTkFrame(self.cards_frame, fg_color=bg_color, corner_radius=10)
        
        # Header with name and status
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))
        
        name_label = ctk.CTkLabel(
            header,
            text=f"{monitor['name']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)
        
        status_label = ctk.CTkLabel(
            header,
            text=f"{status_emoji} {status}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=status_color
        )
        status_label.pack(side="right")
        
        # Info section
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=5)
        
        type_label = ctk.CTkLabel(
            info_frame,
            text=f"Type: {monitor['type']}",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        type_label.pack(anchor="w")
        
        url_label = ctk.CTkLabel(
            info_frame,
            text=f"URL: {monitor['url'][:50]}{'...' if len(monitor['url']) > 50 else ''}",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        url_label.pack(anchor="w")
        
        if monitor.get('response_time'):
            response_label = ctk.CTkLabel(
                info_frame,
                text=f"Response: {monitor['response_time']:.0f}ms",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            )
            response_label.pack(anchor="w")
        
        if monitor.get('last_check'):
            try:
                last_check = datetime.fromisoformat(monitor['last_check'])
                last_check_str = last_check.strftime("%Y-%m-%d %H:%M:%S")
            except:
                last_check_str = monitor['last_check']
            
            check_label = ctk.CTkLabel(
                info_frame,
                text=f"Last Check: {last_check_str}",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            )
            check_label.pack(anchor="w")
        
        # Uptime percentage
        uptime = self.db.get_uptime_percentage(monitor['id'], hours=24)
        uptime_label = ctk.CTkLabel(
            info_frame,
            text=f"24h Uptime: {uptime:.1f}%",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        uptime_label.pack(anchor="w")
        
        # Button frame
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(10, 15))
        
        check_btn = ctk.CTkButton(
            btn_frame,
            text="Check Now",
            command=lambda m=monitor: self.manual_check(m['id']),
            width=80,
            height=28,
            font=ctk.CTkFont(size=11)
        )
        check_btn.pack(side="left", padx=(0, 5))
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            command=lambda m=monitor: self.delete_monitor(m['id'], m['name']),
            width=80,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#dc2626",
            hover_color="#b91c1c"
        )
        delete_btn.pack(side="right")
        
        return card
    
    def on_status_change(self, monitor_id, status):
        """Callback for when a monitor status changes"""
        # Refresh the monitor card in the UI thread
        if self.current_view == "monitors":
            self.window.after(0, self.refresh_monitors)
    
    def manual_check(self, monitor_id):
        """Manually trigger a check for a monitor"""
        def do_check():
            result = self.monitor_engine.manual_check(monitor_id)
            self.window.after(0, lambda: messagebox.showinfo(
                "Check Complete",
                f"Status: {result.get('status')}\n"
                f"Response Time: {result.get('response_time', 'N/A')}\n"
                f"Message: {result.get('error_message') or 'OK'}"
            ))
        
        threading.Thread(target=do_check, daemon=True).start()
    
    def delete_monitor(self, monitor_id, monitor_name):
        """Delete a monitor"""
        if messagebox.askyesno("Confirm Delete", f"Delete monitor '{monitor_name}'?"):
            self.monitor_engine.stop_monitor(monitor_id)
            self.db.delete_monitor(monitor_id)
            self.refresh_monitors()
            messagebox.showinfo("Success", "Monitor deleted successfully")
    
    def show_add_monitor_dialog(self):
        """Show dialog to add a new monitor"""
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Add New Monitor")
        dialog.geometry("500x600")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250)
        y = (dialog.winfo_screenheight() // 2) - (300)
        dialog.geometry(f'500x600+{x}+{y}')
        
        container = ctk.CTkFrame(dialog)
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        title = ctk.CTkLabel(
            container,
            text="Add New Monitor",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # Monitor Name
        name_label = ctk.CTkLabel(container, text="Monitor Name")
        name_label.pack(pady=(10, 5), anchor="w")
        
        name_entry = ctk.CTkEntry(container, width=400, placeholder_text="My Website")
        name_entry.pack(pady=(0, 15))
        
        # Monitor Type
        type_label = ctk.CTkLabel(container, text="Monitor Type")
        type_label.pack(pady=(10, 5), anchor="w")
        
        type_var = ctk.StringVar(value="HTTP")
        type_menu = ctk.CTkOptionMenu(
            container,
            values=["HTTP", "KEYWORD", "HEARTBEAT"],
            variable=type_var,
            width=400
        )
        type_menu.pack(pady=(0, 15))
        
        # URL
        url_label = ctk.CTkLabel(container, text="URL")
        url_label.pack(pady=(10, 5), anchor="w")
        
        url_entry = ctk.CTkEntry(
            container,
            width=400,
            placeholder_text="https://example.com"
        )
        url_entry.pack(pady=(0, 15))
        
        # Keyword (only for KEYWORD type)
        keyword_label = ctk.CTkLabel(container, text="Keyword (for KEYWORD type)")
        keyword_label.pack(pady=(10, 5), anchor="w")
        
        keyword_entry = ctk.CTkEntry(
            container,
            width=400,
            placeholder_text="Text to search for"
        )
        keyword_entry.pack(pady=(0, 15))
        
        # Check Interval
        interval_label = ctk.CTkLabel(container, text="Check Interval (seconds)")
        interval_label.pack(pady=(10, 5), anchor="w")
        
        interval_entry = ctk.CTkEntry(container, width=400, placeholder_text="60")
        interval_entry.insert(0, "60")
        interval_entry.pack(pady=(0, 20))
        
        def add_monitor():
            name = name_entry.get().strip()
            monitor_type = type_var.get()
            url = url_entry.get().strip()
            keyword = keyword_entry.get().strip()
            
            try:
                interval = int(interval_entry.get())
            except:
                messagebox.showerror("Error", "Invalid interval value")
                return
            
            if not name or not url:
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            if interval < 10:
                messagebox.showerror("Error", "Interval must be at least 10 seconds")
                return
            
            # Add to database
            monitor_id = self.db.add_monitor(name, monitor_type, url, keyword, interval)
            
            # Start monitoring
            self.monitor_engine.start_monitor(monitor_id)
            
            messagebox.showinfo("Success", "Monitor added successfully!")
            dialog.destroy()
            self.refresh_monitors()
        
        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(pady=(20, 0))
        
        add_btn = ctk.CTkButton(
            btn_frame,
            text="Add Monitor",
            command=add_monitor,
            width=180,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=180,
            height=40,
            fg_color="transparent",
            border_width=2
        )
        cancel_btn.pack(side="left", padx=5)
    
    def show_status_page(self):
        """Show the status summary page"""
        self.current_view = "status"
        self.clear_main_frame()
        
        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Status Page",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Overall statistics
        monitors = self.db.get_all_monitors()
        total_monitors = len(monitors)
        up_count = sum(1 for m in monitors if m['status'] == 'UP')
        down_count = sum(1 for m in monitors if m['status'] == 'DOWN')
        
        stats_frame = ctk.CTkFrame(self.main_frame)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        stat1 = self.create_stat_box(stats_frame, "Total Monitors", str(total_monitors), "#3b82f6")
        stat1.pack(side="left", padx=10, pady=10, expand=True, fill="both")
        
        stat2 = self.create_stat_box(stats_frame, "Online", str(up_count), "#22c55e")
        stat2.pack(side="left", padx=10, pady=10, expand=True, fill="both")
        
        stat3 = self.create_stat_box(stats_frame, "Offline", str(down_count), "#ef4444")
        stat3.pack(side="left", padx=10, pady=10, expand=True, fill="both")
        
        # Monitor list
        list_frame = ctk.CTkScrollableFrame(self.main_frame)
        list_frame.pack(fill="both", expand=True)
        
        for monitor in monitors:
            self.create_status_row(list_frame, monitor).pack(fill="x", pady=5, padx=10)
    
    def create_stat_box(self, parent, label, value, color):
        """Create a statistics box"""
        box = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        
        value_label = ctk.CTkLabel(
            box,
            text=value,
            font=ctk.CTkFont(size=32, weight="bold")
        )
        value_label.pack(pady=(20, 5))
        
        label_label = ctk.CTkLabel(
            box,
            text=label,
            font=ctk.CTkFont(size=14)
        )
        label_label.pack(pady=(0, 20))
        
        return box
    
    def create_status_row(self, parent, monitor):
        """Create a status row for the status page"""
        status = monitor['status']
        
        if status == 'UP':
            color = "#22c55e"
            emoji = "✅"
        elif status == 'DOWN':
            color = "#ef4444"
            emoji = "❌"
        else:
            color = "#a1a1aa"
            emoji = "❔"
        
        row = ctk.CTkFrame(parent, corner_radius=8)
        
        # Status indicator
        status_label = ctk.CTkLabel(
            row,
            text=f"{emoji} {status}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color,
            width=80
        )
        status_label.pack(side="left", padx=15, pady=15)
        
        # Monitor info
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=(0, 15), pady=15)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=monitor['name'],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        url_label = ctk.CTkLabel(
            info_frame,
            text=monitor['url'],
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        url_label.pack(anchor="w")
        
        # Uptime
        uptime = self.db.get_uptime_percentage(monitor['id'], hours=24)
        uptime_label = ctk.CTkLabel(
            row,
            text=f"{uptime:.1f}%",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=80
        )
        uptime_label.pack(side="right", padx=15, pady=15)
        
        return row
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Settings")
        dialog.geometry("600x700")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (300)
        y = (dialog.winfo_screenheight() // 2) - (350)
        dialog.geometry(f'600x700+{x}+{y}')
        
        container = ctk.CTkScrollableFrame(dialog)
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        title = ctk.CTkLabel(
            container,
            text="⚙️ Notification Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # AWS SNS Section
        sns_label = ctk.CTkLabel(
            container,
            text="AWS SNS Configuration",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        sns_label.pack(pady=(10, 10), anchor="w")
        
        # AWS Access Key
        aws_key_label = ctk.CTkLabel(container, text="AWS Access Key ID")
        aws_key_label.pack(pady=(10, 5), anchor="w")
        
        aws_key_entry = ctk.CTkEntry(container, width=500)
        current_key = self.db.get_setting('aws_access_key', '')
        aws_key_entry.insert(0, current_key)
        aws_key_entry.pack(pady=(0, 15))
        
        # AWS Secret Key
        aws_secret_label = ctk.CTkLabel(container, text="AWS Secret Access Key")
        aws_secret_label.pack(pady=(10, 5), anchor="w")
        
        aws_secret_entry = ctk.CTkEntry(container, width=500, show="•")
        current_secret = self.db.get_setting('aws_secret_key', '')
        aws_secret_entry.insert(0, current_secret)
        aws_secret_entry.pack(pady=(0, 15))
        
        # AWS Region
        aws_region_label = ctk.CTkLabel(container, text="AWS Region")
        aws_region_label.pack(pady=(10, 5), anchor="w")
        
        aws_region_entry = ctk.CTkEntry(container, width=500)
        current_region = self.db.get_setting('aws_region', 'us-east-1')
        aws_region_entry.insert(0, current_region)
        aws_region_entry.pack(pady=(0, 15))
        
        # SNS Topic ARN
        sns_topic_label = ctk.CTkLabel(container, text="SNS Topic ARN")
        sns_topic_label.pack(pady=(10, 5), anchor="w")
        
        sns_topic_entry = ctk.CTkEntry(container, width=500)
        current_topic = self.db.get_setting('sns_topic_arn', '')
        sns_topic_entry.insert(0, current_topic)
        sns_topic_entry.pack(pady=(0, 15))
        
        # Test SNS button
        test_sns_btn = ctk.CTkButton(
            container,
            text="Test SNS Connection",
            command=lambda: self.test_notification('sns'),
            width=200
        )
        test_sns_btn.pack(pady=(0, 20))
        
        # Webhook Section
        webhook_label = ctk.CTkLabel(
            container,
            text="Webhook Configuration",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        webhook_label.pack(pady=(20, 10), anchor="w")
        
        # Webhook URL
        webhook_url_label = ctk.CTkLabel(container, text="Webhook URL")
        webhook_url_label.pack(pady=(10, 5), anchor="w")
        
        webhook_url_entry = ctk.CTkEntry(container, width=500)
        current_webhook = self.db.get_setting('webhook_url', '')
        webhook_url_entry.insert(0, current_webhook)
        webhook_url_entry.pack(pady=(0, 15))
        
        # Test Webhook button
        test_webhook_btn = ctk.CTkButton(
            container,
            text="Test Webhook",
            command=lambda: self.test_notification('webhook'),
            width=200
        )
        test_webhook_btn.pack(pady=(0, 20))
        
        def save_settings():
            self.notification_manager.update_settings(
                aws_access_key=aws_key_entry.get().strip() or None,
                aws_secret_key=aws_secret_entry.get().strip() or None,
                aws_region=aws_region_entry.get().strip() or None,
                sns_topic_arn=sns_topic_entry.get().strip() or None,
                webhook_url=webhook_url_entry.get().strip() or None
            )
            messagebox.showinfo("Success", "Settings saved successfully!")
            dialog.destroy()
        
        # Save button
        save_btn = ctk.CTkButton(
            container,
            text="Save Settings",
            command=save_settings,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.pack(pady=(20, 0))
    
    def test_notification(self, notification_type):
        """Test notification configuration"""
        def do_test():
            if notification_type == 'sns':
                success, message = self.notification_manager.test_sns_connection()
            else:
                success, message = self.notification_manager.test_webhook_connection()
            
            if success:
                self.window.after(0, lambda: messagebox.showinfo("Test Successful", message))
            else:
                self.window.after(0, lambda: messagebox.showerror("Test Failed", message))
        
        threading.Thread(target=do_test, daemon=True).start()
    
    def logout(self):
        """Logout and return to login screen"""
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            self.on_closing()
    
    def on_closing(self):
        """Handle window closing"""
        self.monitor_engine.stop_all_monitors()
        self.window.quit()
        self.window.destroy()
