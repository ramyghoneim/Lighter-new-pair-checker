#!/usr/bin/env python3
"""
Lighter Exchange Spot Pair Monitoring System
Monitors the Lighter exchange for new spot trading pairs and sends notifications.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
import sys

try:
    import lighter
except ImportError:
    print("Error: lighter-sdk not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

from notification import NotificationManager
from config import Config
from website_detector import WebsitePairDetector


class PairMonitor:
    def __init__(self, config: Config):
        self.config = config
        self.pairs_file = Path(config.pairs_storage_path)
        self.website_pairs_file = Path(config.pairs_storage_path).parent / 'website_live_pairs.json'
        self.notifier = NotificationManager(config)
        self.detector = WebsitePairDetector(config)
        self.previous_api_pairs = self._load_pairs('api')
        self.previous_website_pairs = self._load_pairs('website')

    def _load_pairs(self, pair_type: str = 'api') -> set:
        """Load previously tracked pairs from storage."""
        file_path = self.website_pairs_file if pair_type == 'website' else self.pairs_file

        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return set(data.get('pairs', []))
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load {pair_type} pairs file: {e}")
                return set()
        return set()

    def _save_pairs(self, pairs: set, pair_type: str = 'api') -> None:
        """Save current pairs to storage."""
        file_path = self.website_pairs_file if pair_type == 'website' else self.pairs_file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump({
                'pairs': sorted(list(pairs)),
                'last_updated': datetime.utcnow().isoformat(),
                'total_count': len(pairs)
            }, f, indent=2)

    async def fetch_pairs(self) -> set:
        """Fetch all available spot trading pairs from Lighter."""
        client = lighter.ApiClient()
        try:
            order_api = lighter.OrderApi(client)
            books = await order_api.order_books()

            # Extract pair symbols and filter for spot pairs
            # Spot pairs are identified by having "spot" type
            pairs = set()
            if books:
                for book in books:
                    # The symbol is typically in format like "LIT_USDC"
                    if hasattr(book, 'symbol'):
                        symbol = book.symbol
                    elif isinstance(book, dict) and 'symbol' in book:
                        symbol = book['symbol']
                    else:
                        continue

                    # Check if this is a spot pair (not a perpetual futures)
                    # Lighter futures pairs typically have additional identifiers
                    if self._is_spot_pair(book):
                        pairs.add(symbol)

            return pairs
        except Exception as e:
            print(f"Error fetching pairs: {e}")
            return self.previous_pairs  # Return previous pairs on error
        finally:
            await client.close()

    def _is_spot_pair(self, book) -> bool:
        """Determine if a trading pair is a spot pair (not perpetual futures)."""
        # Check for spot market type
        if hasattr(book, 'market_type'):
            return book.market_type == 'spot'
        elif isinstance(book, dict) and 'market_type' in book:
            return book['market_type'] == 'spot'

        # If no explicit market type, check if it has futures-specific fields
        # Perpetual futures typically have funding rates, leverage, etc.
        futures_indicators = ['funding_rate', 'leverage', 'max_leverage', 'is_perpetual']

        if isinstance(book, dict):
            for indicator in futures_indicators:
                if indicator in book:
                    return False
        else:
            for indicator in futures_indicators:
                if hasattr(book, indicator):
                    return False

        # Default to spot if uncertain
        return True

    async def check_for_new_pairs(self) -> list:
        """Check for new trading pairs that are live on the website."""
        # Fetch pairs from both API and website
        current_api_pairs = await self.fetch_pairs()
        current_website_pairs = await self.detector.get_website_pairs()

        print(f"\nAPI pairs: {len(current_api_pairs)}")
        print(f"Website pairs: {len(current_website_pairs)}")

        # Find pairs that are LIVE ON WEBSITE (not just in backend API)
        live_website_pairs = current_website_pairs

        # Find NEW pairs that are live on website
        new_live_pairs = live_website_pairs - self.previous_website_pairs

        if new_live_pairs:
            print(f"\n🎉 Found {len(new_live_pairs)} new pair(s) LIVE on website!")
            for pair in sorted(new_live_pairs):
                print(f"  ✓ {pair}")

            # Send notifications only for website-live pairs
            await self.notifier.notify_new_pairs(sorted(new_live_pairs))

            # Update stored pairs
            self.previous_website_pairs = live_website_pairs
            self._save_pairs(live_website_pairs, pair_type='website')
        else:
            print(f"\nNo new pairs went live on website. Total live pairs: {len(live_website_pairs)}")

        # Also track API pairs for reference
        self.previous_api_pairs = current_api_pairs
        self._save_pairs(current_api_pairs, pair_type='api')

        return sorted(list(new_live_pairs))

    async def run(self) -> None:
        """Run a single monitoring check."""
        print(f"\n{'='*60}")
        print(f"Lighter Pair Monitor - Check at {datetime.utcnow().isoformat()}")
        print(f"{'='*60}")
        print("Monitoring for NEW pairs that go LIVE on the website...")

        try:
            new_pairs = await self.check_for_new_pairs()

            # Print current status
            print(f"\n{'='*60}")
            print(f"Live Website Pairs: {len(self.previous_website_pairs)}")
            if self.previous_website_pairs:
                print("Currently live pairs on website:")
                for pair in sorted(self.previous_website_pairs):
                    print(f"  • {pair}")

        except Exception as e:
            print(f"Error during monitoring: {e}")
            error_msg = f"Error during monitoring: {e}"
            await self.notifier.notify_error(error_msg)


async def main():
    config = Config()
    monitor = PairMonitor(config)
    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())
