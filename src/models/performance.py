from dataclasses import dataclass
from typing import List
from src.models.mapping import G_entity


@dataclass
class TimePeriod:
    """Simple time period definition
    label - e.g. "2021-Q1", "2021", "Jan 2021"
    quantity - total quantity sold in that period
    """

    label: str
    quantity: int


@dataclass
class PerformanceData:
    """Performance summary over time"""

    g_entity: G_entity  # Room or TwelveNC
    periods: List[TimePeriod]
    granularity: str  # "daily", "monthly", "quarterly", "yearly"
    total: int
    average: float

    def __post_init__(self):
        """Validate data on initialization"""
        if not self.g_entity:
            raise ValueError("G_entity cannot be empty")
        if not self.periods:
            raise ValueError("Periods cannot be empty")

    @property
    def period_count(self) -> int:
        """Number of periods analyzed"""
        return len(self.periods)

    def get_period(self, label: str) -> TimePeriod | None:
        """Get specific period by label"""
        return next((p for p in self.periods if p.label == label), None)

    def get_type(self) -> str:
        return self.g_entity.entity_type.upper()

    def get_entity_id(self) -> str:
        return self.g_entity.id
