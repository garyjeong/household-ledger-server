"""
Mock Helpers
Helper functions for creating mocks in tests
"""

from unittest.mock import AsyncMock, Mock, MagicMock
from typing import Optional, Any
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result


def create_mock_session() -> AsyncMock:
    """Create a mock AsyncSession"""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = Mock()
    mock_session.delete = Mock()
    mock_session.merge = AsyncMock()
    return mock_session


def create_mock_result(scalars_value: Any = None, scalar_one_value: Any = None) -> AsyncMock:
    """Create a mock result object"""
    mock_result = AsyncMock(spec=Result)
    
    if scalars_value is not None:
        mock_scalars = AsyncMock()
        mock_scalars.all.return_value = scalars_value if isinstance(scalars_value, list) else [scalars_value]
        mock_scalars.first.return_value = scalars_value if not isinstance(scalars_value, list) else (scalars_value[0] if scalars_value else None)
        mock_scalars.one.return_value = scalars_value if not isinstance(scalars_value, list) else scalars_value[0]
        mock_result.scalars.return_value = mock_scalars
    
    if scalar_one_value is not None:
        mock_result.scalar_one_or_none.return_value = scalar_one_value
        mock_result.scalar_one.return_value = scalar_one_value
        mock_result.scalar.return_value = scalar_one_value
    
    return mock_result


def create_mock_repository(repository_class_name: str) -> AsyncMock:
    """Create a mock repository with common methods"""
    mock_repo = AsyncMock()
    
    # Common repository methods
    mock_repo.find_by_id = AsyncMock()
    mock_repo.find_all = AsyncMock(return_value=[])
    mock_repo.create = AsyncMock()
    mock_repo.update = AsyncMock()
    mock_repo.delete = AsyncMock()
    mock_repo.count_total = AsyncMock(return_value=0)
    
    return mock_repo


def setup_mock_session_for_query(
    mock_session: AsyncMock,
    query_result: Any,
    method: str = "scalar_one_or_none"
):
    """Setup mock session to return specific query result"""
    mock_result = create_mock_result()
    
    if method == "scalar_one_or_none":
        mock_result.scalar_one_or_none.return_value = query_result
    elif method == "scalar_one":
        mock_result.scalar_one.return_value = query_result
    elif method == "scalars_all":
        mock_scalars = AsyncMock()
        if isinstance(query_result, list):
            mock_scalars.all.return_value = query_result
        else:
            mock_scalars.all.return_value = [query_result]
        mock_result.scalars.return_value = mock_scalars
    elif method == "scalars_first":
        mock_scalars = AsyncMock()
        if isinstance(query_result, list) and len(query_result) > 0:
            mock_scalars.first.return_value = query_result[0]
        else:
            mock_scalars.first.return_value = query_result
        mock_result.scalars.return_value = mock_scalars
    
    mock_session.execute.return_value = mock_result
    return mock_session


def setup_mock_session_for_multiple_queries(
    mock_session: AsyncMock,
    query_results: list[Any]
):
    """Setup mock session to return different results for multiple queries"""
    mock_results = []
    for result in query_results:
        mock_result = create_mock_result()
        
        if isinstance(result, list):
            mock_scalars = AsyncMock()
            mock_scalars.all.return_value = result
            mock_result.scalars.return_value = mock_scalars
        else:
            mock_result.scalar_one_or_none.return_value = result
        
        mock_results.append(mock_result)
    
    mock_session.execute.side_effect = mock_results
    return mock_session


def create_mock_statistics_repository() -> AsyncMock:
    """Create a mock statistics repository"""
    mock_repo = AsyncMock()
    
    mock_repo.get_summary_statistics = AsyncMock(return_value={
        "total_income": 1000000,
        "total_expense": 500000,
        "net_amount": 500000,
        "transaction_count": 10
    })
    
    mock_repo.get_category_statistics = AsyncMock(return_value=[
        {"category_id": 1, "category_name": "식비", "amount": 300000},
        {"category_id": 2, "category_name": "교통비", "amount": 200000}
    ])
    
    mock_repo.get_daily_trend = AsyncMock(return_value=[
        {"date": "2025-01-01", "income": 100000, "expense": 50000},
        {"date": "2025-01-02", "income": 150000, "expense": 75000}
    ])
    
    mock_repo.get_monthly_comparison = AsyncMock(return_value=[
        {"month": "2025-01", "income": 1000000, "expense": 500000},
        {"month": "2025-02", "income": 1200000, "expense": 600000}
    ])
    
    return mock_repo


def create_mock_balance_repository() -> AsyncMock:
    """Create a mock balance repository"""
    mock_repo = AsyncMock()
    
    mock_repo.calculate_balance = AsyncMock(return_value=500000)
    mock_repo.get_amount_by_type = AsyncMock(return_value=1000000)
    mock_repo.get_monthly_trend = AsyncMock(return_value=[
        {"month": "2025-01", "balance": 500000, "income": 1000000, "expense": 500000},
        {"month": "2025-02", "balance": 600000, "income": 1200000, "expense": 600000}
    ])
    
    return mock_repo


def create_mock_auth_repository() -> AsyncMock:
    """Create a mock auth repository"""
    mock_repo = AsyncMock()
    
    mock_repo.find_user_by_email = AsyncMock(return_value=None)
    mock_repo.find_user_by_id = AsyncMock(return_value=None)
    mock_repo.create_user = AsyncMock()
    mock_repo.update_user = AsyncMock()
    
    return mock_repo


def create_mock_transaction_repository() -> AsyncMock:
    """Create a mock transaction repository"""
    mock_repo = AsyncMock()
    
    mock_repo.find_by_id = AsyncMock(return_value=None)
    mock_repo.find_all = AsyncMock(return_value=[])
    mock_repo.create = AsyncMock()
    mock_repo.update = AsyncMock()
    mock_repo.delete = AsyncMock()
    mock_repo.count_total = AsyncMock(return_value=0)
    
    return mock_repo


def create_mock_category_repository() -> AsyncMock:
    """Create a mock category repository"""
    mock_repo = AsyncMock()
    
    mock_repo.find_by_id = AsyncMock(return_value=None)
    mock_repo.find_all = AsyncMock(return_value=[])
    mock_repo.create = AsyncMock()
    mock_repo.update = AsyncMock()
    mock_repo.delete = AsyncMock()
    
    return mock_repo


def create_mock_group_repository() -> AsyncMock:
    """Create a mock group repository"""
    mock_repo = AsyncMock()
    
    mock_repo.find_by_id = AsyncMock(return_value=None)
    mock_repo.find_user_groups = AsyncMock(return_value=[])
    mock_repo.create = AsyncMock()
    mock_repo.update = AsyncMock()
    mock_repo.delete = AsyncMock()
    
    return mock_repo


def create_mock_budget_repository() -> AsyncMock:
    """Create a mock budget repository"""
    mock_repo = AsyncMock()
    
    mock_repo.find_by_id = AsyncMock(return_value=None)
    mock_repo.find_all = AsyncMock(return_value=[])
    mock_repo.find_by_period = AsyncMock(return_value=None)
    mock_repo.create = AsyncMock()
    mock_repo.update = AsyncMock()
    mock_repo.delete = AsyncMock()
    
    return mock_repo


def create_mock_recurring_rule_repository() -> AsyncMock:
    """Create a mock recurring rule repository"""
    mock_repo = AsyncMock()
    
    mock_repo.find_by_id = AsyncMock(return_value=None)
    mock_repo.find_all = AsyncMock(return_value=[])
    mock_repo.create = AsyncMock()
    mock_repo.update = AsyncMock()
    mock_repo.delete = AsyncMock()
    
    return mock_repo


# Common test responses
def get_success_response(data: Any = None, message: str = "Success") -> dict:
    """Create a standard success response"""
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response


def get_error_response(message: str = "Error", code: Optional[str] = None) -> dict:
    """Create a standard error response"""
    response = {
        "success": False,
        "message": message
    }
    if code:
        response["code"] = code
    return response


def get_paginated_response(
    items: list,
    total: int,
    limit: int = 50,
    offset: int = 0
) -> dict:
    """Create a standard paginated response"""
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + len(items)) < total
    }

