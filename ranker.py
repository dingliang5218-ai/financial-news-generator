from typing import List
from config import Config
from logger import Logger
from models import NewsEvent

logger = Logger.get_logger('ranker')


class NewsRanker:
    """News event ranker"""

    def __init__(
        self,
        importance_weight=0.6,
        hotness_weight=0.3,
        timeliness_weight=0.1
    ):
        self.importance_weight = importance_weight
        self.hotness_weight = hotness_weight
        self.timeliness_weight = timeliness_weight

    def rank_and_select_top(
        self, events: List[NewsEvent], top_n: int = 3
    ) -> List[NewsEvent]:
        """
        Rank events and select top N

        Args:
            events: List of NewsEvent objects
            top_n: Number of top events to return

        Returns:
            List of top N NewsEvent objects
        """
        if not events:
            return []

        # Calculate scores for all events
        for event in events:
            event.calculate_total_score(
                self.importance_weight,
                self.hotness_weight,
                self.timeliness_weight
            )

        # Sort by total score (descending)
        sorted_events = sorted(
            events,
            key=lambda e: e.total_score,
            reverse=True
        )

        # Select top N
        top_events = sorted_events[:top_n]

        logger.info(f"Ranked {len(events)} events, selected top {len(top_events)}")
        for idx, event in enumerate(top_events, 1):
            logger.info(
                f"  #{idx}: {event.main_title} "
                f"(score: {event.total_score:.2f}, "
                f"importance: {event.importance}, "
                f"hotness: {event.hotness}, "
                f"timeliness: {event.timeliness:.2f})"
            )

        return top_events
