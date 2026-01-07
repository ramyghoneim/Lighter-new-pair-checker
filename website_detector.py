"""
Website live pair detector for Lighter Exchange.
Checks which trading pairs are actually visible/live on the website.
"""

import asyncio
import json
import aiohttp
from typing import Set
from bs4 import BeautifulSoup
from datetime import datetime

from config import Config


class WebsitePairDetector:
    """Detects trading pairs that are actually live on the Lighter website."""

    def __init__(self, config: Config):
        self.config = config
        self.website_url = "https://app.lighter.xyz/trade"
        self.api_url = "https://api.lighter.xyz"

    async def get_website_pairs(self) -> Set[str]:
        """
        Fetch pairs that are visible on the Lighter website.
        Checks the API endpoint that serves the website data.
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Try to fetch the markets data endpoint used by the website
                # This typically returns live/visible pairs
                endpoints = [
                    f"{self.api_url}/v1/markets",
                    f"{self.api_url}/api/v1/markets",
                    f"{self.api_url}/v1/order-books",
                    f"{self.api_url}/api/v1/order-books",
                ]

                for endpoint in endpoints:
                    try:
                        async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                pairs = self._extract_pairs_from_response(data)
                                if pairs:
                                    print(f"✓ Retrieved {len(pairs)} live pairs from API")
                                    return pairs
                    except Exception as e:
                        continue

                # Fallback: Try to extract from HTML
                print("Attempting to detect pairs from website HTML...")
                return await self._get_pairs_from_html(session)

        except Exception as e:
            print(f"Error fetching website pairs: {e}")
            return set()

    async def _get_pairs_from_html(self, session: aiohttp.ClientSession) -> Set[str]:
        """
        Parse the Lighter website HTML to find available trading pairs.
        """
        try:
            async with session.get(self.website_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    print(f"Website returned status {resp.status}")
                    return set()

                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')

                pairs = set()

                # Look for pair links/buttons in the trading interface
                # These patterns search for common UI elements that display pairs
                patterns = [
                    # Look for trading pair divs/buttons with data attributes
                    soup.find_all('div', {'data-pair': True}),
                    soup.find_all('button', {'data-pair': True}),
                    soup.find_all('a', {'data-symbol': True}),
                    soup.find_all('span', {'class': lambda x: x and 'pair' in x.lower()}),
                ]

                for element_list in patterns:
                    for elem in element_list:
                        # Extract pair from data attributes
                        pair = (
                            elem.get('data-pair') or
                            elem.get('data-symbol') or
                            elem.get('data-name')
                        )
                        if pair and pair not in ['', None]:
                            pairs.add(pair)

                # Also try to find pairs in JavaScript/JSON data embedded in HTML
                script_tags = soup.find_all('script', {'type': 'application/json'})
                for script in script_tags:
                    try:
                        data = json.loads(script.string)
                        extracted = self._extract_pairs_from_response(data)
                        pairs.update(extracted)
                    except:
                        pass

                if pairs:
                    print(f"✓ Extracted {len(pairs)} pairs from website HTML")
                    return pairs

                print("⚠️  Could not extract pairs from website HTML")
                return set()

        except Exception as e:
            print(f"Error parsing website HTML: {e}")
            return set()

    def _extract_pairs_from_response(self, data) -> Set[str]:
        """Extract trading pairs from API or JSON response."""
        pairs = set()

        if isinstance(data, dict):
            # Check common API response structures
            for key in ['markets', 'pairs', 'order_books', 'orderBooks', 'data', 'result']:
                if key in data:
                    items = data[key]
                    if isinstance(items, list):
                        for item in items:
                            pair = self._extract_pair_from_item(item)
                            if pair:
                                pairs.add(pair)

            # Recursive search for symbol/pair fields
            for value in data.values():
                if isinstance(value, (list, dict)):
                    pairs.update(self._extract_pairs_from_response(value))

        elif isinstance(data, list):
            for item in data:
                pair = self._extract_pair_from_item(item)
                if pair:
                    pairs.add(pair)
                if isinstance(item, (list, dict)):
                    pairs.update(self._extract_pairs_from_response(item))

        return pairs

    def _extract_pair_from_item(self, item) -> str:
        """Extract pair symbol from a single item."""
        if isinstance(item, str):
            # Check if string looks like a trading pair (e.g., "BTC_USDC")
            if '_' in item and 2 <= len(item.split('_')[0]) <= 10:
                return item
            return None

        if isinstance(item, dict):
            # Look for common field names
            for field in ['symbol', 'pair', 'name', 'market', 'ticker']:
                if field in item:
                    value = item[field]
                    if isinstance(value, str) and '_' in value:
                        return value

        return None

    async def detect_live_pairs_change(self, previous_website_pairs: Set[str]) -> Set[str]:
        """
        Detect which pairs are now live on the website.
        Returns only pairs that are currently live on the website.
        """
        current_website_pairs = await self.get_website_pairs()
        new_on_website = current_website_pairs - previous_website_pairs

        if new_on_website:
            print(f"\n✅ {len(new_on_website)} pair(s) are now LIVE on the website:")
            for pair in sorted(new_on_website):
                print(f"   • {pair}")

        return new_on_website

    def is_pair_tradeable(self, pair: str, api_pairs: Set[str], website_pairs: Set[str]) -> bool:
        """
        Check if a pair is both in the API and visible on the website.
        Only return True if pair is live on the website.
        """
        return pair in api_pairs and pair in website_pairs
