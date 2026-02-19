from dataclasses import dataclass
from typing import List


@dataclass
class TimePeriod:
    """Simple time period definition"""

    label: str
    quantity: int


@dataclass
class PerformanceData:
    """Performance summary over time"""

    identifier: str
    type: str  # "12NC" or "Room"
    periods: List[TimePeriod]
    total: int
    average: float

    @property
    def period_count(self) -> int:
        """Number of periods analyzed"""
        return len(self.periods)

    def get_period(self, label: str) -> TimePeriod | None:
        """Get specific period by label"""
        return next((p for p in self.periods if p.label == label), None)
