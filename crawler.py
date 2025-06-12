import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import os
from pdf2image import convert_from_path
import re

def download_pdf(url, filename):
    """PDF 파일을 다운로드하는 함수"""
    try:
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"PDF 다운로드 실패: {e}")
        return False

def convert_first_page_to_image(pdf_path, image_path):
    """PDF의 첫 페이지를 이미지로 변환하는 함수"""
    try:
        # PDF를 이미지로 변환
        images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path='/opt/homebrew/bin')
        if images:
            # 첫 페이지 이미지 저장
            images[0].save(image_path, 'JPEG')
            return True
    except Exception as e:
        print(f"이미지 변환 실패: {e}")
    return False

def get_research_reports(page=1):
    url = f"https://finance.naver.com/research/company_list.naver?&page={page}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    response.encoding = 'euc-kr'  # 한글 인코딩 처리
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    # 테이블 찾기 (여러 클래스 시도)
    table = soup.find('table', {'class': 'type_1'})
    if not table:
        table = soup.find('table', {'class': 'type_5'})
    if not table:
        table = soup.find('table', {'class': 'type_6'})
    
    if not table:
        return []
    
    reports = []
    rows = table.find_all('tr')[1:]  # 헤더 제외
    today = datetime.now().strftime('%y.%m.%d')  # 오늘 날짜 형식 (예: 24.03.21)
    
    # 폴더 생성
    os.makedirs('report_pdf', exist_ok=True)
    os.makedirs('first_page', exist_ok=True)
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 6:
            date = cols[4].text.strip()
            
            # 오늘 날짜의 리포트만 수집
            if date == today:
                stock_name = cols[0].text.strip()
                title = cols[1].text.strip()
                company = cols[2].text.strip()
                
                # 첨부 파일 링크 추출
                attachment_link = ""
                attachment_cell = cols[3]
                if attachment_cell.find('a'):
                    href = attachment_cell.find('a')['href']
                    if href.startswith('//'):
                        attachment_link = "https:" + href
                    else:
                        attachment_link = href
                    
                    # 파일명 생성 (종목명_제목.pdf)
                    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)  # 파일명에 사용할 수 없는 문자 제거
                    pdf_filename = f"report_pdf/{stock_name}_{safe_title}.pdf"
                    image_filename = f"first_page/{stock_name}_{safe_title}.jpg"
                    
                    # PDF 다운로드 및 첫 페이지 이미지 변환
                    if download_pdf(attachment_link, pdf_filename):
                        print(f"PDF 다운로드 완료: {pdf_filename}")
                        if convert_first_page_to_image(pdf_filename, image_filename):
                            print(f"이미지 변환 완료: {image_filename}")
                
                views = cols[5].text.strip()
                
                reports.append({
                    '종목명': stock_name,
                    '제목': title,
                    '증권사': company,
                    '첨부': attachment_link,
                    '작성일': date,
                    '조회수': views
                })
            elif date < today:  # 오늘보다 이전 날짜가 나오면 더 이상 검색할 필요 없음
                return reports
    
    return reports

def main():
    all_reports = []
    page = 1
    
    print(f"크롤링 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    while True:
        reports = get_research_reports(page)
        
        if not reports:
            break
            
        all_reports.extend(reports)
        page += 1
        time.sleep(1)  # 서버 부하 방지를 위한 딜레이
    
    # DataFrame 생성 및 저장
    df = pd.DataFrame(all_reports)
    filename = f"research_reports_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n크롤링 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"총 {len(all_reports)}개의 오늘자 리포트를 {filename}에 저장했습니다.")

if __name__ == "__main__":
    main() 