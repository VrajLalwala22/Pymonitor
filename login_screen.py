"""
Login Screen using CustomTkinter
"""

import customtkinter as ctk
from tkinter import messagebox

class LoginScreen:
    def __init__(self, database, on_login_success):
        self.db = database
        self.on_login_success = on_login_success
        self.window = None
    
    def show(self):
        """Display the login window"""
        self.window = ctk.CTk()
        self.window.title("Uptime Monitor - Login")
        self.window.geometry("400x500")
        
        # Center window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Set color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Main container
        container = ctk.CTkFrame(self.window)
        container.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Logo/Title
        title = ctk.CTkLabel(
            container,
            text="🔍 Uptime Monitor",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(20, 10))
        
        subtitle = ctk.CTkLabel(
            container,
            text="Desktop Monitoring Application",
            font=ctk.CTkFont(size=12)
        )
        subtitle.pack(pady=(0, 30))
        
        # Username field
        username_label = ctk.CTkLabel(container, text="Username")
        username_label.pack(pady=(10, 5))
        
        self.username_entry = ctk.CTkEntry(
            container,
            width=300,
            placeholder_text="Enter username"
        )
        self.username_entry.pack(pady=(0, 15))
        
        # Password field
        password_label = ctk.CTkLabel(container, text="Password")
        password_label.pack(pady=(10, 5))
        
        self.password_entry = ctk.CTkEntry(
            container,
            width=300,
            placeholder_text="Enter password",
            show="•"
        )
        self.password_entry.pack(pady=(0, 30))
        
        # Login button
        login_btn = ctk.CTkButton(
            container,
            text="Login",
            width=300,
            height=40,
            command=self.handle_login,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        login_btn.pack(pady=(0, 10))
        
        # Register button
        register_btn = ctk.CTkButton(
            container,
            text="Create Account",
            width=300,
            height=40,
            command=self.show_register,
            fg_color="transparent",
            border_width=2
        )
        register_btn.pack(pady=(0, 20))
        
        # Bind Enter key
        self.window.bind('<Return>', lambda e: self.handle_login())
        
        # Focus username field
        self.username_entry.focus()
        
        self.window.mainloop()
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        if self.db.verify_user(username, password):
            self.window.destroy()
            self.on_login_success(username)
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_entry.delete(0, 'end')
    
    def show_register(self):
        """Show registration dialog"""
        register_window = ctk.CTkToplevel(self.window)
        register_window.title("Create Account")
        register_window.geometry("400x450")
        register_window.transient(self.window)
        register_window.grab_set()
        
        # Center dialog
        register_window.update_idletasks()
        width = register_window.winfo_width()
        height = register_window.winfo_height()
        x = (register_window.winfo_screenwidth() // 2) - (width // 2)
        y = (register_window.winfo_screenheight() // 2) - (height // 2)
        register_window.geometry(f'{width}x{height}+{x}+{y}')
        
        container = ctk.CTkFrame(register_window)
        container.pack(fill="both", expand=True, padx=40, pady=40)
        
        title = ctk.CTkLabel(
            container,
            text="Create New Account",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(10, 30))
        
        # Username
        username_label = ctk.CTkLabel(container, text="Username")
        username_label.pack(pady=(10, 5))
        
        username_entry = ctk.CTkEntry(
            container,
            width=300,
            placeholder_text="Choose a username"
        )
        username_entry.pack(pady=(0, 15))
        
        # Password
        password_label = ctk.CTkLabel(container, text="Password")
        password_label.pack(pady=(10, 5))
        
        password_entry = ctk.CTkEntry(
            container,
            width=300,
            placeholder_text="Choose a password",
            show="•"
        )
        password_entry.pack(pady=(0, 15))
        
        # Confirm Password
        confirm_label = ctk.CTkLabel(container, text="Confirm Password")
        confirm_label.pack(pady=(10, 5))
        
        confirm_entry = ctk.CTkEntry(
            container,
            width=300,
            placeholder_text="Re-enter password",
            show="•"
        )
        confirm_entry.pack(pady=(0, 30))
        
        def handle_register():
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            if len(username) < 3:
                messagebox.showerror("Error", "Username must be at least 3 characters")
                return
            
            if len(password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters")
                return
            
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match")
                return
            
            if self.db.user_exists(username):
                messagebox.showerror("Error", "Username already exists")
                return
            
            if self.db.create_user(username, password):
                messagebox.showinfo("Success", "Account created successfully! You can now login.")
                register_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to create account")
        
        register_btn = ctk.CTkButton(
            container,
            text="Create Account",
            width=300,
            height=40,
            command=handle_register,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        register_btn.pack(pady=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            container,
            text="Cancel",
            width=300,
            height=40,
            command=register_window.destroy,
            fg_color="transparent",
            border_width=2
        )
        cancel_btn.pack()
        
        username_entry.focus()
        register_window.bind('<Return>', lambda e: handle_register())
