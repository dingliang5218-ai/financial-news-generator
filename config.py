import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # Version
    VERSION = "1.0.0"

    # Claude API
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

    # RSS Feeds
    RSS_FEEDS = [feed.strip() for feed in os.getenv("RSS_FEEDS", "").split(",") if feed.strip()]
    MAX_NEWS_PER_SOURCE = int(os.getenv("MAX_NEWS_PER_SOURCE") or "20")

    # Generation Parameters
    IMPORTANCE_THRESHOLD = int(os.getenv("IMPORTANCE_THRESHOLD") or "3")
    QUICK_NEWS_MIN_LENGTH = int(os.getenv("QUICK_NEWS_MIN_LENGTH") or "500")
    QUICK_NEWS_MAX_LENGTH = int(os.getenv("QUICK_NEWS_MAX_LENGTH") or "800")
    DEEP_ANALYSIS_MIN_LENGTH = int(os.getenv("DEEP_ANALYSIS_MIN_LENGTH") or "1500")
    DEEP_ANALYSIS_MAX_LENGTH = int(os.getenv("DEEP_ANALYSIS_MAX_LENGTH") or "2500")

    # Scheduler
    FETCH_INTERVAL_MINUTES = int(os.getenv("FETCH_INTERVAL_MINUTES") or "30")

    # Retry Configuration
    MAX_RETRIES = int(os.getenv("MAX_RETRIES") or "3")
    RETRY_DELAY_BASE = int(os.getenv("RETRY_DELAY_BASE") or "2")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS") or "30")

    # Paths
    DATA_DIR = "data"
    LOGS_DIR = "logs"
    BACKUP_DIR = "data/backups"
    DB_PATH = "data/articles.db"

    # Aggregation configuration
    AGGREGATION_ENABLED = os.getenv("AGGREGATION_ENABLED", "true").lower() == "true"
    MIN_SIMILARITY_SCORE = float(os.getenv("MIN_SIMILARITY_SCORE", "0.7"))

    # Ranking configuration
    IMPORTANCE_WEIGHT = float(os.getenv("IMPORTANCE_WEIGHT", "0.6"))
    HOTNESS_WEIGHT = float(os.getenv("HOTNESS_WEIGHT", "0.3"))
    TIMELINESS_WEIGHT = float(os.getenv("TIMELINESS_WEIGHT", "0.1"))
    TOP_N_NEWS = int(os.getenv("TOP_N_NEWS", "3"))

    # Impact analysis configuration
    IMPACT_DIMENSIONS = [
        'global_economy',
        'us_economy',
        'china_economy',
        'us_stock',
        'china_stock',
        'other_markets'
    ]

    # Content generation configuration
    DAILY_SUMMARY_ENABLED = os.getenv("DAILY_SUMMARY_ENABLED", "true").lower() == "true"
    DAILY_SUMMARY_MIN_LENGTH = int(os.getenv("DAILY_SUMMARY_MIN_LENGTH", "1500"))
    DAILY_SUMMARY_MAX_LENGTH = int(os.getenv("DAILY_SUMMARY_MAX_LENGTH", "2000"))

    DEEP_ANALYSIS_ENABLED = os.getenv("DEEP_ANALYSIS_ENABLED", "true").lower() == "true"
    DEEP_ANALYSIS_IMPORTANCE_THRESHOLD = int(os.getenv("DEEP_ANALYSIS_IMPORTANCE_THRESHOLD", "4"))
    DEEP_ANALYSIS_HOTNESS_THRESHOLD = int(os.getenv("DEEP_ANALYSIS_HOTNESS_THRESHOLD", "3"))

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY is required")
        if not cls.RSS_FEEDS or cls.RSS_FEEDS == [""]:
            raise ValueError("RSS_FEEDS is required")
        return True
