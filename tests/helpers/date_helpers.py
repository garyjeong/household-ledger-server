"""
Date Helpers
Helper functions for date manipulation in tests
"""

from datetime import date, datetime, timedelta
from typing import Optional


def get_current_month_start() -> date:
    """Get the first day of the current month"""
    today = date.today()
    return date(today.year, today.month, 1)


def get_current_month_end() -> date:
    """Get the last day of the current month"""
    today = date.today()
    if today.month == 12:
        return date(today.year + 1, 1, 1) - timedelta(days=1)
    return date(today.year, today.month + 1, 1) - timedelta(days=1)


def get_last_month_start() -> date:
    """Get the first day of last month"""
    today = date.today()
    if today.month == 1:
        return date(today.year - 1, 12, 1)
    return date(today.year, today.month - 1, 1)


def get_last_month_end() -> date:
    """Get the last day of last month"""
    today = date.today()
    if today.month == 1:
        return date(today.year - 1, 12, 31)
    return date(today.year, today.month, 1) - timedelta(days=1)


def get_date_range_for_period(period: str) -> tuple[date, date]:
    """
    Get date range for a period string
    
    Args:
        period: Period string like "current-month", "last-month", "2025-01"
    
    Returns:
        Tuple of (start_date, end_date)
    """
    if period == "current-month":
        return get_current_month_start(), get_current_month_end()
    elif period == "last-month":
        return get_last_month_start(), get_last_month_end()
    elif period == "last-3-months":
        end_date = get_current_month_end()
        start_date = end_date - timedelta(days=90)
        return start_date, end_date
    elif period == "last-6-months":
        end_date = get_current_month_end()
        start_date = end_date - timedelta(days=180)
        return start_date, end_date
    elif period == "year":
        today = date.today()
        start_date = date(today.year, 1, 1)
        end_date = date(today.year, 12, 31)
        return start_date, end_date
    elif len(period) == 7 and period[4] == "-":  # Format: YYYY-MM
        year, month = map(int, period.split("-"))
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        return start_date, end_date
    
    # Default: current month
    return get_current_month_start(), get_current_month_end()


def create_date_range(start_date: date, days: int) -> list[date]:
    """Create a list of dates for a range"""
    return [start_date + timedelta(days=i) for i in range(days)]


def get_n_days_ago(n: int) -> date:
    """Get date n days ago"""
    return date.today() - timedelta(days=n)


def get_n_months_ago(n: int) -> date:
    """Get date n months ago"""
    today = date.today()
    year = today.year
    month = today.month - n
    
    while month <= 0:
        month += 12
        year -= 1
    
    return date(year, month, today.day)


def format_date_for_api(d: date) -> str:
    """Format date as ISO string for API"""
    return d.isoformat()


def parse_date_from_string(date_string: str) -> date:
    """Parse date from ISO string"""
    return datetime.fromisoformat(date_string).date()

