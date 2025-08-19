import schedule
import time
import subprocess
import os
import json
from datetime import datetime, timedelta
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/crawler.log'),
        logging.StreamHandler()
    ]
)

class CrawlerScheduler:
    def __init__(self):
        self.status = {
            "last_run": None,
            "next_run": None,
            "total_runs": 0,
            "success_count": 0,
            "error_count": 0,
            "is_running": False
        }
        self.load_status()
    
    def load_status(self):
        """상태 정보를 파일에서 로드"""
        try:
            if os.path.exists('logs/scheduler_status.json'):
                with open('logs/scheduler_status.json', 'r', encoding='utf-8') as f:
                    self.status.update(json.load(f))
        except Exception as e:
            logging.error(f"상태 로드 실패: {e}")
    
    def save_status(self):
        """상태 정보를 파일에 저장"""
        try:
            os.makedirs('logs', exist_ok=True)
            with open('logs/scheduler_status.json', 'w', encoding='utf-8') as f:
                json.dump(self.status, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logging.error(f"상태 저장 실패: {e}")
    
    def run_crawler(self):
        """크롤러 실행"""
        if self.status["is_running"]:
            logging.warning("크롤러가 이미 실행 중입니다.")
            return
        
        self.status["is_running"] = True
        self.status["last_run"] = datetime.now().isoformat()
        self.status["total_runs"] += 1
        self.save_status()
        
        try:
            logging.info("크롤러 시작...")
            
            # 크롤러 실행
            result = subprocess.run(
                ['python', 'src/crawler.py'],
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )
            
            if result.returncode == 0:
                self.status["success_count"] += 1
                logging.info("크롤러 실행 성공")
            else:
                self.status["error_count"] += 1
                logging.error(f"크롤러 실행 실패: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.status["error_count"] += 1
            logging.error("크롤러 실행 타임아웃")
        except Exception as e:
            self.status["error_count"] += 1
            logging.error(f"크롤러 실행 중 오류: {e}")
        finally:
            self.status["is_running"] = False
            self.save_status()
    
    def schedule_jobs(self):
        """스케줄 작업 설정"""
        # 매일 오전 9시, 오후 3시, 오후 9시에 실행
        schedule.every().day.at("09:00").do(self.run_crawler)
        schedule.every().day.at("15:00").do(self.run_crawler)
        schedule.every().day.at("21:00").do(self.run_crawler)
        
        # 테스트용: 1분마다 실행
        # schedule.every(1).minutes.do(self.run_crawler)
        
        logging.info("스케줄 작업이 설정되었습니다.")
        logging.info("실행 시간: 매일 09:00, 15:00, 21:00")
    
    def get_next_run_time(self):
        """다음 실행 시간 계산"""
        now = datetime.now()
        times = ["09:00", "15:00", "21:00"]
        
        for time_str in times:
            run_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            if run_time > now:
                return run_time
        
        # 다음날 09:00
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
    
    def update_next_run(self):
        """다음 실행 시간 업데이트"""
        self.status["next_run"] = self.get_next_run_time().isoformat()
        self.save_status()
    
    def run(self):
        """스케줄러 실행"""
        self.schedule_jobs()
        self.update_next_run()
        
        logging.info("스케줄러가 시작되었습니다.")
        logging.info(f"다음 실행 시간: {self.status['next_run']}")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
                
                # 다음 실행 시간 업데이트
                if datetime.now().minute == 0:  # 매시 정각에 업데이트
                    self.update_next_run()
                    
        except KeyboardInterrupt:
            logging.info("스케줄러가 중지되었습니다.")
        except Exception as e:
            logging.error(f"스케줄러 실행 중 오류: {e}")

def main():
    """메인 함수"""
    scheduler = CrawlerScheduler()
    scheduler.run()

if __name__ == "__main__":
    main()
