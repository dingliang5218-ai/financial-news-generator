from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from config import Config
from logger import Logger
from health_check import HealthCheck
from data_fetcher import DataFetcher
from analyzer import Analyzer
from generator import Generator
from storage import Storage
from error_handler import RetryableError, handle_errors

logger = Logger.get_logger("scheduler")


class NewsScheduler:
    """Automated news generation scheduler"""

    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.storage = Storage()
        self.fetcher = DataFetcher()
        self.analyzer = Analyzer()
        self.generator = Generator()

    def setup(self):
        """Setup scheduled tasks"""
        logger.info("Setting up scheduler...")

        # Daily news generation at 8:00 AM
        self.scheduler.add_job(
            self.generate_daily_news,
            CronTrigger(hour=8, minute=0),
            id="daily_news",
            name="Generate Daily Financial News",
            max_instances=1,
        )

        # Hourly market updates (9 AM - 5 PM on weekdays)
        self.scheduler.add_job(
            self.generate_market_update,
            CronTrigger(day_of_week="mon-fri", hour="9-17", minute=0),
            id="market_updates",
            name="Generate Market Updates",
            max_instances=1,
        )

        # Weekly summary on Sunday at 6 PM
        self.scheduler.add_job(
            self.generate_weekly_summary,
            CronTrigger(day_of_week="sun", hour=18, minute=0),
            id="weekly_summary",
            name="Generate Weekly Summary",
            max_instances=1,
        )

        # Health check every 6 hours
        self.scheduler.add_job(
            HealthCheck.runtime_check,
            CronTrigger(hour="*/6"),
            id="health_check",
            name="Runtime Health Check",
            max_instances=1,
        )

        logger.info("Scheduler setup complete")

    @handle_errors(max_retries=3, retry_delay=300)
    def generate_daily_news(self):
        """Generate daily financial news"""
        logger.info("Starting daily news generation...")

        try:
            # Runtime health check
            if not HealthCheck.runtime_check():
                raise RetryableError("Health check failed")

            # Fetch news
            news_items = self.fetcher.fetch_all_sources()
            if not news_items:
                logger.warning("No news items fetched")
                return

            # Analyze and generate
            analysis = self.analyzer.analyze_batch(news_items)
            articles = []

            for item in analysis["priority_items"][:5]:  # Top 5 stories
                article = self.generator.generate_article(item, style="comprehensive")
                articles.append(article)
                self.storage.save_article(article)

            logger.info(f"Daily news generation complete: {len(articles)} articles")

        except Exception as e:
            logger.error(f"Daily news generation failed: {e}")
            raise

    @handle_errors(max_retries=2, retry_delay=60)
    def generate_market_update(self):
        """Generate hourly market update"""
        logger.info("Starting market update generation...")

        try:
            # Quick health check
            if not HealthCheck.runtime_check():
                raise RetryableError("Health check failed")

            # Fetch recent news (last hour)
            news_items = self.fetcher.fetch_all_sources()
            if not news_items:
                logger.info("No new market updates")
                return

            # Quick analysis
            analysis = self.analyzer.analyze_batch(news_items)

            if analysis["priority_items"]:
                # Generate brief update
                article = self.generator.generate_article(
                    analysis["priority_items"][0], style="brief"
                )
                self.storage.save_article(article)
                logger.info("Market update generated")

        except Exception as e:
            logger.error(f"Market update generation failed: {e}")
            raise

    @handle_errors(max_retries=3, retry_delay=600)
    def generate_weekly_summary(self):
        """Generate weekly summary"""
        logger.info("Starting weekly summary generation...")

        try:
            # Health check
            if not HealthCheck.runtime_check():
                raise RetryableError("Health check failed")

            # Get week's articles
            articles = self.storage.get_articles_by_date_range(days=7)

            if not articles:
                logger.warning("No articles found for weekly summary")
                return

            # Generate summary
            summary = self.generator.generate_weekly_summary(articles)
            self.storage.save_article(summary)

            logger.info("Weekly summary generated")

        except Exception as e:
            logger.error(f"Weekly summary generation failed: {e}")
            raise

    def start(self):
        """Start the scheduler"""
        logger.info("Starting scheduler...")
        logger.info(f"Scheduled jobs: {len(self.scheduler.get_jobs())}")

        for job in self.scheduler.get_jobs():
            logger.info(f"  - {job.name} (next run: {job.next_run_time})")

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped by user")
            self.shutdown()

    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down scheduler...")
        self.scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped")

    def run_once(self, task="daily"):
        """Run a task once (for testing)"""
        logger.info(f"Running task once: {task}")

        tasks = {
            "daily": self.generate_daily_news,
            "market": self.generate_market_update,
            "weekly": self.generate_weekly_summary,
        }

        if task not in tasks:
            raise ValueError(f"Unknown task: {task}")

        tasks[task]()
