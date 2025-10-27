# Docker 설정 가이드

가계부 서버의 Docker 컨테이너 설정

## 📁 폴더 구조

```
docker/
├── database/        # MySQL 데이터베이스 설정
│   ├── Dockerfile.mysql
│   ├── init.sql
│   └── start-db.sh
├── server/          # FastAPI 서버 설정
│   ├── Dockerfile
│   └── .dockerignore
└── README.md        # 이 파일
```

---

## 🗄️ Database 설정 (docker/database/)

### 빠른 시작

```bash
cd docker/database
./start-db.sh
```

### 수동 실행

```bash
cd docker/database

# 1. Docker 이미지 빌드
docker build -t household-ledger-mysql:latest -f Dockerfile.mysql .

# 2. 컨테이너 실행
docker run -d \
  --name household-ledger-db \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=wjdwhdans \
  -e MYSQL_DATABASE=household_ledger \
  -e MYSQL_USER=gary \
  -e MYSQL_PASSWORD=wjdwhdans \
  household-ledger-mysql:latest
```

### 연결 정보

- **Host**: `127.0.0.1`
- **Port**: `3306`
- **User**: `gary`
- **Password**: `wjdwhdans`
- **Database**: `household_ledger`

### 컨테이너 관리

```bash
# 상태 확인
docker ps | grep household-ledger-db

# 로그 확인
docker logs household-ledger-db

# 중지
docker stop household-ledger-db

# 삭제
docker rm household-ledger-db
```

---

## 🚀 Server 설정 (docker/server/)

### 프로덕션 빌드

```bash
cd docker/server
docker build -t household-ledger-api:latest -f Dockerfile ../../

# 컨테이너 실행
docker run -d \
  --name household-ledger-api \
  -p 8000:8000 \
  -e DATABASE_URL=mysql+pymysql://gary:wjdwhdans@host.docker.internal:3306/household_ledger \
  household-ledger-api:latest
```

### 개발 모드

```bash
# 로컬에서 실행
cd /Users/gary/Documents/workspace/household-ledger-server
source .venv/bin/activate
uvicorn app.main:app --reload
```

---

## 📊 컨테이너 상태 확인

```bash
# 실행 중인 컨테이너 확인
docker ps

# 모든 컨테이너 확인 (중지된 것 포함)
docker ps -a
```

---

## 🗂️ 데이터 백업 및 복원

### 백업

```bash
docker exec household-ledger-db mysqldump \
  -u gary -pwjdwhdans household_ledger > backup.sql
```

### 복원

```bash
docker exec -i household-ledger-db mysql \
  -u gary -pwjdwhdans household_ledger < backup.sql
```

---

## 🔧 환경 변수

### Database

| 변수 | 기본값 | 설명 |
|------|--------|------|
| MYSQL_ROOT_PASSWORD | wjdwhdans | Root 비밀번호 |
| MYSQL_DATABASE | household_ledger | 데이터베이스 이름 |
| MYSQL_USER | gary | 애플리케이션 사용자 |
| MYSQL_PASSWORD | wjdwhdans | 애플리케이션 비밀번호 |

### Server

| 변수 | 기본값 | 설명 |
|------|--------|------|
| DATABASE_URL | mysql+pymysql://gary:wjdwhdans@localhost:3306/household_ledger | DB 연결 URL |
| JWT_SECRET | your-secret-key | JWT 시크릿 |
| JWT_REFRESH_SECRET | your-refresh-secret | JWT 갱신 시크릿 |

---

## ⚠️ 참고사항

- 데이터 영속성을 원한다면 볼륨 마운트를 추가하세요:
```bash
docker run -d \
  --name household-ledger-db \
  -p 3306:3306 \
  -v household-ledger-data:/var/lib/mysql \
  household-ledger-mysql:latest
```
