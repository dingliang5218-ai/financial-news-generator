import json
from typing import Dict, Optional
from anthropic import Anthropic
from config import Config
from logger import Logger
from error_handler import retry_with_backoff, RetryableError, DegradableError
from data_fetcher import NewsItem

logger = Logger.get_logger("analyzer")


class NewsAnalysis:
    """News analysis result"""

    def __init__(
        self, importance: int, news_type: str, is_breaking: bool, summary: str
    ):
        self.importance = importance
        self.news_type = news_type
        self.is_breaking = is_breaking
        self.summary = summary

    def to_dict(self) -> Dict:
        return {
            "importance": self.importance,
            "news_type": self.news_type,
            "is_breaking": self.is_breaking,
            "summary": self.summary,
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
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            content = response.content[0].text
            result = json.loads(content)

            analysis = NewsAnalysis(
                importance=result["importance"],
                news_type=result["news_type"],
                is_breaking=result["is_breaking"],
                summary=result["summary"],
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
