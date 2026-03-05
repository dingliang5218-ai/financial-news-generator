import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from config import Config
from logger import Logger
from error_handler import retry_with_backoff, RetryableError, FatalError

logger = Logger.get_logger("storage")


class Storage:
    """Database storage layer"""

    def __init__(self):
        self.db_path = Config.DB_PATH
        self._ensure_data_dir()
        self._init_database()

    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        Path(Config.DATA_DIR).mkdir(parents=True, exist_ok=True)
        Path(Config.BACKUP_DIR).mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Initialize database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Articles table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        source_url TEXT,
                        importance INTEGER,
                        news_type TEXT,
                        word_count INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Raw news table for deduplication
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS raw_news (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        url TEXT UNIQUE,
                        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Data source status table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS data_source_status (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_name TEXT UNIQUE NOT NULL,
                        consecutive_failures INTEGER DEFAULT 0,
                        last_success TIMESTAMP,
                        last_failure TIMESTAMP,
                        is_active INTEGER DEFAULT 1
                    )
                """)

                conn.commit()
                logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.critical(f"Failed to initialize database: {e}")
            raise FatalError(f"Database initialization failed: {e}")

    @retry_with_backoff()
    def save_article(self, article: Dict) -> int:
        """Save generated article"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO articles (title, content, source_url, importance, news_type, word_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        article["title"],
                        article["content"],
                        article.get("source_url"),
                        article.get("importance"),
                        article.get("news_type"),
                        article.get("word_count"),
                    ),
                )
                conn.commit()
                article_id = cursor.lastrowid
                logger.info(f"Saved article: {article['title']} (ID: {article_id})")
                return article_id
        except sqlite3.Error as e:
            logger.error(f"Failed to save article: {e}")
            self._backup_to_json(article)
            raise RetryableError(f"Database write failed: {e}")

    def _backup_to_json(self, article: Dict):
        """Backup article to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_file = f"{Config.BACKUP_DIR}/articles-{timestamp}.json"
        try:
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(article, f, ensure_ascii=False, indent=2)
            logger.warning(f"Article backed up to: {backup_file}")
        except Exception as e:
            logger.error(f"Failed to backup article: {e}")

    def is_news_processed(self, url: str) -> bool:
        """Check if news URL has been processed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM raw_news WHERE url = ?", (url,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logger.error(f"Failed to check news URL: {e}")
            return False

    def mark_news_processed(self, title: str, url: str):
        """Mark news as processed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO raw_news (title, url)
                    VALUES (?, ?)
                """,
                    (title, url),
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to mark news as processed: {e}")

    def update_source_status(self, source_name: str, success: bool):
        """Update data source status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if success:
                    cursor.execute(
                        """
                        INSERT INTO data_source_status (source_name, consecutive_failures, last_success)
                        VALUES (?, 0, ?)
                        ON CONFLICT(source_name) DO UPDATE SET
                            consecutive_failures = 0,
                            last_success = ?,
                            is_active = 1
                    """,
                        (source_name, datetime.now(), datetime.now()),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO data_source_status (source_name, consecutive_failures, last_failure)
                        VALUES (?, 1, ?)
                        ON CONFLICT(source_name) DO UPDATE SET
                            consecutive_failures = consecutive_failures + 1,
                            last_failure = ?
                    """,
                        (source_name, datetime.now(), datetime.now()),
                    )

                    # Mark as inactive if too many failures
                    cursor.execute(
                        """
                        UPDATE data_source_status
                        SET is_active = 0
                        WHERE source_name = ? AND consecutive_failures >= 3
                    """,
                        (source_name,),
                    )

                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to update source status: {e}")

    def get_active_sources(self) -> List[str]:
        """Get list of active data sources"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT source_name FROM data_source_status
                    WHERE is_active = 1
                """)
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get active sources: {e}")
            return []

    def get_article(self, article_id: int) -> Optional[Dict]:
        """Get article by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Failed to get article: {e}")
            return None

    def get_recent_articles(self, limit: int = 10) -> List[Dict]:
        """Get recent articles"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM articles
                    ORDER BY created_at DESC
                    LIMIT ?
                """,
                    (limit,),
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get articles: {e}")
            return []

    def search_articles(self, query: str) -> List[Dict]:
        """Search articles by title or content"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM articles
                    WHERE title LIKE ? OR content LIKE ?
                    ORDER BY created_at DESC
                    LIMIT 50
                """,
                    (f"%{query}%", f"%{query}%"),
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to search articles: {e}")
            return []

    def get_articles_by_date_range(self, days: int = 7) -> List[Dict]:
        """Get articles from the last N days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM articles
                    WHERE created_at >= datetime('now', '-' || ? || ' days')
                    ORDER BY created_at DESC
                """,
                    (days,),
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get articles by date range: {e}")
            return []
