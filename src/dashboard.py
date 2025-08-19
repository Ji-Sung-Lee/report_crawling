import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import glob
import json

# 페이지 설정
st.set_page_config(
    page_title="리포트 크롤링 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 제목과 설명
st.title("📊 리포트 크롤링 대시보드")
st.markdown("네이버 금융 종목분석 리포트 수집 현황을 실시간으로 모니터링합니다.")

# 사이드바
st.sidebar.header("🔧 설정")
st.sidebar.markdown("### 필터 옵션")

# 스케줄러 상태 로드 함수
@st.cache_data(ttl=60)  # 1분마다 캐시 갱신
def load_scheduler_status():
    """스케줄러 상태를 로드합니다."""
    try:
        if os.path.exists('logs/scheduler_status.json'):
            with open('logs/scheduler_status.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        st.error(f"스케줄러 상태 로드 실패: {e}")
        return None

# 데이터 로드 함수
@st.cache_data
def load_data():
    """CSV 파일에서 데이터를 로드합니다."""
    try:
        # CSV 파일 찾기
        csv_files = glob.glob("data/csv/*.csv")
        if not csv_files:
            st.error("CSV 파일을 찾을 수 없습니다.")
            return None
        
        # 가장 최근 파일 선택
        latest_file = max(csv_files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        
        # 날짜 컬럼 처리
        if '작성일' in df.columns:
            df['작성일'] = pd.to_datetime(df['작성일'], format='%y.%m.%d', errors='coerce')
        
        return df, latest_file
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return None, None

# 데이터 로드
df, filename = load_data()

if df is not None:
    st.sidebar.success(f"📁 로드된 파일: {filename}")
    
    # 필터 옵션 (스케줄러 상태 위로 이동)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📅 날짜 필터")
    if '작성일' in df.columns:
        date_range = st.sidebar.date_input(
            "날짜 범위 선택",
            value=(df['작성일'].min().date(), df['작성일'].max().date()),
            min_value=df['작성일'].min().date(),
            max_value=df['작성일'].max().date()
        )
    
    st.sidebar.markdown("### 🏢 증권사 필터")
    all_companies = ["전체"] + sorted(df['증권사'].unique().tolist())
    selected_company = st.sidebar.selectbox("증권사 선택", all_companies)
    
    # 스케줄러 상태 로드
    scheduler_status = load_scheduler_status()
    
    # 스케줄러 상태 표시 (필터 아래로 이동)
    if scheduler_status:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🤖 스케줄러 상태")
        
        # 다음 실행 시간 (맨 위로 이동)
        if scheduler_status.get("next_run"):
            next_run = datetime.fromisoformat(scheduler_status["next_run"])
            st.sidebar.info(f"다음 실행: {next_run.strftime('%Y-%m-%d %H:%M')}")
        
        # 실행 상태
        if scheduler_status.get("is_running"):
            st.sidebar.success("🟢 실행 중")
        else:
            st.sidebar.info("⚪ 대기 중")
        
        # 통계 정보
        st.sidebar.metric("총 실행 횟수", scheduler_status.get("total_runs", 0))
        st.sidebar.metric("성공 횟수", scheduler_status.get("success_count", 0))
        st.sidebar.metric("실패 횟수", scheduler_status.get("error_count", 0))
        
        # 마지막 실행 시간
        if scheduler_status.get("last_run"):
            last_run = datetime.fromisoformat(scheduler_status["last_run"])
            st.sidebar.info(f"마지막 실행: {last_run.strftime('%Y-%m-%d %H:%M')}")
    
    # 기본 통계
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📈 총 리포트 수",
            value=len(df),
            delta=f"+{len(df)} 건"
        )
    
    with col2:
        unique_companies = df['증권사'].nunique()
        st.metric(
            label="🏢 증권사 수",
            value=unique_companies,
            delta=f"+{unique_companies} 개사"
        )
    
    with col3:
        avg_views = int(df['조회수'].mean())
        st.metric(
            label="👀 평균 조회수",
            value=f"{avg_views:,}",
            delta=f"+{avg_views:,} 회"
        )
    
    with col4:
        pdf_count = df['첨부'].notna().sum()
        st.metric(
            label="📄 PDF 첨부",
            value=pdf_count,
            delta=f"+{pdf_count} 건"
        )
    
    # 데이터 필터링
    filtered_df = df.copy()
    if selected_company != "전체":
        filtered_df = filtered_df[filtered_df['증권사'] == selected_company]
    
    # 2. 수집된 리포트 목록 & PDF 다운로드
    st.markdown("---")
    st.subheader("📋 수집된 리포트 목록")
    
    # 검색 기능
    search_term = st.text_input("🔍 종목명 또는 제목으로 검색")
    if search_term:
        filtered_df = filtered_df[
            filtered_df['종목명'].str.contains(search_term, case=False, na=False) |
            filtered_df['제목'].str.contains(search_term, case=False, na=False)
        ]
    
    # 정렬 옵션
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox("정렬 기준", ["작성일", "조회수", "종목명", "증권사"])
    with col2:
        sort_order = st.selectbox("정렬 순서", ["내림차순", "오름차순"])
    
    if sort_order == "내림차순":
        filtered_df = filtered_df.sort_values(sort_by, ascending=False)
    else:
        filtered_df = filtered_df.sort_values(sort_by, ascending=True)
    
    # 미리보기 이미지 경로 생성 함수
    def get_preview_image_path(row):
        """리포트의 미리보기 이미지 경로를 생성합니다."""
        if pd.notna(row['첨부']) and row['첨부'] != "":
            # 종목명으로 이미지 파일 찾기
            import glob
            
            # first_page 폴더에서 해당 종목의 이미지 파일 찾기
            pattern = f"data/images/first_page/{row['종목명']}_*.jpg"
            matching_files = glob.glob(pattern)
            
            if matching_files:
                # 첫 번째 매칭 파일 반환
                return matching_files[0]
                    
        return None
    
    # PDF 다운로드 링크와 미리보기를 포함한 데이터프레임 생성
    display_df = filtered_df.copy()
    
    # 미리보기 컬럼 추가
    display_df['미리보기'] = display_df.apply(get_preview_image_path, axis=1)
    
    # 다운로드 컬럼에 실제 URL 포함
    display_df['다운로드'] = display_df['첨부'].apply(
        lambda x: x if pd.notna(x) and x != "" else "첨부 없음"
    )
    
    # 작성일 형식을 깔끔하게 표시
    display_df['작성일'] = display_df['작성일'].dt.strftime('%Y-%m-%d')
    
    # 다운로드 버튼을 포함한 데이터프레임 생성
    display_df_with_buttons = filtered_df.copy()
    
    # 다운로드 버튼 컬럼 추가
    def create_download_button(url):
        if pd.notna(url) and url != "":
            return "📄 다운로드"
        return "첨부 없음"
    
    display_df_with_buttons['다운로드'] = display_df_with_buttons['첨부'].apply(create_download_button)
    
    # 데이터 에디터로 표시 (편집 가능한 테이블)
    edited_df = st.data_editor(
        display_df_with_buttons[['종목명', '제목', '증권사', '작성일', '조회수', '다운로드']],
        use_container_width=True,
        height=400,
        column_config={
            "작성일": st.column_config.TextColumn(
                "작성일",
                help="리포트 작성일",
                max_chars=10,
                disabled=True
            ),
            "다운로드": st.column_config.TextColumn(
                "다운로드",
                help="PDF 파일 다운로드",
                max_chars=20,
                disabled=True
            )
        },
        disabled=["종목명", "제목", "증권사", "작성일", "조회수", "다운로드"]
    )
    
    # 다운로드 버튼들을 테이블 형태로 표시
    st.markdown("### 📥 PDF 다운로드")
    
    # CSS로 최소 간격 구분선 스타일 추가
    st.markdown("""
    <style>
    .compact-divider {
        height: 1px;
        background-color: #e0e0e0;
        margin: 2px 0;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 각 행을 개별적으로 표시 (최소 간격) - filtered_df 사용
    for idx, row in filtered_df.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 1, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{row['종목명']}**", help=str(row['종목명']))
        
        with col2:
            st.markdown(f"*{row['제목']}*", help=str(row['제목']))
        
        with col3:
            st.markdown(f"**{row['증권사']}**", help=str(row['증권사']))
        
        with col4:
            st.markdown(f"**{row['작성일']}**", help=str(row['작성일']))
        
        with col5:
            st.markdown(f"**{row['조회수']}**", help=str(row['조회수']))
        
        with col6:
            if pd.notna(row['첨부']) and row['첨부'] != "":
                st.link_button("📄 다운로드", row['첨부'], use_container_width=True)
            else:
                st.markdown("첨부 없음", help="첨부 파일이 없습니다")
        
        # 최소 간격 구분선 추가
        st.markdown('<hr class="compact-divider">', unsafe_allow_html=True)
    
    # 미리보기 섹션
    st.markdown("---")
    st.subheader("🖼️ 리포트 미리보기")
    
    # 미리보기 이미지가 있는 리포트들만 필터링
    preview_df = display_df[display_df['미리보기'].notna()]
    
    if not preview_df.empty:
        # 9개까지 표시 (3x3 그리드)
        preview_count = min(len(preview_df), 9)
        
        for i in range(0, preview_count, 3):
            cols = st.columns(3)
            for j in range(3):
                idx = i + j
                if idx < preview_count:
                    row = preview_df.iloc[idx]
                    with cols[j]:
                        st.write(f"**{row['종목명']}**")
                        st.write(f"*{row['제목'][:25]}...*" if len(row['제목']) > 25 else f"*{row['제목']}*")
                        try:
                            st.image(row['미리보기'], use_container_width=True, caption=f"{row['종목명']} 미리보기")
                        except Exception as e:
                            st.error(f"이미지 로드 실패: {e}")
    else:
        st.info("미리보기할 수 있는 이미지가 없습니다.")
    
    # 3. 증권사별 리포트 수, 조회수 분포
    st.markdown("---")
    st.subheader("📊 데이터 분석")
    
    # 차트 섹션
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 증권사별 리포트 수")
        company_counts = filtered_df['증권사'].value_counts()
        
        # 상위 10개 증권사만 표시
        top_companies = company_counts.head(10)
        
        fig_company = px.bar(
            x=top_companies.values,
            y=top_companies.index,
            orientation='h',
            title="",
            labels={'x': '리포트 수', 'y': '증권사'},
            color=top_companies.values,
            color_continuous_scale='Blues'
        )
        
        fig_company.update_layout(
            height=450,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            xaxis=dict(
                title="리포트 수",
                title_font=dict(size=14, color='#666'),
                tickfont=dict(size=11),
                gridcolor='rgba(128,128,128,0.2)'
            ),
            yaxis=dict(
                title="",
                tickfont=dict(size=11),
                gridcolor='rgba(128,128,128,0.2)'
            ),
            showlegend=False
        )
        
        # 바 위에 값 표시
        fig_company.update_traces(
            texttemplate='%{x}',
            textposition='outside',
            textfont=dict(size=10, color='#333')
        )
        
        st.plotly_chart(fig_company, use_container_width=True)
        
        # 추가 통계 정보
        st.markdown(f"**총 증권사 수:** {len(company_counts)}개")
        st.markdown(f"**평균 리포트 수:** {company_counts.mean():.1f}개")
    
    with col2:
        st.markdown("### 📈 조회수 분석")
        
        # 조회수 통계
        views_stats = filtered_df['조회수'].describe()
        
        # 조회수 분포 히스토그램
        fig_views = px.histogram(
            filtered_df,
            x='조회수',
            nbins=12,  # 구간 수 줄여서 막대 간격 확보
            title="",
            labels={'조회수': '조회수', 'count': '리포트 수'},
            color_discrete_sequence=['#2E86AB']
        )
        
        fig_views.update_layout(
            height=450,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            bargap=0.15,  # 막대 간격 설정
            bargroupgap=0.1,  # 그룹 간격 설정
            xaxis=dict(
                title="조회수",
                title_font=dict(size=14, color='#666'),
                tickfont=dict(size=11),
                gridcolor='rgba(128,128,128,0.2)',
                showgrid=True,
                zeroline=False
            ),
            yaxis=dict(
                title="리포트 수",
                title_font=dict(size=14, color='#666'),
                tickfont=dict(size=11),
                gridcolor='rgba(128,128,128,0.2)',
                showgrid=True,
                zeroline=False
            ),
            showlegend=False
        )
        
        # 히스토그램 스타일 개선
        fig_views.update_traces(
            marker=dict(
                line=dict(width=2, color='white'),  # 테두리 두께 증가
                opacity=0.85,  # 투명도 조정
                color='#2E86AB'
            ),
            hovertemplate='조회수 범위: %{x}<br>리포트 수: %{y}<extra></extra>'  # 호버 정보 개선
        )
        
        st.plotly_chart(fig_views, use_container_width=True)
        
        # 조회수 통계 정보
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("평균 조회수", f"{views_stats['mean']:.0f}")
        with col_b:
            st.metric("최대 조회수", f"{views_stats['max']:.0f}")
        with col_c:
            st.metric("중간값", f"{views_stats['50%']:.0f}")
    
    # 4. 실시간 정보
    st.markdown("---")
    st.subheader("🔄 실시간 정보")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**마지막 업데이트:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col2:
        st.info(f"**데이터 파일:** {filename}")
    
    # 자동 새로고침
    if st.button("🔄 새로고침"):
        st.cache_data.clear()
        st.rerun()

else:
    st.error("데이터를 로드할 수 없습니다. CSV 파일이 있는지 확인해주세요.")

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        📊 리포트 크롤링 대시보드 | 
        <a href='https://github.com/Ji-Sung-Lee/report_crawling' target='_blank'>GitHub</a>
    </div>
    """,
    unsafe_allow_html=True
)
