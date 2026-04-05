"""Shared chart utility functions for UI components"""

import calendar
from typing import List, Optional


def extract_year_from_period(period_label: str, analyzer_granularity: str) -> int | None:
    """Extract year from analyzer period label
    Args:
        period_label: Period label from analyzer (e.g., "03-2024", "2024-Q1", "2024")
        analyzer_granularity: The granularity used by analyzer ("monthly", "quarterly", "yearly")
    Does: Parses the given period label based on the specified analyzer granularity to extract the year as an integer.
         For "monthly" granularity, it expects a format like "MM-YYYY" and extracts the year part.
    Returns:
        Year as integer, or None if cannot be extracted
    """
    try:
        if analyzer_granularity == "monthly":
            # Format: "03-2024" -> 2024
            return int(period_label.split("-")[1])
        elif analyzer_granularity == "quarterly":
            # Format: "2024-Q1" -> 2024
            return int(period_label.split("-")[0])
        elif analyzer_granularity == "yearly":
            # Format: "2024" -> 2024
            return int(period_label)
    except (ValueError, IndexError):
        return None
    return None


def convert_period_label_to_ui(period_label: str, analyzer_granularity: str) -> str:
    """Convert analyzer period label to UI-friendly format
    Args:
        period_label: Period label from analyzer (e.g., "03-2024", "2024-Q1")
        analyzer_granularity: The granularity used by analyzer ("monthly", "quarterly", "yearly")
    Does : Converts the given period label from the analyzer format to a more user-friendly format for display in the UI.
            For "monthly" granularity, it converts "MM-YYYY" to the abbreviated month name (e.g., "Mar").
    Returns:
        UI-friendly label (e.g., "Mar", "Q1", "2024")
    """
    try:
        if analyzer_granularity == "monthly":
            # Format: "03-2024" -> "Mar"
            month_num = int(period_label.split("-")[0])
            return calendar.month_abbr[month_num]
        elif analyzer_granularity == "quarterly":
            # Format: "2024-Q1" -> "Q1"
            parts = period_label.split("-")
            return parts[1] if len(parts) > 1 else period_label
        elif analyzer_granularity == "yearly":
            # Format: "2024" -> "2024"
            return period_label
    except (ValueError, IndexError):
        pass
    return period_label


def get_all_period_labels(granularity: str, available_years: Optional[List[int]] = None) -> List[str]:
    """Get all possible period labels for given granularity
    Args:
        granularity: UI granularity ("Months", "Quarters", "Years")
        available_years: List of years (only needed for "Years" granularity)
    Does: Generates a list of all possible period labels based on the specified UI granularity.
         For "Months", it returns the abbreviated month names. For "Quarters", 
         it returns "Q1" to "Q4". For "Years", it returns the list of available years as strings.
    Returns:
        List of period labels in order
    """
    if granularity == "Months":
        return [calendar.month_abbr[i] for i in range(1, 13)]
    elif granularity == "Quarters":
        return ["Q1", "Q2", "Q3", "Q4"]
    elif granularity == "Years":
        if available_years:
            return [str(year) for year in sorted(available_years)]
        return []
    return []


def add_bar_value_labels(ax, bars, values):
    """Add value labels on top of bars in a matplotlib chart
    Args:
        ax: Matplotlib axes object
        bars: Bar containers returned by ax.bar()
        values: Corresponding values for each bar
    Does: Iterates through the given bars and their corresponding values, and adds a text label on top of each bar that has a value greater than zero. 
         The label displays the integer value, is centered horizontally on the bar, and is positioned just above the top of the bar for better visibility.
    Returns: None
    """
    if not ax or not bars or not values:
        return
    
    for bar, value in zip(bars, values):
        if value > 0:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'{int(value)}',
                ha='center',
                va='bottom',
                fontsize=8,
                color='#333333',
                fontweight='bold'
            )
