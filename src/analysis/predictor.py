from typing import List
from ..models import PerformanceData, Prediction
from ..utils import get_next_period_label


class Predictor:
    """Feature 3: Predict future demand based on historical performance"""

    def __init__(self, performance_data: PerformanceData):
        """
        Initialize predictor with historical performance data

        Args:
            performance_data: PerformanceData object with historical periods
        """
        self.performance_data = performance_data

    def predict(self, method: str = "average", buffer_percentage: float = 10.0) -> Prediction:
        """
        Predict demand for the next period

        Args:
            method: Prediction method ("average", "last", "trend")
            buffer_percentage: Safety buffer percentage to add

        Returns:
            Prediction object with forecasted quantity
        """
        if not self.performance_data.periods:
            raise ValueError("No historical data available for prediction")

        # Calculate baseline prediction based on method
        if method == "last":
            baseline = float(self.performance_data.periods[-1].quantity)
        elif method == "trend":
            baseline = self._calculate_trend()
        else:  # default to average
            baseline = self.performance_data.average

        # Apply buffer
        predicted_quantity = baseline * (1 + buffer_percentage / 100)

        # Determine next period label based on current granularity
        granularity = self._infer_granularity()
        next_period = get_next_period_label(granularity)

        return Prediction(
            identifier=self.performance_data.identifier,
            type=self.performance_data.type,
            period_label=next_period,
            predicted_quantity=predicted_quantity,
            baseline=baseline,
            buffer_percentage=buffer_percentage,
            method=method,
        )

    def _calculate_trend(self) -> float:
        """Calculate trend-based prediction using linear regression on recent periods"""
        periods = self.performance_data.periods
        if len(periods) < 2:
            return self.performance_data.average

        # Use last 3 periods or all if less than 3
        recent_periods = periods[-3:] if len(periods) >= 3 else periods

        # Simple linear trend: calculate average change
        changes = []
        for i in range(1, len(recent_periods)):
            changes.append(recent_periods[i].quantity - recent_periods[i - 1].quantity)

        avg_change = sum(changes) / len(changes) if changes else 0

        # Project next period
        return float(recent_periods[-1].quantity + avg_change)

    def _infer_granularity(self) -> str:
        """Infer time granularity from period labels"""
        if not self.performance_data.periods:
            return "monthly"

        label = self.performance_data.periods[0].label

        if "-W" in label:
            return "weekly"
        elif "-Q" in label:
            return "quarterly"
        elif len(label) == 4 and label.isdigit():
            return "yearly"
        elif len(label) == 10:  # YYYY-MM-DD
            return "daily"
        else:
            return "monthly"

    def multi_period_predict(
        self, periods: int = 3, method: str = "average", buffer_percentage: float = 10.0
    ) -> List[Prediction]:
        """
        Predict demand for multiple future periods

        Args:
            periods: Number of future periods to predict
            method: Prediction method
            buffer_percentage: Safety buffer percentage

        Returns:
            List of Prediction objects
        """
        predictions = []

        for i in range(periods):
            prediction = self.predict(method, buffer_percentage)
            predictions.append(prediction)

            # For subsequent predictions, we could update the baseline
            # but for simplicity, we'll use the same approach

        return predictions
