"""
Unit Tests for DashboardService
"""

import pytest
from unittest.mock import AsyncMock
from datetime import date
from app.application.services.dashboard_service import DashboardService


@pytest.fixture
def mock_statistics_repo():
    """Mock statistics repository"""
    return AsyncMock()


@pytest.fixture
def dashboard_service(mock_statistics_repo):
    """DashboardService with mocked repository"""
    return DashboardService(repository=mock_statistics_repo)


@pytest.mark.asyncio
async def test_get_monthly_stats_success(dashboard_service, mock_statistics_repo):
    """Test successful monthly stats retrieval"""
    # Arrange
    mock_stats = {
        "total_income": 1000000,
        "total_expense": 600000,
        "top_categories": [
            {"category_id": 1, "category_name": "식비", "amount": 300000},
            {"category_id": 2, "category_name": "교통비", "amount": 200000}
        ],
        "daily_trend": [
            {"date": "2025-01-01", "income": 100000, "expense": 50000},
            {"date": "2025-01-02", "income": 150000, "expense": 75000}
        ]
    }
    
    mock_statistics_repo.get_monthly_stats.return_value = mock_stats
    
    # Act
    result = await dashboard_service.get_optimized_monthly_stats(
        user_id=1,
        year=2025,
        month=1,
        group_id=None
    )
    
    # Assert
    assert "total_income" in result
    assert "total_expense" in result
    assert "top_categories" in result
    assert "daily_trend" in result
    assert result["total_income"] == 1000000
    mock_statistics_repo.get_monthly_stats.assert_called_once()


@pytest.mark.asyncio
async def test_get_monthly_stats_default_month(dashboard_service, mock_statistics_repo):
    """Test monthly stats with default month (current)"""
    # Arrange
    mock_stats = {
        "total_income": 1000000,
        "total_expense": 600000,
        "top_categories": [],
        "daily_trend": []
    }
    
    mock_statistics_repo.get_monthly_stats.return_value = mock_stats
    
    # Act
    result = await dashboard_service.get_optimized_monthly_stats(
        user_id=1,
        year=None,
        month=None,
        group_id=None
    )
    
    # Assert
    assert "total_income" in result
    mock_statistics_repo.get_monthly_stats.assert_called_once()

