import feedparser
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from config import Config
from logger import Logger
from error_handler import retry_with_backoff, RetryableError, DegradableError
from storage import Storage

logger = Logger.get_logger("data_fetcher")


class NewsItem:
    """News item data structure"""

    def __init__(self, title: str, content: str, url: str, published: str, source: str):
        if not title or not title.strip():
            raise ValueError("NewsItem title cannot be empty")
        if not url or not url.strip():
            raise ValueError("NewsItem url cannot be empty")

        self.title = title
        self.content = content
        self.url = url
        self.published = published
        self.source = source

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "published": self.published,
            "source": self.source,
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

            if not feed.entries:
                logger.warning(f"No entries found in RSS feed: {self.name}")
                self._update_status(True)
                return []

            news_items = []
            for entry in feed.entries[:Config.MAX_NEWS_PER_SOURCE]:
                # Skip if already processed
                if self.storage.is_news_processed(entry.link):
                    continue

                news_item = NewsItem(
                    title=entry.get("title", ""),
                    content=entry.get("summary", entry.get("description", "")),
                    url=entry.get("link", ""),
                    published=entry.get("published", ""),
                    source=self.name,
                )
                news_items.append(news_item)
                # Mark as processed immediately after adding
                self.storage.mark_news_processed(entry.link)

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

        logger.info(
            f"Total fetched: {len(all_news)} news items from {successful_sources} sources"
        )
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
