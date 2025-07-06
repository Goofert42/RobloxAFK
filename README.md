# Quick Usage Guide

## Getting Started

1. **Double-click `run_antileave.bat`** - This will automatically install dependencies and start the script
   
   OR
   
   **Run manually:**
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

2. **Enter a private server URL** (required for reconnection):
   - Copy the private server URL you want to play on
   - Paste it when the script asks for it
   - This helps the script reconnect to the exact same private server
   - Required format: `https://www.roblox.com/share?code=CODE&type=Server`

3. **The script will start monitoring** and show status messages

## What the Script Does

- **Monitors every 5 seconds** for disconnections
- **Detects disconnections** by checking:
  - If Roblox processes are still running
  - If Roblox windows contain disconnection keywords
  - If Roblox windows disappear completely

- **Automatically reconnects** by:
  - Opening the private server URL, which automatically launches Roblox and joins the server

- **Sends notifications** when disconnections are detected
- **Logs everything** to `roblox_antileave.log`

## Customization

Edit `config.py` to customize:
- Check interval (how often to check for disconnections)
- Maximum reconnection attempts
- Disconnection keywords to look for
- Enable/disable notifications
- And much more!

## Tips for Best Results

1. **Provide a private server URL** when starting the script
2. **Keep the script running** in the background while playing
3. **Check the log file** if you encounter issues

## Stopping the Script

Press `Ctrl+C` in the terminal window to stop monitoring.

## Troubleshooting

- **No disconnections detected**: The script might be working perfectly! Check the log file for details.
- **False disconnections**: Adjust the disconnection keywords in `config.py`
- **Reconnection not working**: Make sure you provided a valid game URL
- **Notifications not showing**: Check if notifications are enabled in `config.py`