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

    def _run_news_generation(self):
        """Run news generation task with aggregation and ranking"""
        try:
            logger.info("=" * 60)
            logger.info("Starting news generation task")

            # Step 1: Fetch news
            logger.info("Step 1: Fetching news from all sources...")
            news_items = self.fetcher.fetch_all()

            if not news_items:
                logger.warning("No news items fetched")
                return

            logger.info(f"Fetched {len(news_items)} news items")

            # Step 2: Analyze news
            logger.info("Step 2: Analyzing news importance...")
            analyses = {}
            important_news = []

            for item in news_items:
                analysis = self.analyzer.analyze(item)
                if analysis:
                    analyses[item.url] = analysis
                    if self.analyzer.should_generate_article(analysis):
                        important_news.append(item)

            logger.info(f"Found {len(important_news)} important news items")

            if not important_news:
                logger.warning("No important news to process")
                return

            # Step 3: Aggregate news into events
            logger.info("Step 3: Aggregating news into events...")
            from aggregator import NewsAggregator
            aggregator = NewsAggregator()
            events = aggregator.aggregate(important_news, analyses)

            if not events:
                logger.warning("No events after aggregation")
                return

            logger.info(f"Aggregated into {len(events)} events")

            # Step 4: Rank and select Top 3
            logger.info("Step 4: Ranking events and selecting Top 3...")
            from ranker import NewsRanker
            ranker = NewsRanker()
            top_events = ranker.rank_and_select_top(events, top_n=3)

            if not top_events:
                logger.warning("No top events selected")
                return

            logger.info(f"Selected {len(top_events)} top events")

            # Step 5: Analyze impact for Top 3
            logger.info("Step 5: Analyzing multi-dimensional impact...")
            from impact_analyzer import ImpactAnalyzer
            impact_analyzer = ImpactAnalyzer()
            impact_analyses = {}

            for event in top_events:
                try:
                    analysis = impact_analyzer.analyze(event)
                    impact_analyses[event.event_id] = analysis
                    self.storage.save_impact_analysis(analysis)
                except Exception as e:
                    logger.error(f"Failed to analyze impact for {event.event_id}: {e}")

            # Step 6: Save events
            logger.info("Step 6: Saving events to database...")
            for event in top_events:
                self.storage.save_event(event)

            # Step 7: Generate daily summary
            logger.info("Step 7: Generating daily summary article...")
            try:
                summary_article = self.generator.generate_daily_summary(
                    top_events, impact_analyses
                )
                self.storage.save_article_with_event(
                    summary_article,
                    event_id=','.join([e.event_id for e in top_events])
                )
                logger.info("Daily summary generated successfully")
            except Exception as e:
                logger.error(f"Failed to generate daily summary: {e}")

            # Step 8: Generate deep analysis for high-importance events
            logger.info("Step 8: Generating deep analysis articles...")
            deep_analysis_count = 0

            for event in top_events:
                # Generate deep analysis if importance >= 4 and hotness >= 3
                if event.importance >= 4 and event.hotness >= 3:
                    try:
                        analysis = impact_analyses.get(event.event_id)
                        if analysis:
                            deep_article = self.generator.generate_deep_analysis_for_event(
                                event, analysis
                            )
                            self.storage.save_article_with_event(
                                deep_article,
                                event_id=event.event_id
                            )
                            deep_analysis_count += 1
                            logger.info(f"Deep analysis generated for: {event.main_title}")
                    except Exception as e:
                        logger.error(f"Failed to generate deep analysis for {event.event_id}: {e}")

            logger.info(f"Generated {deep_analysis_count} deep analysis articles")
            logger.info("News generation task completed successfully")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"News generation task failed: {e}", exc_info=True)

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
