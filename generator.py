from typing import Dict, List
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

    @retry_with_backoff()
    def generate_daily_summary(
        self, top_events: List['NewsEvent'], analyses: Dict[str, 'ImpactAnalysis']
    ) -> Dict:
        """Generate daily summary article for top 3 events"""
        try:
            # Prepare events content
            events_content = ""
            for idx, event in enumerate(top_events, 1):
                analysis = analyses.get(event.event_id)
                events_content += f"\n\n事件{idx}：{event.main_title}\n"
                events_content += f"摘要：{event.event_summary}\n"
                events_content += f"来源数：{event.source_count}\n"

                if analysis:
                    events_content += "影响分析：\n"
                    for dim_data in analysis.get_dimensions():
                        if dim_data['impact_level'] != 'none':
                            events_content += f"  - {dim_data['dimension']}: {dim_data['impact_level']} - {dim_data['explanation']}\n"

            prompt = f"""请将今日三大财经要闻整合成一篇"今日财经要闻"汇总文章。

今日要闻：
{events_content}

要求：
- 字数：1500-2000字
- 结构：
  1. 开篇总览（200字）- 概述三大要闻和市场整体情绪
  2. 要闻一（400-500字）- 事件概述 + 多维度影响分析
  3. 要闻二（400-500字）
  4. 要闻三（400-500字）
  5. 综合点评（200-300字）- 三大新闻的关联性和投资启示
- 语言专业、通俗易懂
- 不要使用 markdown 格式

请直接输出文章内容，包含标题。"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                timeout=30.0,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text.strip()
            word_count = len(content)

            # Extract title (first line)
            lines = content.split('\n', 1)
            title = lines[0].strip()
            article_content = lines[1].strip() if len(lines) > 1 else content

            logger.info(f"Generated daily summary: {word_count} chars")

            return {
                'title': title,
                'content': article_content,
                'article_type': 'daily_summary',
                'word_count': word_count,
                'event_ids': [e.event_id for e in top_events]
            }

        except Exception as e:
            if "rate_limit" in str(e).lower():
                logger.warning("Claude API rate limit reached")
                raise RetryableError(f"Rate limit: {e}")
            else:
                logger.error(f"Failed to generate daily summary: {e}")
                raise DegradableError(f"Generation failed: {e}")

    @retry_with_backoff()
    def generate_deep_analysis_for_event(
        self, event: 'NewsEvent', analysis: 'ImpactAnalysis'
    ) -> Dict:
        """Generate deep analysis article for important event"""
        try:
            # Prepare event content
            event_content = f"""标题：{event.main_title}

摘要：{event.event_summary}

来源数量：{event.source_count}

详细内容：
"""
            for item in event.news_items:
                event_content += f"\n[{item.source}] {item.title}\n{item.content}\n"

            # Prepare impact analysis
            impact_content = "\n多维度影响分析：\n"
            for dim_data in analysis.get_dimensions():
                impact_content += f"- {dim_data['dimension']}: {dim_data['impact_level']} - {dim_data['explanation']}\n"

            prompt = f"""请为这个重大财经事件撰写一篇深度分析文章。

{event_content}

{impact_content}

要求：
- 字数：1500-2500字
- 结构：
  1. 事件全景（300字）- 综合所有来源的报道，事件时间线
  2. 背景分析（400字）- 历史背景、相关政策/数据
  3. 多维度影响分析（600-800字）- 详细分析对各市场的影响
  4. 未来展望（300-400字）- 短期影响预测、长期趋势判断、投资建议
- 语言专业、深入浅出
- 不要使用 markdown 格式

请直接输出文章内容，包含标题。"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=5000,
                timeout=30.0,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text.strip()
            word_count = len(content)

            # Extract title
            lines = content.split('\n', 1)
            title = lines[0].strip()
            article_content = lines[1].strip() if len(lines) > 1 else content

            logger.info(f"Generated deep analysis for {event.main_title}: {word_count} chars")

            return {
                'title': title,
                'content': article_content,
                'article_type': 'deep_analysis',
                'event_id': event.event_id,
                'importance': event.importance,
                'word_count': word_count
            }

        except Exception as e:
            if "rate_limit" in str(e).lower():
                logger.warning("Claude API rate limit reached")
                raise RetryableError(f"Rate limit: {e}")
            else:
                logger.error(f"Failed to generate deep analysis: {e}")
                raise DegradableError(f"Generation failed: {e}")
