# 📊 리포트 크롤링 시스템

네이버 금융 종목분석 리포트를 자동으로 수집하고 시각화하는 시스템입니다.

## 🚀 주요 기능

- **자동 크롤링**: 네이버 금융 리포트 페이지에서 데이터 자동 수집
- **실시간 대시보드**: Streamlit 기반 웹 대시보드로 데이터 시각화
- **스케줄링**: 정해진 시간에 자동으로 크롤링 실행
- **PDF 다운로드**: 첨부된 PDF 파일 자동 다운로드
- **데이터 분석**: 증권사별, 조회수별 통계 및 차트 제공

## 📋 시스템 구성

```
report_crawling/
├── src/                    # 소스 코드
│   ├── __init__.py
│   ├── crawler.py         # 크롤링 로직
│   ├── dashboard.py       # 대시보드
│   └── scheduler.py       # 스케줄러
├── scripts/               # 실행 스크립트
│   ├── __init__.py
│   └── run_dashboard.py   # 통합 실행 스크립트
├── data/                  # 데이터 저장소
│   ├── csv/              # CSV 파일들
│   ├── images/           # 이미지 파일들
│   └── pdfs/             # PDF 파일들
├── logs/                  # 로그 파일들
├── config/               # 설정 파일들
├── docs/                 # 문서
├── run.py                # 메인 실행 스크립트
├── requirements.txt      # Python 패키지 목록
└── report_crawling_venv/ # Python 가상환경
```

## 🛠️ 설치 및 설정

### 1. 저장소 클론
```bash
git clone https://github.com/Ji-Sung-Lee/report_crawling.git
cd report_crawling
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv report_crawling_venv
source report_crawling_venv/bin/activate  # macOS/Linux
# 또는
report_crawling_venv\Scripts\activate     # Windows
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

## 🚀 실행 방법

### 방법 1: 통합 실행 스크립트 사용 (권장)
```bash
python run.py
```
- 대시보드만 실행
- 스케줄러만 실행  
- 대시보드 + 스케줄러 함께 실행

### 방법 2: 개별 실행

#### 대시보드 실행
```bash
streamlit run src/dashboard.py
```
- 브라우저에서 `http://localhost:8501` 접속

#### 스케줄러 실행
```bash
python src/scheduler.py
```
- 매일 09:00, 15:00, 21:00에 자동 크롤링

#### 크롤러 수동 실행
```bash
python src/crawler.py
```

## 📊 대시보드 기능

### 주요 화면
- **📈 실시간 통계**: 총 리포트 수, 증권사 수, 평균 조회수, PDF 첨부 수
- **📊 차트 분석**: 증권사별 리포트 수, 조회수 분포
- **📋 데이터 테이블**: 수집된 리포트 목록 (검색, 정렬 기능)
- **📄 PDF 다운로드**: 첨부된 PDF 파일 직접 다운로드
- **🤖 스케줄러 상태**: 크롤링 작업 실행 상태 모니터링

### 필터 기능
- **증권사별 필터링**: 특정 증권사의 리포트만 조회
- **날짜 범위 선택**: 특정 기간의 리포트 조회
- **검색 기능**: 종목명 또는 제목으로 검색
- **정렬 기능**: 작성일, 조회수, 종목명, 증권사별 정렬

## ⏰ 스케줄링 설정

### 기본 스케줄
- **09:00**: 장 시작 전 리포트 수집
- **15:00**: 장 마감 후 리포트 수집  
- **21:00**: 야간 리포트 수집

### 스케줄 변경
`src/scheduler.py` 파일에서 `schedule_jobs()` 함수를 수정하여 스케줄을 변경할 수 있습니다.

```python
def schedule_jobs(self):
    # 매일 오전 9시, 오후 3시, 오후 9시에 실행
    schedule.every().day.at("09:00").do(self.run_crawler)
    schedule.every().day.at("15:00").do(self.run_crawler)
    schedule.every().day.at("21:00").do(self.run_crawler)
    
    # 테스트용: 1분마다 실행
    # schedule.every(1).minutes.do(self.run_crawler)
```

## 📁 데이터 구조

### CSV 파일 형식
```csv
종목명,제목,증권사,첨부,작성일,조회수
삼양식품,"수요는 넘치고, 생산은 확대중",대신증권,https://...,25.08.19,844
```

### 저장 위치
- **CSV 파일**: `data/csv/` 폴더
- **이미지 파일**: `data/images/` 폴더
- **PDF 파일**: `data/pdfs/` 폴더

## 🔧 설정 파일

### .gitignore
- `data/`: 데이터 파일들 제외
- `logs/`: 로그 파일들 제외
- `report_crawling_venv/`: 가상환경 제외

### scheduler_status.json
스케줄러 실행 상태 정보가 자동으로 저장됩니다.

## 📈 모니터링

### 로그 파일
- `logs/crawler.log`: 크롤링 작업 로그
- `logs/scheduler_status.json`: 스케줄러 상태 정보
- 대시보드에서 실시간 상태 확인 가능

### 성능 지표
- 총 실행 횟수
- 성공/실패 횟수
- 마지막 실행 시간
- 다음 실행 시간

## 🚀 24시간 운영

### Docker 배포 (추천)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["python", "run.py"]
```

### 클라우드 배포
- **Streamlit Cloud**: 무료 호스팅
- **Heroku**: 쉬운 배포
- **AWS/GCP**: 고성능 운영

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

- GitHub: [Ji-Sung-Lee](https://github.com/Ji-Sung-Lee)
- 이메일: jsleeethan@gmail.com

---

**⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요!** 