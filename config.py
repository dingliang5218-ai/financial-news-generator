import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

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

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY is required")
        if not cls.RSS_FEEDS or cls.RSS_FEEDS == [""]:
            raise ValueError("RSS_FEEDS is required")
        return True
