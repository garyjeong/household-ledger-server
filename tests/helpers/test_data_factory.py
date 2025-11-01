"""
Test Data Factory
Factory functions for creating test model instances
"""

from datetime import date, datetime, timedelta
from typing import Optional
from app.domain.models.user import User
from app.domain.models.transaction import Transaction, TransactionType
from app.domain.models.category import Category
from app.domain.models.group import Group
from app.domain.models.budget import Budget, OwnerType, BudgetStatus
from app.domain.models.recurring_rule import RecurringRule, RecurringFrequency
from app.domain.models.tag import Tag
from app.infrastructure.security.password_hasher import hash_password


def create_test_user(
    user_id: Optional[int] = None,
    email: str = "test@example.com",
    password: str = "password123",
    nickname: str = "TestUser",
    group_id: Optional[int] = None,
    settings: Optional[dict] = None
) -> User:
    """Create a test user instance"""
    return User(
        id=user_id,
        email=email,
        password_hash=hash_password(password),
        nickname=nickname,
        group_id=group_id,
        settings=settings,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def create_test_transaction(
    transaction_id: Optional[int] = None,
    owner_user_id: int = 1,
    group_id: Optional[int] = None,
    transaction_type: TransactionType = TransactionType.EXPENSE,
    amount: int = 10000,
    category_id: Optional[int] = 1,
    tag_id: Optional[int] = None,
    merchant: Optional[str] = "테스트 상점",
    memo: Optional[str] = "테스트 거래",
    transaction_date: Optional[date] = None
) -> Transaction:
    """Create a test transaction instance"""
    return Transaction(
        id=transaction_id,
        owner_user_id=owner_user_id,
        group_id=group_id,
        type=transaction_type.value,
        date=transaction_date or date.today(),
        amount=amount,
        category_id=category_id,
        tag_id=tag_id,
        merchant=merchant,
        memo=memo,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def create_test_category(
    category_id: Optional[int] = None,
    name: str = "테스트 카테고리",
    category_type: str = "EXPENSE",
    color: str = "#FF5733",
    icon: Optional[str] = "🍔",
    group_id: Optional[int] = None,
    created_by: int = 1,
    is_default: bool = False,
    budget_amount: int = 0
) -> Category:
    """Create a test category instance"""
    return Category(
        id=category_id,
        name=name,
        type=category_type,
        color=color,
        icon=icon,
        group_id=group_id,
        created_by=created_by,
        is_default=is_default,
        budget_amount=budget_amount,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def create_test_group(
    group_id: Optional[int] = None,
    name: str = "테스트 그룹",
    owner_id: int = 1,
    description: Optional[str] = None
) -> Group:
    """Create a test group instance"""
    return Group(
        id=group_id,
        name=name,
        owner_id=owner_id,
        description=description,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def create_test_budget(
    budget_id: Optional[int] = None,
    owner_type: OwnerType = OwnerType.USER,
    owner_id: int = 1,
    period: str = "2025-01",
    total_amount: int = 1000000,
    status: BudgetStatus = BudgetStatus.ACTIVE
) -> Budget:
    """Create a test budget instance"""
    return Budget(
        id=budget_id,
        owner_type=owner_type,
        owner_id=owner_id,
        period=period,
        total_amount=total_amount,
        status=status,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def create_test_recurring_rule(
    rule_id: Optional[int] = None,
    created_by: int = 1,
    group_id: Optional[int] = None,
    category_id: Optional[int] = 1,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    frequency: RecurringFrequency = RecurringFrequency.MONTHLY,
    day_rule: str = "1",
    amount: int = 100000,
    merchant: Optional[str] = "반복 거래 상점",
    memo: Optional[str] = "반복 거래 메모",
    is_active: bool = True
) -> RecurringRule:
    """Create a test recurring rule instance"""
    return RecurringRule(
        id=rule_id,
        created_by=created_by,
        group_id=group_id,
        category_id=category_id,
        start_date=start_date or date.today(),
        end_date=end_date,
        frequency=frequency,
        day_rule=day_rule,
        amount=amount,
        merchant=merchant,
        memo=memo,
        is_active=is_active,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def create_test_tag(
    tag_id: Optional[int] = None,
    name: str = "테스트 태그",
    color: str = "#33FF57",
    group_id: Optional[int] = None,
    created_by: int = 1
) -> Tag:
    """Create a test tag instance"""
    return Tag(
        id=tag_id,
        name=name,
        color=color,
        group_id=group_id,
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


# Bulk creation helpers
def create_test_users(count: int = 5, start_id: int = 1) -> list[User]:
    """Create multiple test users"""
    return [
        create_test_user(
            user_id=start_id + i,
            email=f"user{i}@example.com",
            nickname=f"User{i}"
        )
        for i in range(count)
    ]


def create_test_transactions(
    count: int = 10,
    owner_user_id: int = 1,
    start_date: Optional[date] = None
) -> list[Transaction]:
    """Create multiple test transactions"""
    base_date = start_date or date.today()
    transactions = []
    
    for i in range(count):
        transaction_date = base_date - timedelta(days=i)
        transaction_type = TransactionType.EXPENSE if i % 2 == 0 else TransactionType.INCOME
        
        transactions.append(
            create_test_transaction(
                transaction_id=i + 1,
                owner_user_id=owner_user_id,
                transaction_type=transaction_type,
                amount=10000 * (i + 1),
                memo=f"테스트 거래 {i + 1}",
                transaction_date=transaction_date
            )
        )
    
    return transactions


def create_test_categories(
    count: int = 5,
    category_type: str = "EXPENSE",
    created_by: int = 1
) -> list[Category]:
    """Create multiple test categories"""
    category_names = ["식비", "교통비", "쇼핑", "의료", "교육", "문화", "여행", "기타"]
    colors = ["#FF5733", "#33FF57", "#3357FF", "#FF33F5", "#F5FF33", "#33FFF5", "#FF9533", "#9533FF"]
    
    return [
        create_test_category(
            category_id=i + 1,
            name=category_names[i % len(category_names)],
            category_type=category_type,
            color=colors[i % len(colors)],
            created_by=created_by
        )
        for i in range(min(count, len(category_names)))
    ]


# Sample data dictionaries for API testing
SAMPLE_USER_DATA = {
    "email": "test@example.com",
    "password": "password123",
    "nickname": "TestUser"
}


SAMPLE_TRANSACTION_DATA = {
    "type": "EXPENSE",
    "date": str(date.today()),
    "amount": 10000,
    "category_id": 1,
    "memo": "Test transaction"
}


SAMPLE_CATEGORY_DATA = {
    "name": "식비",
    "type": "EXPENSE",
    "color": "#FF5733",
    "icon": "🍔"
}


SAMPLE_GROUP_DATA = {
    "name": "테스트 그룹",
    "description": "테스트용 그룹입니다"
}


SAMPLE_BUDGET_DATA = {
    "owner_type": "USER",
    "period": "2025-01",
    "total_amount": 1000000,
    "status": "ACTIVE"
}


SAMPLE_RECURRING_RULE_DATA = {
    "start_date": str(date.today()),
    "frequency": "MONTHLY",
    "day_rule": "1",
    "amount": 100000,
    "category_id": 1,
    "memo": "Monthly expense"
}


SAMPLE_SETTINGS_DATA = {
    "currency": "KRW",
    "theme": "light",
    "language": "ko",
    "enable_notifications": True,
    "budget_alerts": True
}


SAMPLE_UPDATE_SETTINGS_DATA = {
    "currency": "USD",
    "theme": "dark",
    "language": "en"
}

