#!/usr/bin/env python3
"""
리포트 크롤링 시스템 실행 스크립트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # scripts 폴더의 실행 스크립트 호출
    from scripts.run_dashboard import main
    main()
