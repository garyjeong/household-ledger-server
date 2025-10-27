# Docker Database Setup

로컬 개발용 MySQL 데이터베이스 Docker 설정

## 📦 사용 방법

### 1. Docker 이미지 빌드

```bash
cd docker
docker build -t household-ledger-mysql:latest -f Dockerfile.mysql .
```

### 2. 컨테이너 실행

```bash
docker run -d \
  --name household-ledger-db \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=wjdwhdans \
  -e MYSQL_DATABASE=household_ledger \
  -e MYSQL_USER=gary \
  -e MYSQL_PASSWORD=wjdwhdans \
  household-ledger-mysql:latest
```

### 3. 컨테이너 상태 확인

```bash
docker ps
```

### 4. 로그 확인

```bash
docker logs household-ledger-db
```

### 5. 데이터베이스 연결

**MySQL 클라이언트로 연결:**
```bash
mysql -h 127.0.0.1 -P 3306 -u gary -pwjdwhdans household_ledger
```

**연결 정보:**
- Host: `127.0.0.1`
- Port: `3306`
- User: `gary`
- Password: `wjdwhdans`
- Database: `household_ledger`

**Root 접속:**
```bash
mysql -h 127.0.0.1 -P 3306 -u root -pwjdwhdans
```

### 6. 컨테이너 중지 및 삭제

```bash
# 중지
docker stop household-ledger-db

# 삭제
docker rm household-ledger-db

# 이미지 삭제
docker rmi household-ledger-mysql:latest
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

| 변수 | 기본값 | 설명 |
|------|--------|------|
| MYSQL_ROOT_PASSWORD | wjdwhdans | Root 비밀번호 |
| MYSQL_DATABASE | household_ledger | 데이터베이스 이름 |
| MYSQL_USER | gary | 애플리케이션 사용자 |
| MYSQL_PASSWORD | wjdwhdans | 애플리케이션 비밀번호 |

---

## 📝 참고사항

- 초기화 스크립트(`init.sql`)는 컨테이너 최초 생성 시에만 실행됩니다.
- 데이터 영속성을 원한다면 볼륨 마운트를 추가하세요:

```bash
docker run -d \
  --name household-ledger-db \
  -p 3306:3306 \
  -v household-ledger-data:/var/lib/mysql \
  household-ledger-mysql:latest
```

- 빠른 시작 스크립트:

```bash
# docker/start-db.sh
#!/bin/bash
docker run -d \
  --name household-ledger-db \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=wjdwhdans \
  -e MYSQL_DATABASE=household_ledger \
  -e MYSQL_USER=gary \
  -e MYSQL_PASSWORD=wjdwhdans \
  household-ledger-mysql:latest

echo "✅ Database started on localhost:3306"
```

