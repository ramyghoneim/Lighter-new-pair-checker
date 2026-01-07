# Lighter Exchange Spot Pair Monitor

A Python-based monitoring system that tracks new spot trading pairs on the Lighter decentralized exchange and sends notifications **when new pairs go LIVE on the website**.

## Key Feature: Website-Live Detection

This monitor specifically detects when pairs become **live and visible on the Lighter website**, not just when they appear in the backend API. Since the backend can register pairs before they're available to trade on the website, this monitor waits for pairs to actually be live on the site before alerting you.

## Features

- **Website-Live Pair Detection**: Monitors when pairs become visible/tradeable on the Lighter website (not just backend)
- **Backend vs. Website Awareness**: Tracks both API pairs and website-visible pairs to ensure accuracy
- **Real-time Pair Monitoring**: Continuously checks for new spot trading pairs
- **Multiple Notification Channels**:
  - Console output (default)
  - Email notifications
  - Webhook notifications
  - Discord notifications
- **Persistent Storage**: Tracks previously seen website-live pairs in JSON format
- **Scheduled Monitoring**: Run continuously or as a one-time check
- **Error Handling**: Graceful error recovery and error notifications
- **Easy Configuration**: Environment-based configuration with `.env` file support

## Installation

1. Clone the repository and navigate to the directory:
```bash
cd Lighter-new-pair-checker
```

2. Run the setup script:
```bash
./setup.sh
```

3. Create a `.env` file from the example:
```bash
cp .env.example .env
```

4. Edit `.env` with your preferred settings:
```bash
nano .env
```

## Quick Start

### Test the Monitor (One-time check)
```bash
python monitor.py
```

### Run for 24/7 Monitoring (Recommended for Production)

#### Option 1: Systemd Service (Linux) - **RECOMMENDED**
Automatically restarts on failure, runs at boot, manages logs automatically.

```bash
# Install and start the service
sudo bash install-service.sh
```

Check status:
```bash
sudo systemctl status lighter-monitor
```

View live logs:
```bash
sudo journalctl -u lighter-monitor -f
```

#### Option 2: Docker Container
Run in a containerized environment (requires Docker):

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f lighter-monitor

# Stop
docker-compose down
```

#### Option 3: Manual Continuous Run
Run in the foreground (less reliable, will stop if terminal closes):

```bash
# Checks every 5 minutes
python scheduler.py

# Custom interval (60 seconds)
python scheduler.py --interval 60
```

#### Option 4: Supervisor (Process Manager)
For servers without systemd:

```bash
sudo cp lighter-monitor.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start lighter-monitor
```

## Configuration

Edit the `.env` file to customize the monitor:

### Basic Settings
```env
# Storage directory for tracking pairs
STORAGE_DIR=.data

# Notification type: console, email, webhook, discord
NOTIFICATION_TYPE=console

# Check interval in seconds (default: 300 = 5 minutes)
CHECK_INTERVAL_SECONDS=300
```

### Email Notifications
To enable email notifications:

1. Set `EMAIL_ENABLED=true`
2. Configure SMTP settings:
```env
EMAIL_ENABLED=true
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use app-specific password for Gmail
```

### Webhook Notifications
For generic webhooks:

```env
WEBHOOK_ENABLED=true
WEBHOOK_URL=https://your-server.com/webhook
```

### Discord Notifications
For Discord notifications:

1. Create a Discord webhook in your server settings
2. Set in `.env`:
```env
DISCORD_ENABLED=true
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/YOUR_ID/YOUR_TOKEN
```

## Usage Examples

### Monitor with Email Notifications
```bash
# Set up .env with email configuration
NOTIFICATION_TYPE=email
EMAIL_ENABLED=true
EMAIL_FROM=monitor@example.com
EMAIL_TO=alerts@example.com

# Run continuous monitoring
python scheduler.py
```

### Monitor with Discord Notifications
```bash
# Set up .env with Discord webhook
NOTIFICATION_TYPE=discord
DISCORD_ENABLED=true
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/...

# Run continuous monitoring
python scheduler.py
```

### Monitor with Custom Interval
```bash
# Check every 2 minutes (120 seconds)
python scheduler.py --interval 120
```

## Project Structure

```
Lighter-new-pair-checker/
├── monitor.py          # Main monitoring logic
├── scheduler.py        # Scheduled execution runner
├── config.py           # Configuration management
├── notification.py     # Notification system
├── requirements.txt    # Python dependencies
├── .env.example        # Example configuration
└── README.md          # This file
```

## Data Storage

The monitor stores tracked pairs in two files:

**`.data/website_live_pairs.json`** - Pairs currently live on the website:
```json
{
  "pairs": ["LIT_USDC", "ETH_USDC"],
  "last_updated": "2024-01-07T12:34:56.789012",
  "total_count": 2
}
```

**`.data/tracked_pairs.json`** - All pairs from backend API (for reference):
```json
{
  "pairs": ["LIT_USDC", "ETH_USDC", "BTC_USDC"],
  "last_updated": "2024-01-07T12:34:56.789012",
  "total_count": 3
}
```

The key difference: You'll only be notified when pairs appear in `website_live_pairs.json`, which reflects what's actually tradeable on the website.

## How It Works

1. **Fetch Backend Pairs**: Uses the Lighter SDK API to fetch all spot trading pairs from the backend
2. **Detect Website-Live Pairs**: Fetches the Lighter website to detect which pairs are actually visible/tradeable
3. **Compare with Previous**: Compares current website-live pairs with previously tracked ones
4. **Detect NEW Live Pairs**: Identifies pairs that are now live on the website for the first time
5. **Send Notifications**: Only notifies for pairs that are confirmed live on the website
6. **Update Storage**:
   - Updates `website_live_pairs.json` with pairs currently live on website
   - Updates `tracked_pairs.json` with all backend API pairs (for reference)
7. **Schedule Next Check**: Waits for the configured interval before next check

**Important**: Notifications are only sent when a pair transitions from "not visible on website" to "live on website". Pairs that exist in the backend but aren't yet on the website won't trigger alerts.

## API Details

The monitor uses the Lighter Python SDK's `OrderApi.order_books()` method:

```python
order_api = lighter.OrderApi(client)
books = await order_api.order_books()
```

This returns all available order books (trading pairs) on the exchange.

## Troubleshooting

### "lighter-sdk not installed"
```bash
pip install -r requirements.txt
```

### Email not sending
- Verify SMTP credentials in `.env`
- For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)
- Check firewall/network if using external SMTP

### Discord webhook not working
- Verify webhook URL is correct
- Ensure Discord webhook has "Send Messages" permission
- Check if webhook has been deleted in Discord

### No pairs detected
- Verify internet connection
- Check if Lighter API is accessible
- Ensure `lighter-sdk` is properly installed

## Notifications

### Console (Default)
Prints new pairs to terminal/logs:
```
🎉 Found 1 new pair(s)!
  ✓ BTC_USDC
```

### Email
Sends formatted email with new pairs list

### Webhook
Sends JSON POST request:
```json
{
  "title": "New Lighter Trading Pairs",
  "pairs": ["BTC_USDC"],
  "pair_count": 1,
  "timestamp": "2024-01-07T12:34:56.789012"
}
```

### Discord
Sends embedded Discord message with pairs list

## 24/7 Background Service Setup

### Linux (Systemd) - Easiest Setup ⭐

The quickest way to run 24/7:

```bash
# One command does everything:
# - Creates lighter-monitor user
# - Installs systemd service
# - Enables auto-start on boot
# - Starts the monitor
sudo bash install-service.sh
```

**Verify it's running:**
```bash
sudo systemctl status lighter-monitor
```

**View live logs:**
```bash
sudo journalctl -u lighter-monitor -f
```

**Management commands:**
```bash
sudo systemctl stop lighter-monitor      # Stop monitoring
sudo systemctl start lighter-monitor     # Resume monitoring
sudo systemctl restart lighter-monitor   # Restart
sudo systemctl disable lighter-monitor   # Remove auto-start
```

### Docker (All Platforms)

Works on Linux, macOS, Windows:

```bash
docker-compose up -d
docker-compose logs -f lighter-monitor  # View logs
docker-compose down                      # Stop
```

### macOS (Launchd)

Create `~/Library/LaunchAgents/com.lighter.monitor.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lighter.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/scheduler.py</string>
    </array>
    <key>StartInterval</key>
    <integer>300</integer>
    <key>StandardOutPath</key>
    <string>/var/log/lighter-monitor.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/lighter-monitor.log</string>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.lighter.monitor.plist
```

### Supervisor (Alternative Process Manager)

For servers without systemd:

```bash
sudo cp lighter-monitor.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start lighter-monitor

# View status
sudo supervisorctl status lighter-monitor

# View logs
tail -f /var/log/lighter-monitor/monitor.log
```

## License

MIT License - Feel free to use and modify as needed

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review Lighter API documentation at https://docs.lighter.xyz
3. Check the lighter-sdk repository at https://github.com/elliottech/lighter-python
