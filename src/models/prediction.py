from dataclasses import dataclass
from src.models.mapping import G_entity


@dataclass
class Prediction:
    """Prediction for a future period"""

    g_entity: G_entity
    period_label: str
    predicted_quantity: float
    baseline: float
    buffer_percentage: float
    method: str

    @property
    def buffer_amount(self) -> float:
        """Calculate the actual buffer amount"""
        return self.predicted_quantity - self.baseline
