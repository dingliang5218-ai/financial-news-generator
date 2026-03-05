import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # Claude API
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

    # RSS Feeds
    RSS_FEEDS = os.getenv("RSS_FEEDS", "").split(",")

    # Generation Parameters
    IMPORTANCE_THRESHOLD = int(os.getenv("IMPORTANCE_THRESHOLD", "3"))
    QUICK_NEWS_MIN_LENGTH = int(os.getenv("QUICK_NEWS_MIN_LENGTH", "500"))
    QUICK_NEWS_MAX_LENGTH = int(os.getenv("QUICK_NEWS_MAX_LENGTH", "800"))
    DEEP_ANALYSIS_MIN_LENGTH = int(os.getenv("DEEP_ANALYSIS_MIN_LENGTH", "1500"))
    DEEP_ANALYSIS_MAX_LENGTH = int(os.getenv("DEEP_ANALYSIS_MAX_LENGTH", "2500"))

    # Scheduler
    FETCH_INTERVAL_MINUTES = int(os.getenv("FETCH_INTERVAL_MINUTES", "30"))

    # Retry Configuration
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY_BASE = int(os.getenv("RETRY_DELAY_BASE", "2"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))

    # Paths
    DATA_DIR = "data"
    LOGS_DIR = "logs"
    BACKUP_DIR = "data/backup"
    DB_PATH = "data/articles.db"

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY is required")
        if not cls.RSS_FEEDS or cls.RSS_FEEDS == [""]:
            raise ValueError("RSS_FEEDS is required")
        return True
