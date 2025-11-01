"""
Transaction API Router
Transaction management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.transaction import (
    TransactionCreateRequest,
    TransactionUpdateRequest,
    TransactionResponse,
    TransactionFilters,
    PaginatedResponse
)
from app.dependencies import get_transaction_service, get_current_user
from app.application.services.transaction_service import TransactionService
from app.domain.models.user import User
from app.domain.models.transaction import Transaction as TransactionModel
from datetime import datetime, date
from typing import Optional

router = APIRouter()

# Include quick-add router
try:
    from app.api.v1.transactions.quick_add import router as quick_add_router
    router.include_router(quick_add_router, prefix="/quick-add", tags=["Transactions"])
except ImportError:
    # Quick-add router not available, skip
    pass


@router.get("", response_model=PaginatedResponse)
async def get_transactions(
    group_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None, description="Search in memo and merchant"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    """Get transactions with filters and pagination"""
    transactions, total = await service.get_transactions(
        group_id=group_id,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        search=search,
        limit=limit,
        offset=offset
    )
    return PaginatedResponse(
        items=transactions,
        total=total,
        limit=limit,
        offset=offset
    )


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    request: TransactionCreateRequest,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    """Create new transaction"""
    transaction = TransactionModel(
        owner_user_id=current_user.id,
        group_id=request.group_id,
        type=request.type.value,
        date=request.date,
        amount=request.amount,
        category_id=request.category_id,
        tag_id=request.tag_id,
        merchant=request.merchant,
        memo=request.memo
    )
    try:
        result = await service.create_transaction(transaction)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    """Get transaction by ID"""
    try:
        transaction = await service.get_transaction(transaction_id, current_user.id)
        return transaction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    request: TransactionUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    """Update transaction"""
    # Convert to dict, filtering None values
    update_data = {k: v for k, v in request.dict().items() if v is not None}
    
    try:
        transaction = await service.update_transaction(
            transaction_id,
            current_user.id,
            update_data
        )
        return transaction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    """Delete transaction"""
    try:
        await service.delete_transaction(transaction_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

