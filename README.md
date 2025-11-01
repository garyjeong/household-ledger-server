# Household Ledger API

신혼부부 가계부 서비스 백엔드 API (FastAPI)

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MySQL 8.4+
- Docker (optional)

### Local Development

#### 1. 가상환경 설정
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
```

#### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

#### 3. 데이터베이스 설정
```bash
# Docker로 데이터베이스 실행
cd docker
./start-db.sh

# 또는 docker-compose 사용
docker-compose up -d db
```

#### 4. 환경 변수 설정
```bash
cp env.template .env
# .env 파일 편집
```

#### 5. 데이터베이스 마이그레이션
```bash
alembic upgrade head
```

#### 6. 서버 실행
```bash
uvicorn app.main:app --reload
```

서버는 `http://localhost:8000`에서 실행됩니다.

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 프로젝트 구조

```
app/
├── api/v1/          # API 라우터
├── domain/          # 도메인 계층
│   ├── models/      # ORM 모델
│   └── repositories/ # Repository 인터페이스
├── application/     # 애플리케이션 계층
│   ├── services/    # 비즈니스 로직
│   └── factories/   # 팩토리 패턴
├── infrastructure/  # 인프라 계층
│   ├── repositories/ # Repository 구현체
│   └── security/    # 보안 유틸리티
├── schemas/         # Pydantic 스키마
└── utils/           # 유틸리티

docker/              # Docker 설정
alembic/             # 데이터베이스 마이그레이션
tests/               # 테스트 파일
```

## 🔐 환경 변수

`.env` 파일 설정:

```env
DATABASE_URL=mysql+pymysql://gary:wjdwhdans@localhost:3306/household_ledger
JWT_SECRET=your-secret-key-change-in-production
JWT_REFRESH_SECRET=your-refresh-secret-change-in-production
```

## 📝 API 엔드포인트

### 🔐 인증 (Auth) - `/api/v1/auth`
- `POST /signup` - 회원가입
- `POST /login` - 로그인  
- `POST /refresh` - 토큰 갱신
- `GET /me` - 현재 사용자 정보
- `POST /change-password` - 비밀번호 변경
- `GET /check-email` - 이메일 중복 체크

### 👥 그룹 (Groups) - `/api/v1/groups`
- `GET /` - 그룹 목록 조회
- `POST /` - 그룹 생성
- `GET /{group_id}` - 그룹 조회
- `PUT /{group_id}` - 그룹 수정
- `DELETE /{group_id}` - 그룹 삭제
- `POST /{group_id}/invite` - 초대 코드 생성
- `POST /join` - 그룹 참여 (초대 코드로)
- `POST /leave` - 그룹 탈퇴

### 💰 거래 (Transactions) - `/api/v1/transactions`
- `GET /` - 거래 목록 조회 (필터링, 페이징)
- `POST /` - 거래 생성
- `GET /{transaction_id}` - 거래 조회
- `PUT /{transaction_id}` - 거래 수정
- `DELETE /{transaction_id}` - 거래 삭제

### 📂 카테고리 (Categories) - `/api/v1/categories`
- `GET /` - 카테고리 목록 조회
- `POST /` - 카테고리 생성
- `PUT /{category_id}` - 카테고리 수정
- `DELETE /{category_id}` - 카테고리 삭제

### 📊 통계 (Statistics) - `/api/v1/statistics`
- `GET /` - 종합 통계 조회
  - 요약 통계 (총 수입, 지출, 순이익, 거래 건수)
  - 카테고리별 통계 (수입/지출)
  - 일별 트렌드 데이터
  - 월별 비교 (최근 6개월)
  - 기간 필터: `current-month`, `last-month`, `last-3-months`, `last-6-months`, `year`

### 📈 대시보드 (Dashboard) - `/api/v1/dashboard`
- `GET /monthly-stats` - 월별 대시보드 통계
  - 월별 수입/지출 총액
  - 상위 5개 지출 카테고리
  - 일별 트렌드

### 🔄 반복 거래 (RecurringRules) - `/api/v1/recurring-rules`
- `GET /` - 반복 거래 규칙 목록 조회
- `POST /` - 반복 거래 규칙 생성
- `GET /{rule_id}` - 반복 거래 규칙 조회
- `PUT /{rule_id}` - 반복 거래 규칙 수정
- `DELETE /{rule_id}` - 반복 거래 규칙 삭제
- `POST /process` - 반복 거래 규칙 일괄 처리 (자동 거래 생성)
- `POST /{rule_id}/generate` - 특정 규칙에서 거래 생성

### 💰 예산 (Budgets) - `/api/v1/budgets`
- `GET /` - 예산 목록 조회
- `POST /` - 예산 생성/수정 (월별)
- `GET /status` - 예산 현황 조회 (예산 대비 지출)
- `GET /{budget_id}` - 예산 조회
- `PUT /{budget_id}` - 예산 수정
- `DELETE /{budget_id}` - 예산 삭제

## 🧪 Testing

```bash
# 전체 테스트 실행
pytest

# 커버리지 포함
pytest --cov=app tests/

# 특정 테스트만 실행
pytest tests/unit/test_auth_service.py
```

## 🐳 Docker Deployment

### Docker Compose 사용
```bash
docker-compose up -d
```

### 개별 Docker 빌드
```bash
docker build -t household-ledger-api .
docker run -p 8000:8000 household-ledger-api
```

## 📊 데이터베이스

### 마이그레이션
```bash
# 마이그레이션 생성
alembic revision --autogenerate -m "description"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.115+
- **ORM**: SQLAlchemy 2.0+
- **Database**: MySQL 8.4
- **Authentication**: JWT (python-jose)
- **Password Hashing**: BCrypt (passlib)
- **Validation**: Pydantic v2
- **Migration**: Alembic
- **Testing**: pytest, pytest-asyncio
- **Architecture**: Clean Architecture + Repository Pattern

## 🏗️ 아키텍처

### Clean Architecture (계층 분리)
- **Domain Layer**: 비즈니스 규칙 (모델, Repository 인터페이스)
- **Application Layer**: Use Cases (Service, Factory)
- **Infrastructure Layer**: 기술 구현 (Repository 구현체, Security)
- **API Layer**: HTTP 엔드포인트 (Router)

### 설계 원칙
- **SOLID 원칙** 준수
- **Repository 패턴**: 데이터 접근 추상화
- **Dependency Injection**: FastAPI Depends 활용
- **ORM 중심**: SQLAlchemy 2.0+ 활용
- **TDD**: 테스트 주도 개발

## 📊 구현 현황

✅ **완료된 작업**
- 9개 ORM 모델 (Users, Groups, Transactions, Categories, RecurringRules, Budgets, etc.)
- 9개 Repository 인터페이스 및 구현체 (Auth, Group, Transaction, Category, Statistics, RecurringRule, Budget)
- 8개 Service (Auth, Group, Transaction, Category, Statistics, Dashboard, RecurringRule, RecurringScheduler, Budget)
- 40개+ API 엔드포인트 (인증, 그룹, 거래, 카테고리, 통계, 대시보드, 반복 거래, 예산)
- JWT 인증 시스템
- 데이터베이스 마이그레이션
- Swagger 문서화
- 통계 및 대시보드 최적화된 쿼리
- 반복 거래 자동 생성 스케줄러
- 예산 관리 및 현황 조회

## 📄 License

MIT
