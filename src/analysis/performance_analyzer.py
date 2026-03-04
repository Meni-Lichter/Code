from datetime import datetime, date
from typing import List, Dict
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from src.models.mapping import Room
from ..models import SalesRecord, PerformanceData, TimePeriod
from ..utils import get_period_key
from src.models import G_entity


class PerformanceAnalyzer:
    """Feature 2: Analyze historical performance"""

    def __init__(self):
        self.sales_data = []  # This will be set by the PerformanceCenter when initialized

    def analyze(
        self,
        analyzed_obj: G_entity,
        lookback_years: int = 3,
        granularity: str = "monthly",
    ) -> PerformanceData:
        """Main analysis function to analyze performance for a given 12NC or Room
        input:
            - identifier: the 12NC or Room number to analyze
            - id_type: "12nc" or "room"
            - lookback_years: number of years to look back for analysis
            - granularity: "monthly" or "yearly"
        output:
            - PerformanceData object containing historical performance data
        """
        self.sales_data = (
            analyzed_obj.g_entity.sales_history
        )  # Assuming Room and TwelveNC have a sales_records attribute

        end_date = datetime.now().date()
        start_date = end_date - relativedelta(years=lookback_years)

        filtered_sales = self._filter_sales(analyzed_obj, start_date, end_date)

        grouped = self._group_by_period(filtered_sales, granularity)

        periods = []  # List of TimePeriod objects for the performance data
        for period_key in sorted(grouped.keys()):
            sales = grouped[period_key]
            periods.append(TimePeriod(label=period_key, quantity=sum(s.quantity for s in sales)))

        total_qty = sum(p.quantity for p in periods)
        avg_qty = total_qty / len(periods) if periods else 0

        return PerformanceData(
            g_entity=analyzed_obj,
            periods=periods,
            granularity=granularity,
            total=total_qty,
            average=avg_qty,
        )

    def _filter_sales(
        self, analyzed_obj: G_entity, start_date: date, end_date: date
    ) -> List[SalesRecord]:
        """Private method to filter sales by identifier and date range
        input:
            - analyzed_obj: the Room or TwelveNC object to filter by
            - start_date: the start date for filtering
            - end_date: the end date for filtering
        output:
            - List of SalesRecord that match the criteria
        """
        if not self.sales_data:
            raise ValueError("No sales data available for filtering")
        relevnat_sales = []
        for sale in self.sales_data:
            if start_date <= sale.date <= end_date:
                relevnat_sales.append(sale)
        return relevnat_sales

    def _group_by_period(
        self, sales: List[SalesRecord], granularity: str
    ) -> Dict[str, List[SalesRecord]]:
        """Private method to group sales by time period based on the specified granularity,
        input:
            - sales: List of SalesRecord to group
            - granularity: "monthly" or "yearly"
        output:
            - Dictionary with period keys and corresponding sales records
        """
        groups = defaultdict(list)

        for sale in sales:
            key = get_period_key(sale.date, granularity)
            groups[key].append(sale)

        return groups

    def multi_item_analyze(
        self,
        analyzed_objs: List[G_entity],
        lookback_years: int = 3,
        granularity: str = "monthly",
    ) -> Dict[str, List[PerformanceData]]:
        """Analyze multiple items:
        input:
            - analyzed_objs: List of Room or TwelveNC objects to analyze
            - lookback_years: number of years to look back for analysis
            - granularity: "monthly" or "yearly"
        output:
            - dictionary of PerformanceData for each analyzed object
        """
        results = defaultdict(list)
        for analyzed_obj in analyzed_objs:
            try:
                performance_data = self.analyze(
                    analyzed_obj=analyzed_obj,
                    lookback_years=lookback_years,
                    granularity=granularity,
                )
                results[analyzed_obj].append(performance_data)
            except Exception as e:
                print(f"Error analyzing entity '{analyzed_obj}': {e}")

        return results
