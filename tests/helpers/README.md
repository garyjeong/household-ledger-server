# Test Helpers

이 디렉토리는 테스트 코드에서 사용할 수 있는 헬퍼 함수들과 모킹 데이터를 제공합니다.

## 구조

- `test_data_factory.py`: 테스트용 모델 인스턴스를 생성하는 팩토리 함수들
- `mock_helpers.py`: Mock 객체를 생성하는 헬퍼 함수들
- `fixture_helpers.py`: pytest fixture들을 정의하는 파일
- `date_helpers.py`: 날짜 관련 헬퍼 함수들

## 사용 예시

### Test Data Factory 사용

```python
from tests.helpers.test_data_factory import create_test_user, create_test_transaction

# 테스트용 사용자 생성
user = create_test_user(
    user_id=1,
    email="test@example.com",
    nickname="TestUser"
)

# 테스트용 거래 생성
transaction = create_test_transaction(
    owner_user_id=1,
    amount=10000,
    memo="Test"
)
```

### Mock Helpers 사용

```python
from tests.helpers.mock_helpers import create_mock_session, create_mock_repository

# Mock 세션 생성
mock_session = create_mock_session()

# Mock 리포지토리 생성
mock_repo = create_mock_repository("TransactionRepository")
```

### Date Helpers 사용

```python
from tests.helpers.date_helpers import get_current_month_start, get_date_range_for_period

# 현재 월 시작일
start_date = get_current_month_start()

# 기간별 날짜 범위
start, end = get_date_range_for_period("current-month")
```

### Fixtures 사용

```python
def test_something(sample_user, sample_transaction):
    # pytest fixture를 통해 테스트 데이터 사용
    assert sample_user.email == "sample@example.com"
```

## Sample Data

자주 사용하는 샘플 데이터는 `test_data_factory.py`의 상수로 정의되어 있습니다:

- `SAMPLE_USER_DATA`
- `SAMPLE_TRANSACTION_DATA`
- `SAMPLE_CATEGORY_DATA`
- `SAMPLE_GROUP_DATA`
- `SAMPLE_BUDGET_DATA`
- `SAMPLE_RECURRING_RULE_DATA`
- `SAMPLE_SETTINGS_DATA`

