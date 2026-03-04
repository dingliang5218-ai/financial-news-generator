# 财经内容自动生成系统 - 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现一个轻量级的自动化财经内容生成系统，从美国财经新闻源采集数据，使用 Claude 进行智能分析和内容生成，输出面向中文读者的高质量财经文章。

**Architecture:** 采用模块化的四层架构（数据采集→智能分析→内容生成→存储），每层职责单一。使用 Python 3.10+ 实现，SQLite 存储数据，APScheduler 管理定时任务。完整的错误处理和日志系统确保系统稳定运行。

**Tech Stack:** Python 3.10+, feedparser, anthropic, APScheduler, SQLite, requests

---

## Task 1: 项目初始化和配置管理

**Files:**
- Create: `config.py`
- Create: `.env.example`
- Create: `requirements.txt`
- Create: `.gitignore`

**Step 1: 创建 requirements.txt**

```txt
feedparser==6.0.10
anthropic==0.18.1
APScheduler==3.10.4
requests==2.31.0
python-dotenv==1.0.0
```

**Step 2: 创建 .env.example**

```env
# Claude API Configuration
CLAUDE_API_KEY=your_api_key_here

# RSS Feed URLs (comma-separated)
RSS_FEEDS=https://feeds.cnbc.com/news/,https://feeds.bloomberg.com/markets/news.rss,https://www.reuters.com/rssFeed/businessNews,https://www.marketwatch.com/rss/topstories

# Generation Parameters
IMPORTANCE_THRESHOLD=3
QUICK_NEWS_MIN_LENGTH=500
QUICK_NEWS_MAX_LENGTH=800
DEEP_ANALYSIS_MIN_LENGTH=1500
DEEP_ANALYSIS_MAX_LENGTH=2500

# Scheduler Configuration
FETCH_INTERVAL_MINUTES=30

# Retry Configuration
MAX_RETRIES=3
RETRY_DELAY_BASE=2

# Logging Configuration
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30
```

**Step 3: 创建 config.py**

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # Claude API
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

    # RSS Feeds
    RSS_FEEDS = os.getenv('RSS_FEEDS', '').split(',')

    # Generation Parameters
    IMPORTANCE_THRESHOLD = int(os.getenv('IMPORTANCE_THRESHOLD', '3'))
    QUICK_NEWS_MIN_LENGTH = int(os.getenv('QUICK_NEWS_MIN_LENGTH', '500'))
    QUICK_NEWS_MAX_LENGTH = int(os.getenv('QUICK_NEWS_MAX_LENGTH', '800'))
    DEEP_ANALYSIS_MIN_LENGTH = int(os.getenv('DEEP_ANALYSIS_MIN_LENGTH', '1500'))
    DEEP_ANALYSIS_MAX_LENGTH = int(os.getenv('DEEP_ANALYSIS_MAX_LENGTH', '2500'))

    # Scheduler
    FETCH_INTERVAL_MINUTES = int(os.getenv('FETCH_INTERVAL_MINUTES', '30'))

    # Retry Configuration
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY_BASE = int(os.getenv('RETRY_DELAY_BASE', '2'))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', '30'))

    # Paths
    DATA_DIR = 'data'
    LOGS_DIR = 'logs'
    BACKUP_DIR = 'data/backup'
    DB_PATH = 'data/articles.db'

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY is required")
        if not cls.RSS_FEEDS or cls.RSS_FEEDS == ['']:
            raise ValueError("RSS_FEEDS is required")
        return True
```

**Step 4: 更新 .gitignore**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment variables
.env

# Database
*.db
*.sqlite
*.sqlite3
data/

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.bak

# Images (reference materials)
*.jpg
*.png
*.jpeg
*.gif

# Reference materials
financial/
```

**Step 5: 创建目录结构**

Run: `mkdir -p data/backup data/backups logs`
Expected: 目录创建成功

**Step 6: 提交**

```bash
git add config.py .env.example requirements.txt .gitignore
git commit -m "feat: add project configuration and dependencies

- Add config.py with environment variable support
- Add .env.example template
- Add requirements.txt with core dependencies
- Update .gitignore for Python project

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: 错误处理和日志系统

**Files:**
- Create: `error_handler.py`
- Create: `logger.py`

**Step 1: 创建 logger.py**

```python
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from config import Config

class Logger:
    """Centralized logging system"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name):
        """Get or create a logger"""
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))

        # Create logs directory if not exists
        Path(Config.LOGS_DIR).mkdir(parents=True, exist_ok=True)

        # Main log file
        today = datetime.now().strftime('%Y-%m-%d')
        main_handler = logging.FileHandler(
            f'{Config.LOGS_DIR}/financial-news-{today}.log',
            encoding='utf-8'
        )
        main_handler.setLevel(logging.DEBUG)

        # Error log file
        error_handler = logging.FileHandler(
            f'{Config.LOGS_DIR}/errors-{today}.log',
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        main_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(main_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def cleanup_old_logs(cls):
        """Remove logs older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=Config.LOG_RETENTION_DAYS)
        logs_dir = Path(Config.LOGS_DIR)

        if not logs_dir.exists():
            return

        for log_file in logs_dir.glob('*.log'):
            try:
                # Extract date from filename
                date_str = log_file.stem.split('-')[-3:]
                if len(date_str) == 3:
                    file_date = datetime.strptime('-'.join(date_str), '%Y-%m-%d')
                    if file_date < cutoff_date:
                        log_file.unlink()
                        print(f"Deleted old log: {log_file}")
            except (ValueError, IndexError):
                continue
```

**Step 2: 创建 error_handler.py**

```python
import time
from functools import wraps
from config import Config
from logger import Logger

logger = Logger.get_logger('error_handler')

class ErrorType:
    """Error classification"""
    RECOVERABLE = 'recoverable'
    DEGRADABLE = 'degradable'
    FATAL = 'fatal'

class RetryableError(Exception):
    """Error that can be retried"""
    pass

class DegradableError(Exception):
    """Error that allows degraded operation"""
    pass

class FatalError(Exception):
    """Fatal error that requires shutdown"""
    pass

def retry_with_backoff(max_retries=None, base_delay=None):
    """Decorator for exponential backoff retry"""
    if max_retries is None:
        max_retries = Config.MAX_RETRIES
    if base_delay is None:
        base_delay = Config.RETRY_DELAY_BASE

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except RetryableError as e:
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} failed after {max_retries} retries: {e}")
                        raise

                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}), "
                        f"retrying in {delay}s: {e}"
                    )
                    time.sleep(delay)
                except (DegradableError, FatalError):
                    raise
                except Exception as e:
                    logger.error(f"{func.__name__} encountered unexpected error: {e}")
                    raise

        return wrapper
    return decorator

def handle_errors(error_type=ErrorType.RECOVERABLE):
    """Decorator for error handling"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RetryableError as e:
                logger.warning(f"Recoverable error in {func.__name__}: {e}")
                if error_type == ErrorType.RECOVERABLE:
                    return None
                raise
            except DegradableError as e:
                logger.error(f"Degradable error in {func.__name__}: {e}")
                if error_type == ErrorType.DEGRADABLE:
                    return None
                raise
            except FatalError as e:
                logger.critical(f"Fatal error in {func.__name__}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                raise

        return wrapper
    return decorator
```

**Step 3: 提交**

```bash
git add error_handler.py logger.py
git commit -m "feat: add error handling and logging system

- Add Logger class with file rotation and multiple handlers
- Add error classification (Recoverable/Degradable/Fatal)
- Add retry decorator with exponential backoff
- Add error handling decorator

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: 数据存储层

**Files:**
- Create: `storage.py`

**Step 1: 创建 storage.py**

```python
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from config import Config
from logger import Logger
from error_handler import retry_with_backoff, RetryableError, FatalError

logger = Logger.get_logger('storage')

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
                cursor.execute('''
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
                ''')

                # Raw news table for deduplication
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS raw_news (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        url TEXT UNIQUE,
                        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Data source status table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS data_source_status (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_name TEXT UNIQUE NOT NULL,
                        consecutive_failures INTEGER DEFAULT 0,
                        last_success TIMESTAMP,
                        last_failure TIMESTAMP,
                        is_active INTEGER DEFAULT 1
                    )
                ''')

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
                cursor.execute('''
                    INSERT INTO articles (title, content, source_url, importance, news_type, word_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    article['title'],
                    article['content'],
                    article.get('source_url'),
                    article.get('importance'),
                    article.get('news_type'),
                    article.get('word_count')
                ))
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
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_file = f"{Config.BACKUP_DIR}/articles-{timestamp}.json"
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(article, f, ensure_ascii=False, indent=2)
            logger.warning(f"Article backed up to: {backup_file}")
        except Exception as e:
            logger.error(f"Failed to backup article: {e}")

    def is_news_processed(self, url: str) -> bool:
        """Check if news URL has been processed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM raw_news WHERE url = ?', (url,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logger.error(f"Failed to check news URL: {e}")
            return False

    def mark_news_processed(self, title: str, url: str):
        """Mark news as processed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO raw_news (title, url)
                    VALUES (?, ?)
                ''', (title, url))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to mark news as processed: {e}")

    def update_source_status(self, source_name: str, success: bool):
        """Update data source status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if success:
                    cursor.execute('''
                        INSERT INTO data_source_status (source_name, consecutive_failures, last_success)
                        VALUES (?, 0, ?)
                        ON CONFLICT(source_name) DO UPDATE SET
                            consecutive_failures = 0,
                            last_success = ?,
                            is_active = 1
                    ''', (source_name, datetime.now(), datetime.now()))
                else:
                    cursor.execute('''
                        INSERT INTO data_source_status (source_name, consecutive_failures, last_failure)
                        VALUES (?, 1, ?)
                        ON CONFLICT(source_name) DO UPDATE SET
                            consecutive_failures = consecutive_failures + 1,
                            last_failure = ?
                    ''', (source_name, datetime.now(), datetime.now()))

                    # Mark as inactive if too many failures
                    cursor.execute('''
                        UPDATE data_source_status
                        SET is_active = 0
                        WHERE source_name = ? AND consecutive_failures >= 3
                    ''', (source_name,))

                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to update source status: {e}")

    def get_active_sources(self) -> List[str]:
        """Get list of active data sources"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT source_name FROM data_source_status
                    WHERE is_active = 1
                ''')
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get active sources: {e}")
            return []

    def get_articles(self, limit: int = 10) -> List[Dict]:
        """Get recent articles"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM articles
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get articles: {e}")
            return []
```

**Step 2: 提交**

```bash
git add storage.py
git commit -m "feat: add database storage layer

- Add Storage class with SQLite operations
- Add articles, raw_news, and data_source_status tables
- Add retry mechanism for database operations
- Add JSON backup for failed writes
- Add source status tracking

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: 数据采集层

**Files:**
- Create: `data_fetcher.py`

**Step 1: 创建 data_fetcher.py**

```python
import feedparser
import requests
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from config import Config
from logger import Logger
from error_handler import retry_with_backoff, RetryableError, DegradableError
from storage import Storage

logger = Logger.get_logger('data_fetcher')

class NewsItem:
    """News item data structure"""
    def __init__(self, title: str, content: str, url: str, published: str, source: str):
        self.title = title
        self.content = content
        self.url = url
        self.published = published
        self.source = source

    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'published': self.published,
            'source': self.source
        }

class DataSource(ABC):
    """Abstract base class for data sources"""

    def __init__(self, name: str):
        self.name = name
        self.storage = Storage()

    @abstractmethod
    def fetch(self) -> List[NewsItem]:
        """Fetch news from source"""
        pass

    def _update_status(self, success: bool):
        """Update source status in database"""
        self.storage.update_source_status(self.name, success)

class RSSSource(DataSource):
    """RSS feed data source"""

    def __init__(self, name: str, feed_url: str):
        super().__init__(name)
        self.feed_url = feed_url

    @retry_with_backoff()
    def fetch(self) -> List[NewsItem]:
        """Fetch news from RSS feed"""
        try:
            logger.info(f"Fetching from {self.name}: {self.feed_url}")

            # Parse RSS feed
            feed = feedparser.parse(self.feed_url)

            if feed.bozo:
                raise RetryableError(f"Failed to parse RSS feed: {feed.bozo_exception}")

            news_items = []
            for entry in feed.entries[:20]:  # Limit to 20 most recent
                # Skip if already processed
                if self.storage.is_news_processed(entry.link):
                    continue

                news_item = NewsItem(
                    title=entry.get('title', ''),
                    content=entry.get('summary', entry.get('description', '')),
                    url=entry.get('link', ''),
                    published=entry.get('published', ''),
                    source=self.name
                )
                news_items.append(news_item)

            logger.info(f"Fetched {len(news_items)} new items from {self.name}")
            self._update_status(True)
            return news_items

        except RetryableError:
            self._update_status(False)
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching from {self.name}: {e}")
            self._update_status(False)
            raise DegradableError(f"Failed to fetch from {self.name}: {e}")

class DataFetcher:
    """Main data fetcher coordinating all sources"""

    def __init__(self):
        self.storage = Storage()
        self.sources = self._init_sources()

    def _init_sources(self) -> List[DataSource]:
        """Initialize data sources from configuration"""
        sources = []
        for i, feed_url in enumerate(Config.RSS_FEEDS):
            if feed_url.strip():
                source_name = f"RSS-{i+1}"
                sources.append(RSSSource(source_name, feed_url.strip()))

        logger.info(f"Initialized {len(sources)} data sources")
        return sources

    def fetch_all(self) -> List[NewsItem]:
        """Fetch from all active sources"""
        all_news = []
        successful_sources = 0

        for source in self.sources:
            try:
                news_items = source.fetch()
                all_news.extend(news_items)
                successful_sources += 1
            except DegradableError as e:
                logger.warning(f"Skipping source {source.name}: {e}")
                continue
            except Exception as e:
                logger.error(f"Failed to fetch from {source.name}: {e}")
                continue

        # Check if we have enough active sources
        if successful_sources < 2:
            logger.error(f"Only {successful_sources} sources available, minimum is 2")
            if successful_sources == 0:
                raise DegradableError("All data sources failed")

        logger.info(f"Total fetched: {len(all_news)} news items from {successful_sources} sources")
        return all_news

    def deduplicate(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Remove duplicate news items"""
        seen_urls = set()
        unique_items = []

        for item in news_items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)

        logger.info(f"Deduplicated: {len(news_items)} -> {len(unique_items)} items")
        return unique_items
```

**Step 2: 提交**

```bash
git add data_fetcher.py
git commit -m "feat: add data fetching layer

- Add NewsItem data structure
- Add DataSource abstract base class
- Add RSSSource implementation
- Add DataFetcher coordinator
- Add deduplication logic
- Add source status tracking

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: 智能分析层

**Files:**
- Create: `analyzer.py`

**Step 1: 创建 analyzer.py**

```python
import json
from typing import Dict, Optional
from anthropic import Anthropic
from config import Config
from logger import Logger
from error_handler import retry_with_backoff, RetryableError, DegradableError
from data_fetcher import NewsItem

logger = Logger.get_logger('analyzer')

class NewsAnalysis:
    """News analysis result"""
    def __init__(self, importance: int, news_type: str, is_breaking: bool, summary: str):
        self.importance = importance
        self.news_type = news_type
        self.is_breaking = is_breaking
        self.summary = summary

    def to_dict(self) -> Dict:
        return {
            'importance': self.importance,
            'news_type': self.news_type,
            'is_breaking': self.is_breaking,
            'summary': self.summary
        }

class NewsAnalyzer:
    """Intelligent news analyzer using Claude"""

    def __init__(self):
        self.client = Anthropic(api_key=Config.CLAUDE_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    @retry_with_backoff()
    def analyze(self, news_item: NewsItem) -> Optional[NewsAnalysis]:
        """Analyze news importance and classification"""
        try:
            prompt = f"""分析这条美国财经新闻的重要性：

标题：{news_item.title}
内容：{news_item.content}

请判断：
1. 重要性等级（1-5分，5分最重要）
2. 新闻类型（市场行情/公司财报/政策变化/经济数据/其他）
3. 是否为突发重大事件（true/false）
4. 关键信息摘要（1-2句话）

以 JSON 格式返回，格式如下：
{{
  "importance": 3,
  "news_type": "市场行情",
  "is_breaking": false,
  "summary": "关键信息摘要"
}}"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            content = response.content[0].text
            result = json.loads(content)

            analysis = NewsAnalysis(
                importance=result['importance'],
                news_type=result['news_type'],
                is_breaking=result['is_breaking'],
                summary=result['summary']
            )

            logger.info(
                f"Analyzed: {news_item.title[:50]}... "
                f"(importance: {analysis.importance}, type: {analysis.news_type})"
            )

            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response: {e}\nResponse: {content}")
            raise DegradableError(f"Invalid response format: {e}")
        except Exception as e:
            if "rate_limit" in str(e).lower():
                logger.warning("Claude API rate limit reached, will retry")
                raise RetryableError(f"Rate limit: {e}")
            else:
                logger.error(f"Failed to analyze news: {e}")
                raise DegradableError(f"Analysis failed: {e}")

    def should_generate_article(self, analysis: NewsAnalysis) -> bool:
        """Determine if article should be generated"""
        return analysis.importance >= Config.IMPORTANCE_THRESHOLD
```

**Step 2: 提交**

```bash
git add analyzer.py
git commit -m "feat: add intelligent news analyzer

- Add NewsAnalysis data structure
- Add NewsAnalyzer using Claude API
- Add importance scoring and classification
- Add rate limit handling
- Add article generation decision logic

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: 内容生成层

**Files:**
- Create: `generator.py`

**Step 1: 创建 generator.py**

```python
from typing import Dict
from anthropic import Anthropic
from config import Config
from logger import Logger
from error_handler import retry_with_backoff, RetryableError, DegradableError
from data_fetcher import NewsItem
from analyzer import NewsAnalysis

logger = Logger.get_logger('generator')

class ContentGenerator:
    """Content generator using Claude"""

    def __init__(self):
        self.client = Anthropic(api_key=Config.CLAUDE_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    @retry_with_backoff()
    def generate(self, news_item: NewsItem, analysis: NewsAnalysis) -> Dict:
        """Generate article based on importance"""
        if analysis.importance >= 4:
            return self._generate_deep_analysis(news_item, analysis)
        else:
            return self._generate_quick_news(news_item, analysis)

    def _generate_quick_news(self, news_item: NewsItem, analysis: NewsAnalysis) -> Dict:
        """Generate quick news article (500-800 words)"""
        try:
            prompt = f"""将这条美国财经新闻改写成中文快讯：

原文标题：{news_item.title}
原文内容：{news_item.content}
关键信息：{analysis.summary}
新闻类型：{analysis.news_type}

要求：
- 字数：{Config.QUICK_NEWS_MIN_LENGTH}-{Config.QUICK_NEWS_MAX_LENGTH}字
- 翻译准确，语言流畅
- 保留关键数据和事实
- 简要解读对市场的影响
- 面向中文读者，通俗易懂
- 不要使用 markdown 格式

文章结构：
1. 事件概述（200字）
2. 市场影响分析（300-600字）

请直接输出文章内容，不要包含标题。"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text.strip()
            word_count = len(content)

            logger.info(f"Generated quick news: {news_item.title[:50]}... ({word_count} chars)")

            return {
                'title': news_item.title,
                'content': content,
                'source_url': news_item.url,
                'importance': analysis.importance,
                'news_type': analysis.news_type,
                'word_count': word_count
            }

        except Exception as e:
            if "rate_limit" in str(e).lower():
                logger.warning("Claude API rate limit reached")
                raise RetryableError(f"Rate limit: {e}")
            else:
                logger.error(f"Failed to generate quick news: {e}")
                raise DegradableError(f"Generation failed: {e}")

    def _generate_deep_analysis(self, news_item: NewsItem, analysis: NewsAnalysis) -> Dict:
        """Generate deep analysis article (1500-2500 words)"""
        try:
            prompt = f"""针对这条重大财经新闻，撰写深度分析文章：

原文标题：{news_item.title}
原文内容：{news_item.content}
关键信息：{analysis.summary}
新闻类型：{analysis.news_type}

文章结构：
1. 事件概述（200字）- 简明扼要说明发生了什么
2. 背景分析（400字）- 事件的来龙去脉、历史背景
3. 市场影响（600字）- 对各个市场、行业、资产类别的影响分析
4. 未来展望（300字）- 可能的后续发展和投资者应关注的要点

要求：
- 总字数：{Config.DEEP_ANALYSIS_MIN_LENGTH}-{Config.DEEP_ANALYSIS_MAX_LENGTH}字
- 专业但通俗，避免过度专业术语
- 数据支撑观点，引用具体数字
- 多角度分析，客观中立
- 面向中文读者
- 不要使用 markdown 格式

请直接输出文章内容，不要包含标题。"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text.strip()
            word_count = len(content)

            logger.info(f"Generated deep analysis: {news_item.title[:50]}... ({word_count} chars)")

            return {
                'title': news_item.title,
                'content': content,
                'source_url': news_item.url,
                'importance': analysis.importance,
                'news_type': analysis.news_type,
                'word_count': word_count
            }

        except Exception as e:
            if "rate_limit" in str(e).lower():
                logger.warning("Claude API rate limit reached")
                raise RetryableError(f"Rate limit: {e}")
            else:
                logger.error(f"Failed to generate deep analysis: {e}")
                raise DegradableError(f"Generation failed: {e}")
```

**Step 2: 提交**

```bash
git add generator.py
git commit -m "feat: add content generator

- Add ContentGenerator using Claude API
- Add quick news generation (500-800 words)
- Add deep analysis generation (1500-2500 words)
- Add rate limit handling
- Add word count tracking

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: 健康检查系统

**Files:**
- Create: `health_check.py`

**Step 1: 创建 health_check.py**

```python
import os
import shutil
from pathlib import Path
from anthropic import Anthropic
from config import Config
from logger import Logger
from error_handler import FatalError

logger = Logger.get_logger('health_check')

class HealthCheck:
    """System health check"""

    @staticmethod
    def startup_check():
        """Comprehensive startup health check"""
        logger.info("Starting system health check...")

        checks = {
            'config': HealthCheck._check_config(),
            'dependencies': HealthCheck._check_dependencies(),
            'storage': HealthCheck._check_storage(),
            'api': HealthCheck._check_api_connection()
        }

        failed_checks = [name for name, passed in checks.items() if not passed]

        if failed_checks:
            error_msg = f"Health check failed: {', '.join(failed_checks)}"
            logger.critical(error_msg)
            raise FatalError(error_msg)

        logger.info("All health checks passed ✓")
        return True

    @staticmethod
    def _check_config():
        """Check configuration"""
        try:
            Config.validate()
            logger.info("✓ Configuration valid")
            return True
        except Exception as e:
            logger.error(f"✗ Configuration check failed: {e}")
            return False

    @staticmethod
    def _check_dependencies():
        """Check required dependencies"""
        try:
            import feedparser
            import anthropic
            import apscheduler
            logger.info("✓ All dependencies installed")
            return True
        except ImportError as e:
            logger.error(f"✗ Missing dependency: {e}")
            return False

    @staticmethod
    def _check_storage():
        """Check storage directories and permissions"""
        try:
            # Check data directory
            Path(Config.DATA_DIR).mkdir(parents=True, exist_ok=True)
            Path(Config.BACKUP_DIR).mkdir(parents=True, exist_ok=True)
            Path(Config.LOGS_DIR).mkdir(parents=True, exist_ok=True)

            # Check write permissions
            test_file = Path(Config.DATA_DIR) / '.write_test'
            test_file.write_text('test')
            test_file.unlink()

            # Check disk space (at least 100MB)
            stat = shutil.disk_usage(Config.DATA_DIR)
            free_mb = stat.free / (1024 * 1024)
            if free_mb < 100:
                logger.warning(f"Low disk space: {free_mb:.1f}MB free")

            logger.info(f"✓ Storage check passed ({free_mb:.1f}MB free)")
            return True
        except Exception as e:
            logger.error(f"✗ Storage check failed: {e}")
            return False

    @staticmethod
    def _check_api_connection():
        """Test Claude API connection"""
        try:
            client = Anthropic(api_key=Config.CLAUDE_API_KEY)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            logger.info("✓ Claude API connection successful")
            return True
        except Exception as e:
            logger.error(f"✗ Claude API connection failed: {e}")
            return False

    @staticmethod
    def runtime_check():
        """Runtime health check before each task"""
        checks = {
            'disk_space': HealthCheck._check_disk_space(),
            'database': HealthCheck._check_database()
        }

        failed = [name for name, passed in checks.items() if not passed]
        if failed:
            logger.warning(f"Runtime health issues: {', '.join(failed)}")

        return all(checks.values())

    @staticmethod
    def _check_disk_space():
        """Check available disk space"""
        try:
            stat = shutil.disk_usage(Config.DATA_DIR)
            free_mb = stat.free / (1024 * 1024)
            if free_mb < 50:
                logger.error(f"Critical: Low disk space ({free_mb:.1f}MB)")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to check disk space: {e}")
            return False

    @staticmethod
    def _check_database():
        """Check database connection"""
        try:
            import sqlite3
            with sqlite3.connect(Config.DB_PATH) as conn:
                conn.execute('SELECT 1')
            return True
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            return False
```

**Step 2: 提交**

```bash
git add health_check.py
git commit -m "feat: add health check system

- Add startup health check (config, dependencies, storage, API)
- Add runtime health check (disk space, database)
- Add disk space monitoring
- Add API connection test

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: 主调度器和命令行工具

**Files:**
- Create: `scheduler.py`
- Create: `cli.py`
- Create: `main.py`

**Step 1: 创建 scheduler.py**

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config import Config
from logger import Logger
from health_check import HealthCheck
from data_fetcher import DataFetcher
from analyzer import NewsAnalyzer
from generator import ContentGenerator
from storage import Storage
from error_handler import DegradableError

logger = Logger.get_logger('scheduler')

class NewsScheduler:
    """Main scheduler for news processing"""

    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.data_fetcher = DataFetcher()
        self.analyzer = NewsAnalyzer()
        self.generator = ContentGenerator()
        self.storage = Storage()

    def main_job(self):
        """Main task: fetch → analyze → generate → store"""
        logger.info("=" * 60)
        logger.info("Starting news processing job")
        logger.info("=" * 60)

        try:
            # Runtime health check
            if not HealthCheck.runtime_check():
                logger.warning("Runtime health check failed, but continuing...")

            # 1. Fetch data
            logger.info("Step 1: Fetching news...")
            news_list = self.data_fetcher.fetch_all()
            news_list = self.data_fetcher.deduplicate(news_list)

            if not news_list:
                logger.info("No new news to process")
                return

            # 2. Analyze news
            logger.info(f"Step 2: Analyzing {len(news_list)} news items...")
            analyzed_news = []
            for news_item in news_list:
                try:
                    analysis = self.analyzer.analyze(news_item)
                    if analysis and self.analyzer.should_generate_article(analysis):
                        analyzed_news.append((news_item, analysis))
                        # Mark as processed
                        self.storage.mark_news_processed(news_item.title, news_item.url)
                except DegradableError as e:
                    logger.warning(f"Skipping news analysis: {e}")
                    continue

            logger.info(f"Found {len(analyzed_news)} news items worth generating")

            # 3. Generate articles
            logger.info("Step 3: Generating articles...")
            generated_count = 0
            for news_item, analysis in analyzed_news:
                try:
                    article = self.generator.generate(news_item, analysis)
                    article_id = self.storage.save_article(article)
                    generated_count += 1
                    logger.info(f"Generated article #{article_id}: {article['title'][:50]}...")
                except DegradableError as e:
                    logger.warning(f"Skipping article generation: {e}")
                    continue

            logger.info(f"Successfully generated {generated_count} articles")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Job failed with error: {e}", exc_info=True)

    def start(self):
        """Start the scheduler"""
        logger.info(f"Starting scheduler (interval: {Config.FETCH_INTERVAL_MINUTES} minutes)")

        # Add main job
        self.scheduler.add_job(
            self.main_job,
            trigger=IntervalTrigger(minutes=Config.FETCH_INTERVAL_MINUTES),
            id='main_job',
            name='News processing job',
            replace_existing=True
        )

        # Run immediately on start
        self.main_job()

        # Start scheduler
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped by user")
            self.scheduler.shutdown()
```

**Step 2: 创建 cli.py**

```python
import sys
from pathlib import Path
from storage import Storage
from logger import Logger

logger = Logger.get_logger('cli')

class CLI:
    """Command-line interface"""

    def __init__(self):
        self.storage = Storage()

    def list_articles(self, limit=10):
        """List recent articles"""
        articles = self.storage.get_articles(limit)

        if not articles:
            print("No articles found")
            return

        print(f"\n{'='*80}")
        print(f"Recent Articles (showing {len(articles)})")
        print(f"{'='*80}\n")

        for article in articles:
            print(f"ID: {article['id']}")
            print(f"Title: {article['title']}")
            print(f"Type: {article['news_type']} | Importance: {article['importance']}")
            print(f"Words: {article['word_count']} | Created: {article['created_at']}")
            print(f"URL: {article['source_url']}")
            print(f"{'-'*80}\n")

    def show_article(self, article_id):
        """Show full article content"""
        articles = self.storage.get_articles(limit=1000)
        article = next((a for a in articles if a['id'] == article_id), None)

        if not article:
            print(f"Article {article_id} not found")
            return

        print(f"\n{'='*80}")
        print(f"Article #{article['id']}")
        print(f"{'='*80}\n")
        print(f"Title: {article['title']}\n")
        print(f"Type: {article['news_type']} | Importance: {article['importance']}")
        print(f"Words: {article['word_count']} | Created: {article['created_at']}")
        print(f"Source: {article['source_url']}\n")
        print(f"{'-'*80}\n")
        print(article['content'])
        print(f"\n{'='*80}\n")

    def export_article(self, article_id, output_file):
        """Export article to file"""
        articles = self.storage.get_articles(limit=1000)
        article = next((a for a in articles if a['id'] == article_id), None)

        if not article:
            print(f"Article {article_id} not found")
            return

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# {article['title']}\n\n")
                f.write(f"**类型**: {article['news_type']} | **重要性**: {article['importance']}\n")
                f.write(f"**字数**: {article['word_count']} | **创建时间**: {article['created_at']}\n")
                f.write(f"**来源**: {article['source_url']}\n\n")
                f.write(f"{'-'*80}\n\n")
                f.write(article['content'])

            print(f"Article exported to: {output_file}")
        except Exception as e:
            print(f"Failed to export article: {e}")

    def show_stats(self):
        """Show system statistics"""
        # TODO: Implement statistics
        print("Statistics feature coming soon...")

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python cli.py list [limit]          - List recent articles")
        print("  python cli.py show <id>             - Show article content")
        print("  python cli.py export <id> <file>    - Export article to file")
        print("  python cli.py stats                 - Show statistics")
        return

    cli = CLI()
    command = sys.argv[1]

    if command == 'list':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        cli.list_articles(limit)
    elif command == 'show':
        if len(sys.argv) < 3:
            print("Error: Article ID required")
            return
        cli.show_article(int(sys.argv[2]))
    elif command == 'export':
        if len(sys.argv) < 4:
            print("Error: Article ID and output file required")
            return
        cli.export_article(int(sys.argv[2]), sys.argv[3])
    elif command == 'stats':
        cli.show_stats()
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main()
```

**Step 3: 创建 main.py**

```python
#!/usr/bin/env python3
"""
Financial News Generator - Main Entry Point
"""
import sys
from config import Config
from logger import Logger
from health_check import HealthCheck
from scheduler import NewsScheduler
from error_handler import FatalError

def main():
    """Main entry point"""
    # Initialize logger
    logger = Logger.get_logger('main')

    try:
        logger.info("="*60)
        logger.info("Financial News Generator Starting...")
        logger.info("="*60)

        # Startup health check
        HealthCheck.startup_check()

        # Cleanup old logs
        Logger.cleanup_old_logs()

        # Start scheduler
        scheduler = NewsScheduler()
        scheduler.start()

    except FatalError as e:
        logger.critical(f"Fatal error: {e}")
        logger.critical("System cannot start. Please fix the issues and try again.")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**Step 4: 创建 README.md**

```markdown
# 财经内容自动生成系统

自动采集美国财经新闻，使用 Claude AI 进行智能分析和内容生成，输出面向中文读者的高质量财经文章。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，至少需要配置：
- `CLAUDE_API_KEY`: 你的 Claude API 密钥
- `RSS_FEEDS`: RSS 源列表（逗号分隔）

### 3. 运行系统

```bash
python main.py
```

系统将每 30 分钟自动采集和生成文章。

### 4. 查看生成的文章

```bash
# 列出最近的文章
python cli.py list

# 查看特定文章
python cli.py show 1

# 导出文章到文件
python cli.py export 1 article.md
```

## 项目结构

```
financial-news-generator/
├── config.py              # 配置管理
├── error_handler.py       # 错误处理
├── logger.py              # 日志系统
├── storage.py             # 数据存储
├── data_fetcher.py        # 数据采集
├── analyzer.py            # 智能分析
├── generator.py           # 内容生成
├── health_check.py        # 健康检查
├── scheduler.py           # 任务调度
├── cli.py                 # 命令行工具
├── main.py                # 主程序入口
├── requirements.txt       # 依赖列表
├── .env.example           # 配置模板
└── data/                  # 数据目录
    ├── articles.db        # 文章数据库
    ├── backup/            # 备份目录
    └── backups/           # 数据库备份
```

## 功能特性

- ✅ 自动采集多个 RSS 源
- ✅ Claude AI 智能分析新闻重要性
- ✅ 双策略内容生成（快讯/深度分析）
- ✅ 完整的错误处理和重试机制
- ✅ 日志记录和监控
- ✅ 健康检查和自我恢复
- ✅ 命令行工具

## 配置说明

详见 `.env.example` 文件中的注释。

## 日志

日志文件位于 `logs/` 目录：
- `financial-news-YYYY-MM-DD.log`: 主日志
- `errors-YYYY-MM-DD.log`: 错误日志

## 许可证

MIT License
```

**Step 5: 提交所有文件**

```bash
git add scheduler.py cli.py main.py README.md
git commit -m "feat: add scheduler, CLI, and main entry point

- Add NewsScheduler with APScheduler
- Add CLI tool for viewing and exporting articles
- Add main.py entry point with health checks
- Add comprehensive README

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## 完成

实施计划已完成！所有核心模块已定义：

1. ✅ 项目初始化和配置管理
2. ✅ 错误处理和日志系统
3. ✅ 数据存储层
4. ✅ 数据采集层
5. ✅ 智能分析层
6. ✅ 内容生成层
7. ✅ 健康检查系统
8. ✅ 主调度器和命令行工具

**下一步：**
- 创建 `.env` 文件并配置 API 密钥
- 安装依赖：`pip install -r requirements.txt`
- 运行系统：`python main.py`

---