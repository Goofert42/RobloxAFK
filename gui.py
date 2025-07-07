#!/usr/bin/env python3
"""
Modern GUI for Roblox Anti-Leave Script
A simple and clean interface to control the anti-leave functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
import logging
from main import RobloxAntiLeave
import webbrowser
import sys
import os

class ModernGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Roblox Anti-Leave")
        self.root.geometry("600x900")
        self.root.resizable(True, True)
        
        # Modern color scheme
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'accent': '#4a9eff',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'card': '#3c3c3c',
            'input': '#404040'
        }
        
        # Configure root
        self.root.configure(bg=self.colors['bg'])
        
        # Anti-leave instance
        self.anti_leave = None
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # Queue for thread communication
        self.log_queue = queue.Queue()
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.setup_button_effects()
        self.setup_logging()
        
        # Start log processing
        self.process_log_queue()
        
    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()

        # Use a theme that works better with custom colors
        try:
            style.theme_use('clam')
        except:
            pass  # Use default theme if clam not available

        # Configure button style with better contrast
        style.configure('Modern.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=1,
                       relief='flat',
                       focuscolor='none',
                       padding=(15, 8))

        style.map('Modern.TButton',
                 background=[('active', '#3d8bfd'),
                           ('pressed', '#0d6efd'),
                           ('disabled', '#666666')],
                 foreground=[('active', 'white'),
                           ('pressed', 'white'),
                           ('disabled', '#cccccc')])

        # Configure success button with better visibility
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=1,
                       relief='flat',
                       focuscolor='none',
                       padding=(15, 8))

        style.map('Success.TButton',
                 background=[('active', '#45a049'),
                           ('pressed', '#3d8b40'),
                           ('disabled', '#666666')],
                 foreground=[('active', 'white'),
                           ('pressed', 'white'),
                           ('disabled', '#cccccc')])

        # Configure warning button with better visibility
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground='white',
                       borderwidth=1,
                       relief='flat',
                       focuscolor='none',
                       padding=(15, 8))

        style.map('Warning.TButton',
                 background=[('active', '#e68900'),
                           ('pressed', '#cc7a00'),
                           ('disabled', '#666666')],
                 foreground=[('active', 'white'),
                           ('pressed', 'white'),
                           ('disabled', '#cccccc')])

        # Configure entry style with better contrast
        style.configure('Modern.TEntry',
                       fieldbackground=self.colors['input'],
                       foreground='white',
                       borderwidth=2,
                       relief='flat',
                       insertcolor='white',
                       selectbackground=self.colors['accent'],
                       selectforeground='white')

        style.map('Modern.TEntry',
                 fieldbackground=[('focus', '#4a4a4a'),
                                ('!focus', self.colors['input'])],
                 bordercolor=[('focus', self.colors['accent']),
                            ('!focus', '#666666')])
        
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Main container with better spacing
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="Roblox Anti-Leave",
                              font=('Segoe UI', 24, 'bold'),
                              fg=self.colors['fg'],
                              bg=self.colors['bg'])
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(main_frame,
                                 text="Automatically reconnect to private servers",
                                 font=('Segoe UI', 12),
                                 fg='#888888',
                                 bg=self.colors['bg'])
        subtitle_label.pack(pady=(0, 30))
        
        # URL Input Section with beveled corners
        url_frame = tk.Frame(main_frame, bg=self.colors['card'], relief='raised', bd=2)
        url_frame.pack(fill='x', pady=(0, 25), padx=5)
        
        # Internal container for proper padding
        url_inner = tk.Frame(url_frame, bg=self.colors['card'])
        url_inner.pack(fill='both', expand=True, padx=20, pady=18)

        url_title = tk.Label(url_inner,
                            text="Private Server URL",
                            font=('Segoe UI', 14, 'bold'),
                            fg=self.colors['fg'],
                            bg=self.colors['card'])
        url_title.pack(anchor='w', pady=(0, 8))

        url_desc = tk.Label(url_inner,
                           text="Format: https://www.roblox.com/share?code=CODE&type=Server",
                           font=('Segoe UI', 10),
                           fg='#888888',
                           bg=self.colors['card'])
        url_desc.pack(anchor='w', pady=(0, 15))
        
        # Use regular tkinter Entry for better compatibility
        self.url_entry = tk.Entry(url_inner,
                                 bg=self.colors['input'],
                                 fg='white',
                                 font=('Segoe UI', 11),
                                 relief='sunken',
                                 bd=2,
                                 insertbackground='white',
                                 selectbackground=self.colors['accent'],
                                 selectforeground='white')
        self.url_entry.pack(fill='x', pady=(0, 18), ipady=8)

        # Buttons frame with better spacing
        button_frame = tk.Frame(url_inner, bg=self.colors['card'])
        button_frame.pack(fill='x')
        
        # Use custom styled tkinter buttons for better visibility
        self.start_button = tk.Button(button_frame,
                                     text="Start Monitoring",
                                     bg=self.colors['success'],
                                     fg='white',
                                     font=('Segoe UI', 10, 'bold'),
                                     relief='raised',
                                     bd=2,
                                     padx=20,
                                     pady=8,
                                     cursor='hand2',
                                     command=self.start_monitoring)
        self.start_button.pack(side='left', padx=(0, 15))

        self.stop_button = tk.Button(button_frame,
                                    text="Stop Monitoring",
                                    bg=self.colors['warning'],
                                    fg='white',
                                    font=('Segoe UI', 10, 'bold'),
                                    relief='raised',
                                    bd=2,
                                    padx=20,
                                    pady=8,
                                    cursor='hand2',
                                    state='disabled',
                                    command=self.stop_monitoring)
        self.stop_button.pack(side='left', padx=(0, 15))

        validate_button = tk.Button(button_frame,
                                   text="Validate URL",
                                   bg=self.colors['accent'],
                                   fg='white',
                                   font=('Segoe UI', 10, 'bold'),
                                   relief='raised',
                                   bd=2,
                                   padx=20,
                                   pady=8,
                                   cursor='hand2',
                                   command=self.validate_url)
        validate_button.pack(side='left')
        
        # Status Section with beveled corners
        status_frame = tk.Frame(main_frame, bg=self.colors['card'], relief='raised', bd=2)
        status_frame.pack(fill='x', pady=(0, 25), padx=5)

        # Internal container for proper padding
        status_inner = tk.Frame(status_frame, bg=self.colors['card'])
        status_inner.pack(fill='both', expand=True, padx=20, pady=18)

        status_title = tk.Label(status_inner,
                               text="Status",
                               font=('Segoe UI', 14, 'bold'),
                               fg=self.colors['fg'],
                               bg=self.colors['card'])
        status_title.pack(anchor='w', pady=(0, 8))

        self.status_label = tk.Label(status_inner,
                                    text="Ready to start monitoring",
                                    font=('Segoe UI', 11),
                                    fg=self.colors['success'],
                                    bg=self.colors['card'])
        self.status_label.pack(anchor='w')
        
        # Log Section with beveled corners
        log_frame = tk.Frame(main_frame, bg=self.colors['card'], relief='raised', bd=2)
        log_frame.pack(fill='both', expand=True, padx=5)

        # Internal container for proper padding
        log_inner = tk.Frame(log_frame, bg=self.colors['card'])
        log_inner.pack(fill='both', expand=True, padx=20, pady=18)

        log_title = tk.Label(log_inner,
                            text="Activity Log",
                            font=('Segoe UI', 14, 'bold'),
                            fg=self.colors['fg'],
                            bg=self.colors['card'])
        log_title.pack(anchor='w', pady=(0, 12))

        # Log text area with beveled border
        self.log_text = scrolledtext.ScrolledText(log_inner,
                                                 height=8,
                                                 bg=self.colors['input'],
                                                 fg=self.colors['fg'],
                                                 font=('Consolas', 10),
                                                 wrap=tk.WORD,
                                                 state='disabled',
                                                 relief='sunken',
                                                 bd=2)
        self.log_text.pack(fill='both', expand=True)
        
        # Footer with better spacing
        footer_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        footer_frame.pack(fill='x', pady=(20, 0))
        
        help_button = tk.Button(footer_frame,
                               text="Help",
                               bg=self.colors['accent'],
                               fg='white',
                               font=('Segoe UI', 10),
                               relief='raised',
                               bd=2,
                               padx=15,
                               pady=5,
                               cursor='hand2',
                               command=self.show_help)
        help_button.pack(side='left')

        about_button = tk.Button(footer_frame,
                                text="About",
                                bg=self.colors['accent'],
                                fg='white',
                                font=('Segoe UI', 10),
                                relief='raised',
                                bd=2,
                                padx=15,
                                pady=5,
                                cursor='hand2',
                                command=self.show_about)
        about_button.pack(side='left', padx=(15, 0))

        # Store button references for effects
        self.buttons = [self.start_button, self.stop_button, validate_button, help_button, about_button]

    def setup_button_effects(self):
        """Add hover effects to buttons"""
        def on_enter(event, button, hover_color):
            if button['state'] != 'disabled':
                button.config(bg=hover_color)

        def on_leave(event, button, normal_color):
            if button['state'] != 'disabled':
                button.config(bg=normal_color)

        # Add hover effects after buttons are created
        self.root.after(100, self.apply_hover_effects)

    def apply_hover_effects(self):
        """Apply hover effects to all buttons"""
        try:
            # Start button hover
            self.start_button.bind("<Enter>", lambda e: self.start_button.config(bg='#45a049') if self.start_button['state'] != 'disabled' else None)
            self.start_button.bind("<Leave>", lambda e: self.start_button.config(bg=self.colors['success']) if self.start_button['state'] != 'disabled' else None)

            # Stop button hover
            self.stop_button.bind("<Enter>", lambda e: self.stop_button.config(bg='#e68900') if self.stop_button['state'] != 'disabled' else None)
            self.stop_button.bind("<Leave>", lambda e: self.stop_button.config(bg=self.colors['warning']) if self.stop_button['state'] != 'disabled' else None)
        except:
            pass  # Ignore if buttons don't exist yet

    def setup_logging(self):
        """Setup logging to capture messages in GUI"""
        # Create custom handler that sends logs to queue
        class QueueHandler(logging.Handler):
            def __init__(self, log_queue):
                super().__init__()
                self.log_queue = log_queue
                
            def emit(self, record):
                self.log_queue.put(self.format(record))
        
        # Configure logging
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            
        # Add queue handler
        queue_handler = QueueHandler(self.log_queue)
        queue_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(queue_handler)
        
    def process_log_queue(self):
        """Process log messages from queue and display in GUI"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.add_log_message(message)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_log_queue)
        
    def add_log_message(self, message):
        """Add message to log display"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
    def validate_url(self):
        """Validate the entered URL"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a private server URL")
            return
            
        # Create temporary instance to validate
        temp_anti_leave = RobloxAntiLeave()
        if temp_anti_leave.is_valid_roblox_url(url):
            messagebox.showinfo("Success", "✓ Valid private server URL!")
            self.add_log_message(f"URL validated: {url}")
        else:
            messagebox.showerror("Error", 
                               "Invalid URL format!\n\n" +
                               "Required format:\n" +
                               "https://www.roblox.com/share?code=CODE&type=Server")
            
    def start_monitoring(self):
        """Start the anti-leave monitoring"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a private server URL")
            return
            
        # Validate URL
        temp_anti_leave = RobloxAntiLeave()
        if not temp_anti_leave.is_valid_roblox_url(url):
            messagebox.showerror("Error", "Invalid private server URL format!")
            return
            
        # Start monitoring in separate thread
        self.is_monitoring = True
        self.anti_leave = RobloxAntiLeave()
        
        def monitor():
            try:
                self.anti_leave.start_monitoring(url)
            except Exception as e:
                self.log_queue.put(f"ERROR - Monitoring failed: {e}")
                self.is_monitoring = False
                
        self.monitoring_thread = threading.Thread(target=monitor, daemon=True)
        self.monitoring_thread.start()
        
        # Update UI
        self.start_button.config(state='disabled', bg='#666666')
        self.stop_button.config(state='normal', bg=self.colors['warning'])
        self.url_entry.config(state='disabled', bg='#666666')
        self.status_label.config(text="Monitoring active", fg=self.colors['success'])
        
        self.add_log_message("Monitoring started successfully")
        
    def stop_monitoring(self):
        """Stop the anti-leave monitoring"""
        if self.anti_leave:
            self.anti_leave.stop_monitoring()
            
        self.is_monitoring = False
        
        # Update UI
        self.start_button.config(state='normal', bg=self.colors['success'])
        self.stop_button.config(state='disabled', bg='#666666')
        self.url_entry.config(state='normal', bg=self.colors['input'])
        self.status_label.config(text="Monitoring stopped", fg=self.colors['warning'])
        
        self.add_log_message("Monitoring stopped")
        
    def show_help(self):
        """Show help information"""
        help_text = """
Roblox Anti-Leave Help

How to use:
1. Copy a private server URL from Roblox
2. Paste it in the URL field
3. Click 'Start Monitoring'
4. The program will automatically reconnect if you get disconnected

URL Format:
https://www.roblox.com/share?code=CODE&type=Server

Features:
• Detects when Roblox closes or crashes
• Detects AFK kick popups
• Automatically opens private server URL
• Desktop notifications
• Activity logging

Tips:
• Keep this window open while playing
• Check the activity log for status updates
• Use 'Validate URL' to test your URL before starting
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("500x400")
        help_window.configure(bg=self.colors['bg'])
        
        text_widget = scrolledtext.ScrolledText(help_window,
                                               bg=self.colors['input'],
                                               fg=self.colors['fg'],
                                               font=('Segoe UI', 11),
                                               wrap=tk.WORD)
        text_widget.pack(fill='both', expand=True, padx=20, pady=20)
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
        
    def show_about(self):
        """Show about information"""
        messagebox.showinfo("About", 
                           "Roblox Anti-Leave v2.0\n\n" +
                           "Automatically reconnects to Roblox private servers\n" +
                           "when you get disconnected or kicked for AFK.\n\n" +
                           "Created for private server reconnection")
        
    def on_closing(self):
        """Handle window closing"""
        if self.is_monitoring:
            if messagebox.askokcancel("Quit", "Monitoring is active. Stop monitoring and quit?"):
                self.stop_monitoring()
                self.root.destroy()
        else:
            self.root.destroy()
            
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Main function to start GUI"""
    try:
        app = ModernGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
