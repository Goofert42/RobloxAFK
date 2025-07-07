#!/usr/bin/env python3
"""
Roblox Anti-Leave Script
Automatically detects when you've been disconnected from a Roblox game
and attempts to reconnect you.
"""

import time
import logging
import subprocess
import webbrowser
from typing import List, Optional
import re
import sys

# Import configuration
try:
    from config import *
except ImportError:
    print("Warning: config.py not found, using default settings")
    # Default settings if config.py is missing
    CHECK_INTERVAL = 5
    MAX_RECONNECT_ATTEMPTS = 3
    RECONNECT_DELAY = 10
    DISCONNECTION_COOLDOWN = 30
    DISCONNECT_INDICATORS = ["disconnected", "connection lost", "unable to connect", "kicked", "error", "reconnect", "lost connection"]
    ROBLOX_PATTERNS = [r"Roblox", r".*- Roblox", r"Roblox Player"]
    ROBLOX_PROCESS_NAMES = ["robloxplayerbeta.exe", "roblox.exe", "robloxplayer.exe"]
    ENABLE_NOTIFICATIONS = True
    NOTIFICATION_TIMEOUT = 10
    LOG_LEVEL = "INFO"
    LOG_FILE = "roblox_antileave.log"
    ENABLE_CONSOLE_LOGGING = True
    BROWSER_WAIT_TIME = 3
    PLAY_BUTTON_IMAGE = "play_button.png"
    PLAY_BUTTON_CONFIDENCE = 0.8
    ENABLE_CLIPBOARD_DETECTION = True
    ENABLE_PROCESS_MONITORING = True
    ENABLE_WINDOW_MONITORING = True

try:
    import pygetwindow as gw
    import psutil
    from plyer import notification
    if ENABLE_CLIPBOARD_DETECTION:
        import pyperclip
except ImportError as e:
    print(f"Missing required library: {e}")
    print("Please install required packages:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
log_handlers = []
if ENABLE_CONSOLE_LOGGING:
    log_handlers.append(logging.StreamHandler())
log_handlers.append(logging.FileHandler(LOG_FILE))

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)
logger = logging.getLogger(__name__)

class RobloxAntiLeave:
    def __init__(self):
        self.last_game_url = None
        self.monitoring = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = MAX_RECONNECT_ATTEMPTS
        self.check_interval = CHECK_INTERVAL
        self.reconnect_delay = RECONNECT_DELAY

        # Use configuration settings
        self.disconnect_indicators = DISCONNECT_INDICATORS
        self.roblox_patterns = ROBLOX_PATTERNS
        self.roblox_process_names = ROBLOX_PROCESS_NAMES

        # State tracking to prevent spam detection
        self.last_disconnection_time = 0
        self.disconnection_cooldown = DISCONNECTION_COOLDOWN
        self.was_connected = False
        self.consecutive_disconnects = 0

    def get_roblox_windows(self) -> List:
        """Get all Roblox-related windows"""
        roblox_windows = []
        try:
            all_windows = gw.getAllWindows()
            for window in all_windows:
                if window.title and any(re.search(pattern, window.title, re.IGNORECASE)
                                      for pattern in self.roblox_patterns):
                    roblox_windows.append(window)
        except Exception as e:
            logger.error(f"Error getting Roblox windows: {e}")
        return roblox_windows

    def is_roblox_running(self) -> bool:
        """Check if Roblox process is running"""
        if not ENABLE_PROCESS_MONITORING:
            return True  # Skip process monitoring if disabled

        try:
            for proc in psutil.process_iter(['pid', 'name']):
                proc_name = proc.info['name'].lower()
                if any(roblox_name.lower() in proc_name for roblox_name in self.roblox_process_names):
                    return True
        except Exception as e:
            logger.error(f"Error checking Roblox process: {e}")
        return False

    def detect_disconnection(self) -> bool:
        """Detect if user has been disconnected from Roblox"""
        try:
            import time
            current_time = time.time()

            # Cooldown period to prevent spam detection
            if current_time - self.last_disconnection_time < self.disconnection_cooldown:
                return False

            # Check if Roblox is running first
            roblox_running = True
            if ENABLE_PROCESS_MONITORING:
                roblox_running = self.is_roblox_running()

            # Check for Roblox windows
            roblox_windows = []
            if ENABLE_WINDOW_MONITORING:
                roblox_windows = self.get_roblox_windows()

            # Determine current connection state
            currently_connected = roblox_running and (not ENABLE_WINDOW_MONITORING or len(roblox_windows) > 0)

            # If we were connected and now we're not, that's a disconnection
            if self.was_connected and not currently_connected:
                logger.info("Disconnection detected: Roblox was running but now stopped/closed")
                self.last_disconnection_time = current_time
                self.was_connected = False
                self.consecutive_disconnects += 1
                return True

            # Update connection state
            if currently_connected:
                self.was_connected = True
                self.consecutive_disconnects = 0

            # Only check for specific disconnection popups if we think we're connected
            if currently_connected and ENABLE_WINDOW_MONITORING:
                # Check Roblox windows for disconnection messages
                for window in roblox_windows:
                    title = window.title.lower()
                    # Only check for very specific disconnection indicators
                    specific_indicators = ['disconnected', 'kicked', 'connection lost', 'session expired']
                    if any(indicator in title for indicator in specific_indicators):
                        logger.info(f"Disconnection message in Roblox window: {window.title}")
                        self.last_disconnection_time = current_time
                        self.was_connected = False
                        self.consecutive_disconnects += 1
                        return True

                # Check for Roblox-specific popup windows (very conservative)
                try:
                    all_windows = gw.getAllWindows()
                    for window in all_windows:
                        if window.title and 'roblox' in window.title.lower():
                            title = window.title.lower()
                            # Only check for very specific and strong disconnection indicators
                            if ('disconnected' in title or
                                ('kicked' in title and 'afk' in title) or
                                'session expired' in title):
                                logger.info(f"Roblox disconnection popup: {window.title}")
                                self.last_disconnection_time = current_time
                                self.was_connected = False
                                self.consecutive_disconnects += 1
                                return True
                except Exception as e:
                    logger.debug(f"Error checking popup windows: {e}")

            return False

        except Exception as e:
            logger.error(f"Error detecting disconnection: {e}")
            return False

    def get_last_game_url(self) -> Optional[str]:
        """Try to get the last game URL from browser history or clipboard"""
        # This is a simplified approach - in practice, you might want to
        # store the game URL when the script starts or use browser automation
        if ENABLE_CLIPBOARD_DETECTION:
            try:
                # Try to get from clipboard (user might have copied the game URL)
                clipboard_content = pyperclip.paste()
                # Only support private server share URLs
                if ("roblox.com/share" in clipboard_content and "type=Server" in clipboard_content and "code=" in clipboard_content):
                    return clipboard_content
            except:
                pass

        return None

    def is_valid_roblox_url(self, url: str) -> bool:
        """Check if the URL is a valid private server URL in the required format"""
        if not url:
            return False

        url_lower = url.lower()
        # Only accept private server share URLs in the specific format
        if "roblox.com/share" in url_lower and "type=server" in url_lower and "code=" in url_lower:
            return True

        return False

    def normalize_roblox_url(self, url: str) -> str:
        """Normalize Roblox URL to ensure it works properly"""
        if not url:
            return url

        # Ensure URL has proper protocol
        if url.startswith("www.roblox.com"):
            url = "https://" + url
        elif url.startswith("roblox.com"):
            url = "https://" + url
        elif not url.startswith(("http://", "https://", "roblox://")):
            # If it looks like a partial URL, try to fix it
            if "roblox.com" in url:
                url = "https://" + url

        return url

    def reconnect_to_game(self) -> bool:
        """Attempt to reconnect to the last Roblox game"""
        try:
            logger.info(f"Attempting reconnection (attempt {self.reconnect_attempts + 1})")

            # Try to get the last game URL
            game_url = self.get_last_game_url() or self.last_game_url

            if game_url and self.is_valid_roblox_url(game_url):
                # Normalize the URL to ensure it works properly
                normalized_url = self.normalize_roblox_url(game_url)
                logger.info(f"Reconnecting to: {normalized_url}")
                if "privateServerLinkCode=" in normalized_url:
                    logger.info("Detected private server URL")
                webbrowser.open(normalized_url)
                time.sleep(BROWSER_WAIT_TIME)  # Wait for browser to open

                # Private server URLs automatically open Roblox and join the server
                logger.info("Private server URL will automatically open Roblox and join the server")

            else:
                # If no URL available, just try to open Roblox
                logger.info("No game URL available, opening Roblox")
                try:
                    # Try to start Roblox directly
                    subprocess.Popen(['start', 'roblox:'], shell=True)
                except:
                    # Fallback to opening Roblox website
                    webbrowser.open('https://www.roblox.com/')

            self.reconnect_attempts += 1

            # Reset disconnection state after successful reconnection attempt
            import time
            self.last_disconnection_time = time.time()

            return True

        except Exception as e:
            logger.error(f"Error during reconnection: {e}")
            return False



    def send_notification(self, title: str, message: str):
        """Send desktop notification"""
        if not ENABLE_NOTIFICATIONS:
            return

        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Roblox Anti-Leave",
                timeout=NOTIFICATION_TIMEOUT
            )
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    def start_monitoring(self, game_url: Optional[str] = None):
        """Start monitoring for disconnections"""
        self.last_game_url = game_url
        self.monitoring = True
        self.reconnect_attempts = 0

        # Reset disconnection state when starting
        import time
        self.last_disconnection_time = 0
        self.was_connected = True  # Assume connected when starting
        self.consecutive_disconnects = 0

        logger.info("Starting Roblox disconnection monitoring...")
        if game_url:
            logger.info(f"Monitoring private server: {game_url}")

        self.send_notification("Roblox Anti-Leave", "Monitoring started")

        try:
            while self.monitoring:
                if self.detect_disconnection():
                    logger.warning("Disconnection detected!")
                    self.send_notification("Roblox Anti-Leave", "Disconnection detected! Attempting to reconnect...")

                    if self.reconnect_attempts < self.max_reconnect_attempts:
                        if self.reconnect_to_game():
                            logger.info("Reconnection attempt completed")
                            # Wait a bit longer after reconnection attempt
                            time.sleep(self.reconnect_delay)
                        else:
                            logger.error("Reconnection attempt failed")
                    else:
                        logger.error(f"Max reconnection attempts ({self.max_reconnect_attempts}) reached")
                        self.send_notification("Roblox Anti-Leave",
                                             f"Max reconnection attempts reached. Stopping monitoring.")
                        break

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error during monitoring: {e}")
        finally:
            self.monitoring = False
            logger.info("Monitoring stopped")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        logger.info("Stopping monitoring...")


def main():
    """Main function"""
    print("Roblox Anti-Leave Script")
    print("=" * 30)

    anti_leave = RobloxAntiLeave()

    # Get private server URL from user (optional)
    print("This script only works with private server URLs.")
    print("Required format: https://www.roblox.com/share?code=CODE&type=Server")
    print()
    game_url = input("Enter private server URL (optional, press Enter to skip): ").strip()
    if not game_url:
        game_url = None
    elif not anti_leave.is_valid_roblox_url(game_url):
        print("Error: Invalid URL format!")
        print("Only private server URLs are supported:")
        print("- https://www.roblox.com/share?code=CODE&type=Server")
        print("Please restart the script with a valid private server URL.")
        return
    else:
        # Normalize the URL
        game_url = anti_leave.normalize_roblox_url(game_url)
        print("✓ Valid private server URL detected!")

    print("\nStarting monitoring...")
    print("Press Ctrl+C to stop")

    try:
        anti_leave.start_monitoring(game_url)
    except KeyboardInterrupt:
        print("\nStopping...")
        anti_leave.stop_monitoring()


if __name__ == "__main__":
    main()