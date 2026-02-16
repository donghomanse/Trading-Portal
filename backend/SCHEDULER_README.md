# KOSPI 마스터 데이터 스케줄러

## 개요
이 애플리케이션은 매일 밤 10시(22:00)에 자동으로 KOSPI 주식 마스터 데이터를 업데이트합니다.

## 기능

### 자동 업데이트 (스케줄링)
- **실행 시간**: 매일 22:00 (밤 10시)
- **작업 내용**:
  1. 대신증권에서 KOSPI 마스터 파일 다운로드
  2. 데이터 파싱 및 처리
  3. 데이터베이스에 저장 (stocks 테이블)
  4. Excel 파일 백업 (kospi_code.xlsx)
  5. JSON 파일 백업 (kospi_code.json)

### API 엔드포인트

#### 1. 스케줄러 상태 확인
```bash
GET /api/scheduler/status
```

응답 예시:
```json
{
  "status": "running",
  "next_run_time": "2024-01-20T22:00:00+09:00",
  "job_name": "Daily KOSPI Master Update"
}
```

#### 2. 수동 업데이트 실행
```bash
POST /api/scheduler/update-kospi
```

응답 예시:
```json
{
  "status": "success",
  "message": "KOSPI master data updated successfully"
}
```

#### 3. 종목 조회
```bash
GET /api/stocks?skip=0&limit=100
```

#### 4. 특정 종목 조회
```bash
GET /api/stocks/{code}
```

예시: `GET /api/stocks/005930` (삼성전자)

## 사용 방법

### 1. 서버 시작
```bash
cd backend
python main.py
```

서버 시작 시 자동으로 스케줄러가 활성화되며, 다음과 같은 메시지가 출력됩니다:
```
[SCHEDULER] Started - KOSPI master data will be updated daily at 22:00
[SCHEDULER] Next run time: 2024-01-20 22:00:00+09:00
[APP] Application started - KOSPI data will be updated daily at 22:00
```

### 2. 수동 업데이트 실행
웹 브라우저나 curl을 사용하여 수동으로 업데이트를 실행할 수 있습니다:

```bash
curl -X POST http://localhost:8000/api/scheduler/update-kospi
```

### 3. 스케줄러 상태 확인
```bash
curl http://localhost:8000/api/scheduler/status
```

## 파일 구조

```
backend/
├── scheduler.py              # 스케줄러 설정 및 업데이트 로직
├── download_kospi_master.py  # KOSPI 마스터 다운로드 함수
├── main.py                   # FastAPI 앱 (스케줄러 통합)
├── models.py                 # Stock 모델 정의
└── database.py               # DB 설정
```

## 주의사항

1. **시간대**: 서버의 로컬 시간대를 기준으로 22:00에 실행됩니다.
2. **네트워크**: 대신증권 서버에 접근할 수 있어야 합니다.
3. **디스크 공간**: Excel, JSON 백업 파일이 저장되므로 충분한 디스크 공간이 필요합니다.
4. **데이터베이스**: 매번 업데이트 시 기존 stocks 테이블 데이터가 삭제되고 새로 저장됩니다.

## 로그 확인

스케줄러 실행 시 다음과 같은 로그가 출력됩니다:

```
[SCHEDULER] Starting KOSPI master update at 2024-01-20 22:00:00
[SCHEDULER] Downloading KOSPI master file...
[SCHEDULER] Processing KOSPI master data...
[SCHEDULER] Saving to database...
[DB] Clearing existing stock data...
[DB] Inserting stock data...
[DB] Inserted 100 stocks...
[DB] Inserted 200 stocks...
...
[DB] Total 2493 stocks inserted successfully!
[SCHEDULER] Saving to Excel...
[SCHEDULER] Saving to JSON...
[SCHEDULER] KOSPI master update completed successfully!
[SCHEDULER] Total stocks: 2493
[SCHEDULER] Next update: Tomorrow at 22:00
```

## 문제 해결

### 스케줄러가 시작되지 않는 경우
1. APScheduler 패키지 설치 확인: `pip install apscheduler==3.10.4`
2. 로그에서 에러 메시지 확인

### 업데이트 실패 시
1. 네트워크 연결 확인
2. 대신증권 서버 접근 가능 여부 확인
3. 디스크 공간 확인
4. 데이터베이스 연결 확인

### 수동 실행으로 테스트
```bash
cd backend
python download_kospi_master.py
```
