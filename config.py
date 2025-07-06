"""
Configuration file for Roblox Anti-Leave Script
Modify these settings to customize the behavior of the script.
"""

# Monitoring settings
CHECK_INTERVAL = 5  # seconds between disconnection checks
MAX_RECONNECT_ATTEMPTS = 3  # maximum number of reconnection attempts
RECONNECT_DELAY = 10  # seconds to wait after a reconnection attempt

# Detection settings
DISCONNECT_INDICATORS = [
    "disconnected",
    "connection lost", 
    "unable to connect",
    "kicked",
    "error",
    "reconnect",
    "lost connection",
    "connection failed",
    "network error",
    "timeout"
]

# Roblox window patterns to look for
ROBLOX_PATTERNS = [
    r"Roblox",
    r".*- Roblox", 
    r"Roblox Player",
    r"RobloxPlayerBeta"
]

# Roblox process names to monitor
ROBLOX_PROCESS_NAMES = [
    "robloxplayerbeta.exe",
    "roblox.exe",
    "robloxplayer.exe"
]

# Notification settings
ENABLE_NOTIFICATIONS = True
NOTIFICATION_TIMEOUT = 10  # seconds

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "roblox_antileave.log"
ENABLE_CONSOLE_LOGGING = True

# Browser settings
BROWSER_WAIT_TIME = 3  # seconds to wait for browser to open

# Advanced settings
ENABLE_CLIPBOARD_DETECTION = True  # try to get game URL from clipboard
ENABLE_PROCESS_MONITORING = True  # monitor Roblox processes
ENABLE_WINDOW_MONITORING = True   # monitor Roblox windows
