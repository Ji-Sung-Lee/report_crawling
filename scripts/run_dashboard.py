#!/usr/bin/env python3
"""
리포트 크롤링 대시보드 실행 스크립트
대시보드와 스케줄러를 함께 실행합니다.
"""

import subprocess
import sys
import os
import time
import signal
import threading
from datetime import datetime

def run_streamlit():
    """Streamlit 대시보드 실행"""
    try:
        print("🚀 Streamlit 대시보드를 시작합니다...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "src/dashboard.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Streamlit 대시보드가 중지되었습니다.")
    except Exception as e:
        print(f"❌ Streamlit 실행 중 오류: {e}")

def run_scheduler():
    """스케줄러 실행"""
    try:
        print("🤖 크롤링 스케줄러를 시작합니다...")
        subprocess.run([sys.executable, "src/scheduler.py"])
    except KeyboardInterrupt:
        print("\n🛑 스케줄러가 중지되었습니다.")
    except Exception as e:
        print(f"❌ 스케줄러 실행 중 오류: {e}")

def main():
    """메인 함수"""
    print("=" * 50)
    print("📊 리포트 크롤링 대시보드 시스템")
    print("=" * 50)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 가상환경 확인
    if not os.path.exists("report_crawling_venv"):
        print("❌ 가상환경을 찾을 수 없습니다.")
        print("다음 명령어로 가상환경을 생성하세요:")
        print("python -m venv report_crawling_venv")
        return
    
    # 필요한 파일 확인
    required_files = ["src/dashboard.py", "src/scheduler.py", "src/crawler.py"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ 필요한 파일이 없습니다: {', '.join(missing_files)}")
        return
    
    print("✅ 모든 필요한 파일이 확인되었습니다.")
    print()
    
    # 실행 모드 선택
    print("실행 모드를 선택하세요:")
    print("1. 대시보드만 실행")
    print("2. 스케줄러만 실행")
    print("3. 대시보드 + 스케줄러 (권장)")
    
    try:
        choice = input("선택 (1-3): ").strip()
    except KeyboardInterrupt:
        print("\n🛑 사용자가 중단했습니다.")
        return
    
    if choice == "1":
        print("📊 대시보드만 실행합니다...")
        run_streamlit()
    elif choice == "2":
        print("🤖 스케줄러만 실행합니다...")
        run_scheduler()
    elif choice == "3":
        print("🚀 대시보드와 스케줄러를 함께 실행합니다...")
        print("대시보드: http://localhost:8501")
        print("스케줄러: 백그라운드에서 실행")
        print()
        
        # 스케줄러를 백그라운드 스레드로 실행
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # 대시보드 실행
        run_streamlit()
    else:
        print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main()
