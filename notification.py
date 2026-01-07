"""Notification system for Lighter pair monitor."""

import asyncio
import json
from datetime import datetime
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    import aiohttp
except ImportError:
    aiohttp = None

from config import Config


class NotificationManager:
    """Manages sending notifications through multiple channels."""

    def __init__(self, config: Config):
        self.config = config
        self.notification_type = config.NOTIFICATION_TYPE.lower()

    async def notify_new_pairs(self, new_pairs: List[str]) -> None:
        """Send notification about new trading pairs."""
        message = self._format_new_pairs_message(new_pairs)

        if self.notification_type == 'email':
            self._send_email_notification(
                subject="🎉 New Trading Pairs on Lighter Exchange",
                body=message,
                pairs=new_pairs
            )
        elif self.notification_type == 'webhook':
            await self._send_webhook_notification(
                title="New Lighter Trading Pairs",
                message=message,
                pairs=new_pairs
            )
        elif self.notification_type == 'discord':
            await self._send_discord_notification(
                title="New Lighter Trading Pairs",
                pairs=new_pairs
            )
        else:  # console (default)
            self._send_console_notification(message)

    async def notify_error(self, error_message: str) -> None:
        """Send notification about errors during monitoring."""
        if self.notification_type == 'email':
            self._send_email_notification(
                subject="⚠️ Lighter Pair Monitor Error",
                body=f"An error occurred during monitoring:\n\n{error_message}"
            )
        elif self.notification_type == 'webhook':
            await self._send_webhook_notification(
                title="Lighter Monitor Error",
                message=error_message,
                error=True
            )
        elif self.notification_type == 'discord':
            await self._send_discord_notification(
                title="Monitor Error",
                error=True,
                message=error_message
            )
        else:
            print(f"⚠️ Error: {error_message}")

    def _format_new_pairs_message(self, pairs: List[str]) -> str:
        """Format new pairs into a readable message."""
        pairs_list = "\n".join([f"• {pair}" for pair in pairs])
        return f"""
New Trading Pairs Detected on Lighter Exchange!

Found {len(pairs)} new pair(s):
{pairs_list}

Time: {datetime.utcnow().isoformat()}
"""

    def _send_console_notification(self, message: str) -> None:
        """Print notification to console."""
        print(message)

    def _send_email_notification(self, subject: str, body: str, pairs: List[str] = None) -> None:
        """Send email notification."""
        if not self.config.EMAIL_ENABLED:
            print("Email notifications not enabled")
            return

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.EMAIL_FROM
            msg['To'] = self.config.EMAIL_TO

            # Create HTML version
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif;">
                <h2>{subject}</h2>
                <p>{body.replace(chr(10), '<br>')}</p>
                {self._generate_html_pair_table(pairs) if pairs else ''}
                <hr>
                <small>Lighter Exchange Pair Monitor</small>
              </body>
            </html>
            """

            part1 = MIMEText(body, 'plain')
            part2 = MIMEText(html_body, 'html')

            msg.attach(part1)
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
                server.starttls()
                server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
                server.send_message(msg)

            print(f"✓ Email sent to {self.config.EMAIL_TO}")
        except Exception as e:
            print(f"✗ Failed to send email: {e}")

    async def _send_webhook_notification(self, title: str, message: str = "",
                                        pairs: List[str] = None, error: bool = False) -> None:
        """Send webhook notification."""
        if not self.config.WEBHOOK_ENABLED or not aiohttp:
            print("Webhook notifications not configured")
            return

        try:
            payload = {
                "title": title,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "error": error
            }

            if pairs:
                payload["pairs"] = pairs
                payload["pair_count"] = len(pairs)

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.WEBHOOK_URL,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        print(f"✓ Webhook notification sent")
                    else:
                        print(f"✗ Webhook returned status {resp.status}")
        except Exception as e:
            print(f"✗ Failed to send webhook: {e}")

    async def _send_discord_notification(self, title: str, pairs: List[str] = None,
                                         error: bool = False, message: str = "") -> None:
        """Send Discord webhook notification."""
        if not self.config.DISCORD_ENABLED or not aiohttp:
            print("Discord notifications not configured")
            return

        try:
            embed = {
                "title": title,
                "color": 16711680 if error else 65280,  # Red for errors, green for new pairs
                "timestamp": datetime.utcnow().isoformat()
            }

            if pairs:
                pairs_str = "\n".join([f"• `{pair}`" for pair in pairs])
                embed["fields"] = [
                    {
                        "name": f"New Pairs ({len(pairs)})",
                        "value": pairs_str,
                        "inline": False
                    }
                ]
            elif message:
                embed["description"] = message

            payload = {"embeds": [embed]}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.DISCORD_WEBHOOK_URL,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 204:
                        print(f"✓ Discord notification sent")
                    else:
                        print(f"✗ Discord returned status {resp.status}")
        except Exception as e:
            print(f"✗ Failed to send Discord notification: {e}")

    @staticmethod
    def _generate_html_pair_table(pairs: List[str]) -> str:
        """Generate HTML table for pairs."""
        if not pairs:
            return ""

        rows = "\n".join([f"<tr><td>{pair}</td></tr>" for pair in pairs])
        return f"""
        <table style="border-collapse: collapse; margin: 10px 0;">
          <tr style="background-color: #f0f0f0;">
            <th style="border: 1px solid #ddd; padding: 8px;">Pair</th>
          </tr>
          {rows}
        </table>
        """
