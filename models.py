from typing import List, Dict
from datetime import datetime
from data_fetcher import NewsItem


class NewsEvent:
    """Aggregated news event"""

    def __init__(
        self,
        event_id: str,
        main_title: str,
        event_summary: str,
        news_items: List[NewsItem],
        importance: int,
    ):
        self.event_id = event_id
        self.main_title = main_title
        self.event_summary = event_summary
        self.news_items = news_items
        self.source_count = len(news_items)
        self.earliest_time = min(item.published for item in news_items)
        self.importance = importance
        self.hotness = min(self.source_count, 4)  # Max 4 points
        self.timeliness = 0.0  # Will be calculated
        self.total_score = 0.0  # Will be calculated

    def calculate_timeliness(self) -> float:
        """Calculate timeliness score based on earliest publication time"""
        try:
            earliest = datetime.fromisoformat(self.earliest_time)
            now = datetime.now()
            hours_ago = (now - earliest).total_seconds() / 3600

            if hours_ago <= 1:
                return 1.0
            elif hours_ago <= 6:
                return 0.8
            elif hours_ago <= 12:
                return 0.5
            elif hours_ago <= 24:
                return 0.3
            else:
                return 0.1
        except Exception:
            return 0.1

    def calculate_total_score(
        self, importance_weight=0.6, hotness_weight=0.3, timeliness_weight=0.1
    ) -> float:
        """Calculate total score"""
        self.timeliness = self.calculate_timeliness()
        self.total_score = (
            self.importance * importance_weight
            + self.hotness * hotness_weight
            + self.timeliness * timeliness_weight
        )
        return self.total_score

    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "main_title": self.main_title,
            "event_summary": self.event_summary,
            "source_count": self.source_count,
            "earliest_time": self.earliest_time,
            "importance": self.importance,
            "hotness": self.hotness,
            "timeliness": self.timeliness,
            "total_score": self.total_score,
            "news_items": [item.to_dict() for item in self.news_items],
        }


class ImpactAnalysis:
    """Multi-dimensional impact analysis"""

    def __init__(self, event_id: str, analysis_data: Dict):
        self.event_id = event_id
        self.global_economy = analysis_data.get("global_economy", {})
        self.us_economy = analysis_data.get("us_economy", {})
        self.china_economy = analysis_data.get("china_economy", {})
        self.us_stock = analysis_data.get("us_stock", {})
        self.china_stock = analysis_data.get("china_stock", {})
        self.other_markets = analysis_data.get("other_markets", {})

    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "global_economy": self.global_economy,
            "us_economy": self.us_economy,
            "china_economy": self.china_economy,
            "us_stock": self.us_stock,
            "china_stock": self.china_stock,
            "other_markets": self.other_markets,
        }

    def get_dimensions(self) -> List[Dict]:
        """Get all dimensions as a list"""
        return [
            {"dimension": "global_economy", **self.global_economy},
            {"dimension": "us_economy", **self.us_economy},
            {"dimension": "china_economy", **self.china_economy},
            {"dimension": "us_stock", **self.us_stock},
            {"dimension": "china_stock", **self.china_stock},
            {"dimension": "other_markets", **self.other_markets},
        ]
