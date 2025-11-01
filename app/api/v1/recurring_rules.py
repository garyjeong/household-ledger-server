"""
RecurringRules API Router
Recurring rule management endpoints
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status, Path, Body
from typing import Optional
from app.dependencies import get_current_user
from app.domain.models.user import User
from app.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.services.recurring_rule_service import RecurringRuleService
from app.application.services.recurring_scheduler_service import RecurringSchedulerService
from app.infrastructure.repositories.recurring_rule_repository_impl import RecurringRuleRepositoryImpl
from app.schemas.recurring_rule import (
    RecurringRuleCreateRequest,
    RecurringRuleUpdateRequest,
    RecurringRuleResponse,
    ProcessRecurringRulesRequest,
    GenerateTransactionRequest
)
from app.domain.models.recurring_rule import RecurringRule, RecurringFrequency
from datetime import date

router = APIRouter()


def get_recurring_rule_service(db: AsyncSession = Depends(get_session)) -> RecurringRuleService:
    """Dependency injection for RecurringRuleService"""
    repository = RecurringRuleRepositoryImpl(db)
    return RecurringRuleService(repository)


@router.get("", response_model=dict)
async def get_recurring_rules(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    group_id: Optional[int] = Query(None, description="Filter by group ID"),
    current_user: User = Depends(get_current_user),
    service: RecurringRuleService = Depends(get_recurring_rule_service)
):
    """Get all recurring rules for the current user"""
    try:
        rules = await service.get_recurring_rules(
            user_id=current_user.id,
            group_id=group_id,
            is_active=is_active
        )
        
        # Serialize rules
        serialized_rules = []
        for rule in rules:
            rule_dict = {
                "id": rule.id,
                "group_id": rule.group_id,
                "created_by": rule.created_by,
                "start_date": rule.start_date,
                "frequency": rule.frequency.value,
                "day_rule": rule.day_rule,
                "amount": rule.amount,
                "category_id": rule.category_id,
                "merchant": rule.merchant,
                "memo": rule.memo,
                "is_active": rule.is_active,
                "category": None,
                "group": None
            }
            
            if rule.category:
                rule_dict["category"] = {
                    "id": rule.category.id,
                    "name": rule.category.name,
                    "type": rule.category.type.value if hasattr(rule.category.type, 'value') else str(rule.category.type),
                    "color": rule.category.color
                }
            
            if rule.group:
                rule_dict["group"] = {
                    "id": rule.group.id,
                    "name": rule.group.name
                }
            
            serialized_rules.append(rule_dict)
        
        return {
            "success": True,
            "data": serialized_rules
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"반복 거래 규칙 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_recurring_rule(
    request: RecurringRuleCreateRequest,
    current_user: User = Depends(get_current_user),
    service: RecurringRuleService = Depends(get_recurring_rule_service),
    db: AsyncSession = Depends(get_session)
):
    """Create a new recurring rule"""
    try:
        # Get user's group_id
        group_id = current_user.group_id
        
        # Create recurring rule model
        recurring_rule = RecurringRule(
            group_id=group_id,
            created_by=current_user.id,
            start_date=request.start_date,
            frequency=request.frequency,
            day_rule=request.day_rule,
            amount=request.amount,
            category_id=request.category_id,
            merchant=request.merchant,
            memo=request.memo,
            is_active=True
        )
        
        # Validate category if provided
        if request.category_id:
            from app.domain.models.category import Category
            from sqlalchemy import select
            
            stmt = select(Category).where(Category.id == request.category_id)
            result = await db.execute(stmt)
            category = result.scalar_one_or_none()
            
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="존재하지 않는 카테고리입니다"
                )
        
        # Create rule
        created_rule = await service.create_recurring_rule(recurring_rule)
        
        # Refresh to get relationships
        await db.refresh(created_rule, ["category", "group"])
        
        # Serialize response
        rule_dict = {
            "id": created_rule.id,
            "group_id": created_rule.group_id,
            "created_by": created_rule.created_by,
            "start_date": created_rule.start_date,
            "frequency": created_rule.frequency.value,
            "day_rule": created_rule.day_rule,
            "amount": created_rule.amount,
            "category_id": created_rule.category_id,
            "merchant": created_rule.merchant,
            "memo": created_rule.memo,
            "is_active": created_rule.is_active,
            "category": None,
            "group": None
        }
        
        if created_rule.category:
            rule_dict["category"] = {
                "id": created_rule.category.id,
                "name": created_rule.category.name,
                "type": created_rule.category.type.value if hasattr(created_rule.category.type, 'value') else str(created_rule.category.type),
                "color": created_rule.category.color
            }
        
        if created_rule.group:
            rule_dict["group"] = {
                "id": created_rule.group.id,
                "name": created_rule.group.name
            }
        
        return {
            "success": True,
            "data": rule_dict
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"반복 거래 규칙 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{rule_id}", response_model=dict)
async def get_recurring_rule(
    rule_id: int = Path(..., description="Recurring rule ID"),
    current_user: User = Depends(get_current_user),
    service: RecurringRuleService = Depends(get_recurring_rule_service)
):
    """Get a specific recurring rule by ID"""
    try:
        rule = await service.get_recurring_rule(rule_id, current_user.id)
        
        # Serialize response
        rule_dict = {
            "id": rule.id,
            "group_id": rule.group_id,
            "created_by": rule.created_by,
            "start_date": rule.start_date,
            "frequency": rule.frequency.value,
            "day_rule": rule.day_rule,
            "amount": rule.amount,
            "category_id": rule.category_id,
            "merchant": rule.merchant,
            "memo": rule.memo,
            "is_active": rule.is_active,
            "category": None,
            "group": None
        }
        
        if rule.category:
            rule_dict["category"] = {
                "id": rule.category.id,
                "name": rule.category.name,
                "type": rule.category.type.value if hasattr(rule.category.type, 'value') else str(rule.category.type),
                "color": rule.category.color
            }
        
        if rule.group:
            rule_dict["group"] = {
                "id": rule.group.id,
                "name": rule.group.name
            }
        
        return {
            "success": True,
            "data": rule_dict
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"반복 거래 규칙 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/{rule_id}", response_model=dict)
async def update_recurring_rule(
    rule_id: int = Path(..., description="Recurring rule ID"),
    request: RecurringRuleUpdateRequest = ...,
    current_user: User = Depends(get_current_user),
    service: RecurringRuleService = Depends(get_recurring_rule_service)
):
    """Update a recurring rule"""
    try:
        updated_data = request.model_dump(exclude_unset=True)
        updated_rule = await service.update_recurring_rule(
            rule_id=rule_id,
            user_id=current_user.id,
            updated_data=updated_data
        )
        
        # Serialize response
        rule_dict = {
            "id": updated_rule.id,
            "group_id": updated_rule.group_id,
            "created_by": updated_rule.created_by,
            "start_date": updated_rule.start_date,
            "frequency": updated_rule.frequency.value,
            "day_rule": updated_rule.day_rule,
            "amount": updated_rule.amount,
            "category_id": updated_rule.category_id,
            "merchant": updated_rule.merchant,
            "memo": updated_rule.memo,
            "is_active": updated_rule.is_active,
            "category": None,
            "group": None
        }
        
        if updated_rule.category:
            rule_dict["category"] = {
                "id": updated_rule.category.id,
                "name": updated_rule.category.name,
                "type": updated_rule.category.type.value if hasattr(updated_rule.category.type, 'value') else str(updated_rule.category.type),
                "color": updated_rule.category.color
            }
        
        if updated_rule.group:
            rule_dict["group"] = {
                "id": updated_rule.group.id,
                "name": updated_rule.group.name
            }
        
        return {
            "success": True,
            "data": rule_dict
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"반복 거래 규칙 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_rule(
    rule_id: int = Path(..., description="Recurring rule ID"),
    current_user: User = Depends(get_current_user),
    service: RecurringRuleService = Depends(get_recurring_rule_service)
):
    """Delete a recurring rule"""
    try:
        await service.delete_recurring_rule(rule_id, current_user.id)
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"반복 거래 규칙 삭제 중 오류가 발생했습니다: {str(e)}"
        )


def get_recurring_scheduler_service(db: AsyncSession = Depends(get_session)) -> RecurringSchedulerService:
    """Dependency injection for RecurringSchedulerService"""
    return RecurringSchedulerService(db)


@router.post("/process", response_model=dict)
async def process_recurring_rules(
    request: ProcessRecurringRulesRequest = Body(default=ProcessRecurringRulesRequest()),
    current_user: User = Depends(get_current_user),
    scheduler: RecurringSchedulerService = Depends(get_recurring_scheduler_service)
):
    """
    Process recurring rules for a specific date or date range and generate transactions
    
    This endpoint processes all active recurring rules that match the criteria
    and automatically generates transactions.
    
    Supports:
    - Single date: process rules for one date
    - Date range: process rules for a range of dates (max 31 days)
    """
    try:
        from datetime import timedelta
        
        # Handle date range
        if hasattr(request, 'start_date') and hasattr(request, 'end_date'):
            if request.start_date and request.end_date:
                # Date range processing
                if request.start_date > request.end_date:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="시작 날짜는 종료 날짜보다 이전이어야 합니다"
                    )
                
                # Max 31 days
                days_diff = (request.end_date - request.start_date).days
                if days_diff > 31:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="처리 기간은 최대 31일까지만 가능합니다"
                    )
                
                # Process for each date in range
                current_date = request.start_date
                total_created = 0
                total_skipped = 0
                
                while current_date <= request.end_date:
                    result = await scheduler.process_recurring_rules(
                        target_date=current_date,
                        rule_id=request.rule_id,
                        user_id=current_user.id
                    )
                    total_created += result.get('created', 0)
                    total_skipped += result.get('skipped', 0)
                    current_date += timedelta(days=1)
                
                return {
                    "success": True,
                    "created": total_created,
                    "skipped": total_skipped,
                    "start_date": request.start_date.isoformat(),
                    "end_date": request.end_date.isoformat()
                }
        
        # Single date processing
        result = await scheduler.process_recurring_rules(
            target_date=request.target_date,
            rule_id=request.rule_id,
            user_id=current_user.id
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"반복 거래 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/{rule_id}/generate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def generate_transaction_from_rule(
    rule_id: int = Path(..., description="Recurring rule ID"),
    request: GenerateTransactionRequest = Body(...),
    current_user: User = Depends(get_current_user),
    scheduler: RecurringSchedulerService = Depends(get_recurring_scheduler_service)
):
    """
    Generate a single transaction from a specific recurring rule
    
    This endpoint creates one transaction based on the recurring rule for the specified date.
    """
    try:
        transaction = await scheduler.generate_transaction_from_rule(
            rule_id=rule_id,
            target_date=request.transaction_date,
            user_id=current_user.id
        )
        
        # Serialize transaction
        transaction_dict = {
            "id": transaction.id,
            "group_id": transaction.group_id,
            "owner_user_id": transaction.owner_user_id,
            "type": transaction.type.value if hasattr(transaction.type, 'value') else str(transaction.type),
            "date": transaction.date.isoformat(),
            "amount": transaction.amount,
            "category_id": transaction.category_id,
            "tag_id": transaction.tag_id,
            "merchant": transaction.merchant,
            "memo": transaction.memo,
            "created_at": transaction.created_at.isoformat(),
            "updated_at": transaction.updated_at.isoformat()
        }
        
        return {
            "success": True,
            "data": transaction_dict
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"거래 생성 중 오류가 발생했습니다: {str(e)}"
        )

