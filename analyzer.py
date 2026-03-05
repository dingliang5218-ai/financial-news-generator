import json
from typing import Dict, Optional
from anthropic import Anthropic, RateLimitError
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
        content = ""  # Initialize to avoid UnboundLocalError
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
                timeout=30.0,  # Add timeout handling
            )

            # Parse response with markdown cleanup
            content = response.content[0].text.strip()

            # Remove possible markdown code block markers
            if content.startswith("```"):
                lines = content.split("\n")
                # Remove first line (```json or ```)
                lines = lines[1:]
                # Remove last line (```)
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines).strip()

            result = json.loads(content)

            # Validate response fields
            if "importance" not in result or "news_type" not in result or \
               "is_breaking" not in result or "summary" not in result:
                raise ValueError("Missing required fields in response")

            # Validate importance is 1-5 integer
            importance = result["importance"]
            if not isinstance(importance, int) or importance < 1 or importance > 5:
                raise ValueError(f"Invalid importance value: {importance}, must be integer 1-5")

            # Validate is_breaking is boolean
            is_breaking = result["is_breaking"]
            if not isinstance(is_breaking, bool):
                raise ValueError(f"Invalid is_breaking value: {is_breaking}, must be boolean")

            analysis = NewsAnalysis(
                importance=importance,
                news_type=result["news_type"],
                is_breaking=is_breaking,
                summary=result["summary"],
            )

            logger.info(
                f"Analyzed: {news_item.title[:50]}... "
                f"(importance: {analysis.importance}, type: {analysis.news_type})"
            )

            return analysis

        except RateLimitError as e:
            logger.warning("Claude API rate limit reached, will retry")
            raise RetryableError(f"Rate limit: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response: {e}\nResponse: {content}")
            raise DegradableError(f"Invalid response format: {e}")
        except ValueError as e:
            logger.error(f"Response validation failed: {e}\nResponse: {content}")
            raise DegradableError(f"Invalid response data: {e}")
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
