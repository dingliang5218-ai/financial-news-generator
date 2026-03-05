import json
import hashlib
from typing import List, Dict
from anthropic import Anthropic
from config import Config
from logger import Logger
from error_handler import retry_with_backoff, RetryableError, DegradableError
from data_fetcher import NewsItem
from analyzer import NewsAnalysis
from models import NewsEvent

logger = Logger.get_logger("aggregator")


class NewsAggregator:
    """Intelligent news aggregator using Claude AI"""

    def __init__(self):
        self.client = Anthropic(api_key=Config.CLAUDE_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    @retry_with_backoff()
    def aggregate(
        self, news_items: List[NewsItem], analyses: Dict[str, NewsAnalysis]
    ) -> List[NewsEvent]:
        """
        Aggregate news items into events

        Args:
            news_items: List of news items
            analyses: Dict mapping news URL to NewsAnalysis

        Returns:
            List of NewsEvent objects
        """
        if not news_items:
            return []

        try:
            # Prepare news list for Claude
            news_list = []
            for idx, item in enumerate(news_items):
                analysis = analyses.get(item.url)
                news_list.append(
                    {
                        "id": idx,
                        "title": item.title,
                        "content": item.content[:500],
                        "url": item.url,
                        "source": item.source,
                        "importance": analysis.importance if analysis else 3,
                    }
                )

            prompt = f"""分析这批新闻，识别报道同一事件的新闻组。

新闻列表：
{json.dumps(news_list, ensure_ascii=False, indent=2)}

请识别哪些新闻报道的是同一个事件。

返回 JSON 格式：
{{
  "events": [
    {{
      "event_id": "unique_id",
      "main_title": "事件主标题",
      "news_ids": [0, 2, 5],
      "event_summary": "事件简述"
    }}
  ],
  "standalone_news": [1, 3, 4]
}}"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                timeout=30.0,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            result = json.loads(content)
            events = []

            for event_data in result.get("events", []):
                event_id = event_data["event_id"]
                news_ids = event_data["news_ids"]
                event_news_items = [
                    news_items[i] for i in news_ids if i < len(news_items)
                ]

                if not event_news_items:
                    continue

                importance = max(
                    analyses.get(item.url).importance
                    for item in event_news_items
                    if item.url in analyses
                )

                event = NewsEvent(
                    event_id=event_id,
                    main_title=event_data["main_title"],
                    event_summary=event_data["event_summary"],
                    news_items=event_news_items,
                    importance=importance,
                )
                events.append(event)
                logger.info(f"Aggregated event: {event.main_title}")

            for news_id in result.get("standalone_news", []):
                if news_id >= len(news_items):
                    continue

                item = news_items[news_id]
                analysis = analyses.get(item.url)
                if not analysis:
                    continue

                event_id = hashlib.md5(item.title.encode()).hexdigest()[:12]
                event = NewsEvent(
                    event_id=f"standalone_{event_id}",
                    main_title=item.title,
                    event_summary=analysis.summary,
                    news_items=[item],
                    importance=analysis.importance,
                )
                events.append(event)

            logger.info(f"Aggregation complete: {len(events)} events")
            return events

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse aggregation response: {e}")
            raise DegradableError(f"Invalid aggregation response: {e}")
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RetryableError(f"Rate limit: {e}")
            else:
                raise DegradableError(f"Aggregation failed: {e}")
