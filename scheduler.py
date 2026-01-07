#!/usr/bin/env python3
"""
Scheduler for running Lighter pair monitor at regular intervals.
Supports both one-time execution and continuous monitoring.
"""

import asyncio
import sys
from datetime import datetime
import signal

from monitor import PairMonitor
from config import Config


class ScheduledMonitor:
    """Runs the pair monitor on a schedule."""

    def __init__(self, config: Config, run_once: bool = False):
        self.config = config
        self.run_once = run_once
        self.should_stop = False
        self.monitor = PairMonitor(config)

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """Handle shutdown signals gracefully."""
        print("\n\nShutting down monitor...")
        self.should_stop = True

    async def run(self) -> None:
        """Run the monitor once or continuously."""
        if self.run_once:
            await self.monitor.run()
        else:
            await self._run_scheduled()

    async def _run_scheduled(self) -> None:
        """Run the monitor on a schedule."""
        print(f"\nStarting scheduled monitoring (interval: {self.config.CHECK_INTERVAL_SECONDS}s)")
        print("Press Ctrl+C to stop\n")

        while not self.should_stop:
            try:
                await self.monitor.run()

                if not self.should_stop:
                    print(f"\nNext check in {self.config.CHECK_INTERVAL_SECONDS} seconds...")
                    await asyncio.sleep(self.config.CHECK_INTERVAL_SECONDS)
            except Exception as e:
                print(f"Error in scheduled run: {e}")
                if not self.should_stop:
                    await asyncio.sleep(self.config.CHECK_INTERVAL_SECONDS)

        print("\nMonitor stopped.")


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Monitor Lighter exchange for new spot trading pairs'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run monitor once and exit'
    )
    parser.add_argument(
        '--interval',
        type=int,
        help='Override check interval in seconds'
    )

    args = parser.parse_args()

    config = Config()

    # Override interval if provided
    if args.interval:
        config.CHECK_INTERVAL_SECONDS = args.interval

    if not config.validate():
        print("Warning: Configuration validation failed")

    scheduler = ScheduledMonitor(config, run_once=args.once)
    await scheduler.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested")
        sys.exit(0)
