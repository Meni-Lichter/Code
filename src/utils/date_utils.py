"""Date utility functions for period key generation and next period labeling"""

import calendar
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from src.utils import load_config


def get_period_key(dt: date, granularity: str) -> str:
    """Generate period key based on granularity using MM-DD-YYYY format from config
    input:
        - dt: date object
        - granularity: "daily", "monthly", "quarterly", "yearly"
    output:
        - String representing the period key in MM-DD-YYYY compatible format
    """
    if granularity == "daily":
        return dt.strftime("%m-%d-%Y")  # MM-DD-YYYY
    elif granularity == "monthly":
        return f"{dt.month:02d}-{dt.year}"  # MM-YYYY
    elif granularity == "quarterly":
        quarter = (dt.month - 1) // 3 + 1
        return f"{dt.year}-Q{quarter}"
    else:  # yearly
        return str(dt.year)


def get_next_period_label(granularity: str) -> str:
    """Generate the next period label based on granularity

    Returns labels in MM-DD-YYYY compatible format from config
    """
    now = datetime.now()

    if granularity == "yearly":
        return str(now.year + 1)
    elif granularity == "quarterly":
        current_quarter = (now.month - 1) // 3 + 1
        next_quarter = current_quarter + 1
        next_year = now.year
        if next_quarter > 4:
            next_quarter = 1
            next_year += 1
        return f"{next_year}-Q{next_quarter}"
    elif granularity == "monthly":
        next_month = now.month + 1
        next_year = now.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        # Return MM-YYYY format
        return f"{next_month:02d}-{next_year}"  # "03-2025"
    elif granularity == "daily":
        next_day = now + timedelta(days=1)
        # Format: MM-DD-YYYY
        return next_day.strftime("%m-%d-%Y")  # "02-24-2025"
    else:
        return str(now.year + 1)


def match_granularity(target_time: str, granularity: str) -> str:
    """
    Adjust target_time to match the granularity of historical performance data.

    If target is more specific than data (e.g., daily target but monthly data),
    convert target to data's granularity and notify user.

    If target is less specific than data (e.g., monthly target but daily data),
    keep target as-is (aggregation will happen during prediction).

    Args:
        target_time: User's requested target period
        granularity: Granularity of historical performance data

    Returns:
        Adjusted target_time matching data granularity
    """

    config = load_config()
    date_format = config["validation"].get("date_format", "MM-DD-YYYY")
    target_time = str(target_time)
    label_granularity = get_granularity_from_label(target_time, date_format)

    # If granularities match, no adjustment needed
    if label_granularity == granularity:
        return target_time

    # Define granularity hierarchy (least to most specific)
    granularity_order = {"yearly": 1, "quarterly": 2, "monthly": 3, "daily": 4}

    target_level = granularity_order.get(label_granularity, 0)
    data_level = granularity_order.get(granularity, 0)

    # Target is MORE specific than data - need to convert UP
    if target_level > data_level:
        print(
            f"⚠️  Warning: Target time '{target_time}' is {label_granularity}, "
            f"but data is {granularity}. Converting to {granularity} granularity."
        )

        try:
            # Parse based on label granularity using MM-DD-YYYY format
            if label_granularity == "daily":
                # Parse MM-DD-YYYY format
                date_obj = datetime.strptime(target_time, "%m-%d-%Y")
            elif label_granularity == "monthly":
                # Parse MM-YYYY format
                date_obj = datetime.strptime(target_time, "%m-%Y")
            elif label_granularity == "quarterly":
                parts = target_time.split("-Q")
                year = int(parts[0])
                quarter = int(parts[1])
                month = quarter * 3 - 2  # First month of quarter
                date_obj = datetime(year, month, 1)
            elif label_granularity == "yearly":
                date_obj = datetime(int(target_time), 1, 1)
            else:
                return target_time  # Can't parse, return as-is

            # Convert to data's granularity using MM-DD-YYYY format
            if granularity == "yearly":
                return f"{date_obj.year}"
            elif granularity == "quarterly":
                quarter = (date_obj.month - 1) // 3 + 1
                return f"{date_obj.year}-Q{quarter}"
            elif granularity == "monthly":
                # Return in MM-YYYY format
                return f"{date_obj.month:02d}-{date_obj.year}"
            elif granularity == "daily":
                # Return in MM-DD-YYYY format
                return date_obj.strftime("%m-%d-%Y")
            else:
                # Unknown granularity, return as-is
                return target_time

        except (ValueError, IndexError, AttributeError) as e:
            print(f"⚠️  Error parsing target time '{target_time}': {e}. Using as-is.")
            return target_time

    # Target is LESS specific than data - keep target as-is
    # Aggregation will happen during prediction
    else:
        print(
            f"ℹ️  Target time '{target_time}' is {label_granularity}, "
            f"data is {granularity}. Will aggregate data to match target."
        )
        return target_time


def get_granularity_from_label(label: str, date_format: str) -> str:
    """Determine granularity from a period label using MM-DD-YYYY format

    Args:
        label: Period label to analyze
        date_format: Date format from config (e.g., 'MM-DD-YYYY')

    Returns:
        Granularity string: 'yearly', 'quarterly', 'monthly', or 'daily'
    """
    if "-Q" in label:
        return "quarterly"
    elif len(label) == 10 and label.count("-") == 2:  # MM-DD-YYYY (e.g., 02-24-2025)
        return "daily"
    elif len(label) == 7 and label[2] == "-":  # MM-YYYY (e.g., 02-2025)
        return "monthly"
    elif len(label) == 4 and label.isdigit():  # YYYY
        return "yearly"
    else:
        return "monthly"  # Default
