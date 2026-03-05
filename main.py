#!/usr/bin/env python3
"""
Financial News Auto-Generation System
Main entry point
"""

import sys
import argparse
from pathlib import Path

from config import Config
from logger import Logger
from health_check import HealthCheck
from scheduler import NewsScheduler
from error_handler import FatalError

logger = Logger.get_logger("main")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Financial News Auto-Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start scheduler (default)
  %(prog)s --run-once daily   # Generate daily news once
  %(prog)s --run-once market  # Generate market update once
  %(prog)s --run-once weekly  # Generate weekly summary once
  %(prog)s --health-check     # Run health check only
        """,
    )

    parser.add_argument(
        "--run-once",
        choices=["daily", "market", "weekly"],
        help="Run a task once and exit (for testing)",
    )

    parser.add_argument(
        "--health-check", action="store_true", help="Run health check only and exit"
    )

    parser.add_argument(
        "--skip-health-check",
        action="store_true",
        help="Skip startup health check (not recommended)",
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {Config.VERSION}"
    )

    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()

    logger.info("=" * 60)
    logger.info(f"Financial News Auto-Generation System v{Config.VERSION}")
    logger.info("=" * 60)

    try:
        # Health check only mode
        if args.health_check:
            logger.info("Running health check...")
            HealthCheck.startup_check()
            logger.info("Health check passed!")
            return 0

        # Startup health check
        if not args.skip_health_check:
            HealthCheck.startup_check()
        else:
            logger.warning("Skipping health check (not recommended)")

        # Initialize scheduler
        scheduler = NewsScheduler()
        scheduler.setup()

        # Run once mode
        if args.run_once:
            logger.info(f"Running task once: {args.run_once}")
            scheduler.run_once(args.run_once)
            logger.info("Task completed successfully")
            return 0

        # Normal scheduler mode
        logger.info("Starting scheduler in daemon mode...")
        logger.info("Press Ctrl+C to stop")
        scheduler.start()

        return 0

    except FatalError as e:
        logger.critical(f"Fatal error: {e}")
        return 1

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0

    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
