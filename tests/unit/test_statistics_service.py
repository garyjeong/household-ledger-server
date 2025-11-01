"""
Unit Tests for StatisticsService
"""

import pytest
from unittest.mock import AsyncMock
from datetime import date
from app.application.services.statistics_service import StatisticsService


@pytest.fixture
def mock_statistics_repo():
    """Mock statistics repository"""
    return AsyncMock()


@pytest.fixture
def statistics_service(mock_statistics_repo):
    """StatisticsService with mocked repository"""
    return StatisticsService(repository=mock_statistics_repo)


@pytest.mark.asyncio
async def test_get_statistics_current_month(statistics_service, mock_statistics_repo):
    """Test getting statistics for current month"""
    # Arrange
    mock_summary = {
        'total_income': 1000000,
        'total_expense': 500000,
        'net_amount': 500000,
        'transaction_count': 10
    }
    
    mock_category_stats = [
        {'category_id': 1, 'category_name': '식비', 'amount': 300000},
        {'category_id': 2, 'category_name': '교통비', 'amount': 200000}
    ]
    
    mock_daily_trend = [
        {'date': '2025-01-01', 'income': 100000, 'expense': 50000},
        {'date': '2025-01-02', 'income': 150000, 'expense': 75000}
    ]
    
    mock_monthly_comparison = [
        {'month': '2025-01', 'income': 1000000, 'expense': 500000},
        {'month': '2025-02', 'income': 1200000, 'expense': 600000}
    ]
    
    mock_statistics_repo.get_summary_statistics.return_value = mock_summary
    mock_statistics_repo.get_category_statistics.return_value = mock_category_stats
    mock_statistics_repo.get_daily_trend.return_value = mock_daily_trend
    mock_statistics_repo.get_monthly_comparison.return_value = mock_monthly_comparison
    
    # Act
    result = await statistics_service.get_statistics(
        user_id=1,
        period='current-month'
    )
    
    # Assert
    assert 'summary' in result
    assert 'category_statistics' in result
    assert 'daily_trend' in result
    assert 'monthly_comparison' in result
    assert result['summary']['total_income'] == 1000000
    mock_statistics_repo.get_summary_statistics.assert_called_once()


@pytest.mark.asyncio
async def test_calculate_date_range_current_month(statistics_service):
    """Test date range calculation for current month"""
    # Act
    start_date, end_date = statistics_service.calculate_date_range('current-month')
    
    # Assert
    assert isinstance(start_date, date)
    assert isinstance(end_date, date)
    assert start_date <= end_date


@pytest.mark.asyncio
async def test_calculate_date_range_last_month(statistics_service):
    """Test date range calculation for last month"""
    # Act
    start_date, end_date = statistics_service.calculate_date_range('last-month')
    
    # Assert
    assert isinstance(start_date, date)
    assert isinstance(end_date, date)
    assert start_date <= end_date


@pytest.mark.asyncio
async def test_calculate_date_range_last_3_months(statistics_service):
    """Test date range calculation for last 3 months"""
    # Act
    start_date, end_date = statistics_service.calculate_date_range('last-3-months')
    
    # Assert
    assert isinstance(start_date, date)
    assert isinstance(end_date, date)
    # Should span approximately 3 months
    days_diff = (end_date - start_date).days
    assert days_diff >= 85  # Approx 3 months


@pytest.mark.asyncio
async def test_get_statistics_custom_dates(statistics_service, mock_statistics_repo):
    """Test getting statistics with custom date range"""
    # Arrange
    start_date = date(2025, 1, 1)
    end_date = date(2025, 1, 31)
    
    mock_statistics_repo.get_summary_statistics.return_value = {
        'total_income': 1000000,
        'total_expense': 500000
    }
    mock_statistics_repo.get_category_statistics.return_value = []
    mock_statistics_repo.get_daily_trend.return_value = []
    mock_statistics_repo.get_monthly_comparison.return_value = []
    
    # Act
    result = await statistics_service.get_statistics(
        user_id=1,
        start_date=start_date,
        end_date=end_date
    )
    
    # Assert
    assert 'summary' in result
    mock_statistics_repo.get_summary_statistics.assert_called_once()

