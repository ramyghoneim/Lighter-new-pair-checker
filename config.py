"""Configuration management for Lighter pair monitor."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the pair monitoring system."""

    # Storage
    STORAGE_DIR = Path(os.getenv('STORAGE_DIR', '.data'))
    PAIRS_STORAGE_PATH = STORAGE_DIR / 'tracked_pairs.json'

    # Notification settings
    NOTIFICATION_TYPE = os.getenv('NOTIFICATION_TYPE', 'console')  # 'console', 'email', 'webhook', 'discord'

    # Email settings (if using email notifications)
    EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
    EMAIL_FROM = os.getenv('EMAIL_FROM', '')
    EMAIL_TO = os.getenv('EMAIL_TO', '')
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

    # Webhook settings (if using webhook notifications)
    WEBHOOK_ENABLED = os.getenv('WEBHOOK_ENABLED', 'false').lower() == 'true'
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')

    # Discord settings (if using Discord notifications)
    DISCORD_ENABLED = os.getenv('DISCORD_ENABLED', 'false').lower() == 'true'
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')

    # Lighter API settings
    LIGHTER_API_URL = os.getenv('LIGHTER_API_URL', 'https://api.lighter.xyz')

    # Monitoring settings
    CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', '300'))  # 5 minutes default

    @property
    def pairs_storage_path(self) -> str:
        return str(self.PAIRS_STORAGE_PATH)

    def validate(self) -> bool:
        """Validate configuration."""
        if self.NOTIFICATION_TYPE == 'email' and self.EMAIL_ENABLED:
            if not all([self.EMAIL_FROM, self.EMAIL_TO, self.SMTP_USERNAME, self.SMTP_PASSWORD]):
                print("Warning: Email notifications enabled but missing required configuration")
                return False

        if self.NOTIFICATION_TYPE == 'webhook' and self.WEBHOOK_ENABLED:
            if not self.WEBHOOK_URL:
                print("Warning: Webhook notifications enabled but WEBHOOK_URL not set")
                return False

        if self.NOTIFICATION_TYPE == 'discord' and self.DISCORD_ENABLED:
            if not self.DISCORD_WEBHOOK_URL:
                print("Warning: Discord notifications enabled but DISCORD_WEBHOOK_URL not set")
                return False

        return True
