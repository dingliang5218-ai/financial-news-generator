import json
from typing import Dict
from anthropic import Anthropic
from config import Config
from logger import Logger
from error_handler import retry_with_backoff, RetryableError, DegradableError
from models import NewsEvent, ImpactAnalysis

logger = Logger.get_logger("impact_analyzer")


class ImpactAnalyzer:
    """Multi-dimensional impact analyzer"""

    def __init__(self):
        self.client = Anthropic(api_key=Config.CLAUDE_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    @retry_with_backoff()
    def analyze(self, event: NewsEvent) -> ImpactAnalysis:
        """
        Analyze multi-dimensional impact of a news event

        Args:
            event: NewsEvent object

        Returns:
            ImpactAnalysis object
        """
        try:
            # Prepare event content
            event_content = f"""标题：{event.main_title}

摘要：{event.event_summary}

来源数量：{event.source_count}

详细内容：
"""
            for item in event.news_items:
                event_content += f"\n[{item.source}] {item.content[:300]}\n"

            prompt = f"""分析这条新闻事件对各个市场的影响：

{event_content}

请从以下维度分析影响：
1. 全球经济 (global_economy)
2. 美国经济 (us_economy)
3. 中国经济 (china_economy)
4. 美国股市 (us_stock)
5. 中国股市/A股 (china_stock)
6. 其他市场 (other_markets)

对每个维度，评估：
- impact_level: "high"（高影响）/ "medium"（中影响）/ "low"（低影响）/ "none"（无影响）
- explanation: 影响说明（50字内）

返回 JSON 格式：
{{
  "global_economy": {{
    "impact_level": "medium",
    "explanation": "影响说明"
  }},
  "us_economy": {{
    "impact_level": "high",
    "explanation": "影响说明"
  }},
  "china_economy": {{
    "impact_level": "low",
    "explanation": "影响说明"
  }},
  "us_stock": {{
    "impact_level": "high",
    "explanation": "影响说明"
  }},
  "china_stock": {{
    "impact_level": "medium",
    "explanation": "影响说明"
  }},
  "other_markets": {{
    "impact_level": "low",
    "explanation": "影响说明"
  }}
}}"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                timeout=30.0,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            content = response.content[0].text.strip()

            # Remove markdown code blocks
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            analysis_data = json.loads(content)

            # Validate structure
            required_dimensions = [
                "global_economy",
                "us_economy",
                "china_economy",
                "us_stock",
                "china_stock",
                "other_markets",
            ]
            for dim in required_dimensions:
                if dim not in analysis_data:
                    raise ValueError(f"Missing dimension: {dim}")
                if "impact_level" not in analysis_data[dim]:
                    raise ValueError(f"Missing impact_level in {dim}")
                if "explanation" not in analysis_data[dim]:
                    raise ValueError(f"Missing explanation in {dim}")

            analysis = ImpactAnalysis(event.event_id, analysis_data)

            logger.info(f"Impact analysis complete for: {event.main_title}")
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse impact analysis: {e}\nResponse: {content}")
            raise DegradableError(f"Invalid analysis response: {e}")
        except Exception as e:
            if "rate_limit" in str(e).lower():
                logger.warning("Claude API rate limit reached")
                raise RetryableError(f"Rate limit: {e}")
            else:
                logger.error(f"Impact analysis failed: {e}")
                raise DegradableError(f"Analysis failed: {e}")
