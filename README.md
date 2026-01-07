# Lighter Exchange Spot Pair Monitor

A Python-based monitoring system that tracks new spot trading pairs on the Lighter decentralized exchange and sends notifications when new pairs are added.

## Features

- **Real-time Pair Monitoring**: Continuously checks for new spot trading pairs on Lighter
- **Multiple Notification Channels**:
  - Console output (default)
  - Email notifications
  - Webhook notifications
  - Discord notifications
- **Persistent Storage**: Tracks previously seen pairs in JSON format
- **Scheduled Monitoring**: Run continuously or as a one-time check
- **Error Handling**: Graceful error recovery and error notifications
- **Easy Configuration**: Environment-based configuration with `.env` file support

## Installation

1. Clone the repository and navigate to the directory:
```bash
cd Lighter-new-pair-checker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example:
```bash
cp .env.example .env
```

4. Edit `.env` with your preferred settings

## Quick Start

### Run Once (Check immediately)
```bash
python monitor.py
```

### Continuous Monitoring (Checks every 5 minutes)
```bash
python scheduler.py
```

### Custom Interval (Check every 60 seconds)
```bash
python scheduler.py --interval 60
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

The monitor stores tracked pairs in `.data/tracked_pairs.json`:

```json
{
  "pairs": ["LIT_USDC", "ETH_USDC"],
  "last_updated": "2024-01-07T12:34:56.789012",
  "total_count": 2
}
```

## How It Works

1. **Fetch Current Pairs**: Uses the Lighter SDK to fetch all available spot trading pairs
2. **Compare with Previous**: Compares current pairs with previously tracked pairs
3. **Detect New Pairs**: Identifies any new pairs not seen before
4. **Send Notifications**: Sends notifications through configured channels
5. **Update Storage**: Updates the stored pair list for next check
6. **Schedule Next Check**: Waits for the configured interval before next check

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

## Setting Up as a Background Service

### Linux (systemd)

Create `/etc/systemd/system/lighter-monitor.service`:
```ini
[Unit]
Description=Lighter Exchange Spot Pair Monitor
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/Lighter-new-pair-checker
ExecStart=/usr/bin/python3 /home/youruser/Lighter-new-pair-checker/scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable lighter-monitor
sudo systemctl start lighter-monitor
```

### macOS (launchd)

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

## License

MIT License - Feel free to use and modify as needed

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review Lighter API documentation at https://docs.lighter.xyz
3. Check the lighter-sdk repository at https://github.com/elliottech/lighter-python
