from typing import Dict
from anthropic import Anthropic
from config import Config
from logger import Logger
from error_handler import retry_with_backoff, RetryableError, DegradableError
from data_fetcher import NewsItem
from analyzer import NewsAnalysis

logger = Logger.get_logger("generator")


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
                timeout=30.0,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text.strip()
            word_count = len(content)

            logger.info(
                f"Generated quick news: {news_item.title[:50]}... ({word_count} chars)"
            )

            return {
                "title": news_item.title,
                "content": content,
                "source_url": news_item.url,
                "importance": analysis.importance,
                "news_type": analysis.news_type,
                "word_count": word_count,
            }

        except Exception as e:
            if "rate_limit" in str(e).lower():
                logger.warning("Claude API rate limit reached")
                raise RetryableError(f"Rate limit: {e}")
            else:
                logger.error(f"Failed to generate quick news: {e}")
                raise DegradableError(f"Generation failed: {e}")

    def _generate_deep_analysis(
        self, news_item: NewsItem, analysis: NewsAnalysis
    ) -> Dict:
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
                timeout=30.0,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text.strip()
            word_count = len(content)

            logger.info(
                f"Generated deep analysis: {news_item.title[:50]}... ({word_count} chars)"
            )

            return {
                "title": news_item.title,
                "content": content,
                "source_url": news_item.url,
                "importance": analysis.importance,
                "news_type": analysis.news_type,
                "word_count": word_count,
            }

        except Exception as e:
            if "rate_limit" in str(e).lower():
                logger.warning("Claude API rate limit reached")
                raise RetryableError(f"Rate limit: {e}")
            else:
                logger.error(f"Failed to generate deep analysis: {e}")
                raise DegradableError(f"Generation failed: {e}")
