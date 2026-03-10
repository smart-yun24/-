import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정 및 모바일 최적화 레이아웃
st.set_page_config(page_title="하천구역 스마트 조회", layout="wide", initial_sidebar_state="collapsed")

# 2. 고퀄리티 모바일 CSS 디자인
st.markdown("""
    <style>
    /* 전체 배경색 - 부드러운 그레이 */
    .stApp { background-color: #f1f3f5; }
    
    /* 제목 스타일 - 고급스러운 네이비 */
    .main-title { font-size: 1.4rem !important; font-weight: 800; color: #1a202c; margin-bottom: 20px; text-align: center; }

    /* 검색 팝오버 버튼 디자인 */
    div[data-testid="stPopover"] > button {
        width: 100%; background-color: #3182ce; color: white; border-radius: 12px; height: 50px; font-weight: 700; border: none;
    }

    /* 카드 스타일 컨테이너 */
    .info-card {
        background-color: white; padding: 18px; border-radius: 16px; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        margin-bottom: 15px; border: 1px solid #edf2f7;
    }
    
    /* 카드 제목(지번) 및 뱃지 스타일 */
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .jibun-text { font-size: 1.2rem; font-weight: 700; color: #2d3748; }
    .jimok-badge { 
        background-color: #ebf8ff; color: #2b6cb0; padding: 4px 10px; border-radius: 20px; 
        font-size: 0.8rem; font-weight: 600; 
    }
    
    /* 데이터 텍스트 스타일 */
    .data-label { color: #718096; font-size: 0.85rem; }
    .data-value { color: #1a202c; font-size: 1rem; font-weight: 600; }
    
    /* 지도 가기 버튼 */
    .map-btn {
        display: inline-block; width: 100%; text-align: center; background-color: #03C75A;
        color: white; padding: 10px; border-radius: 10px; text-decoration: none; 
        font-weight: 700; font-size: 0.9rem; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 메인 타이틀
st.markdown('<p class="main-title">🌊 하천구역 스마트 조회기</p>', unsafe_allow_html=True)

# 3. 데이터 로딩 (10개 항목 기준)
region_files = {
    "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "고령군": "03_goryeong.xlsm",
    "달성군": "04_dalseong.xlsm", "달서구": "05_dalseo.xlsm", "문경시": "06_mungyeong.xlsm",
    "안동시": "07_andong.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm",
    "상주시": "10_sangju.xlsm", "성주군": "11_seongju.xlsm"
}

# 4. 사이드바 대신 상단 팝오버 검색창 활용 (모바일용)
with st.popover("🔍 필지 검색 및 설정"):
    selected_region = st.selectbox("🎯 지자체 선택", options=list(region_files.keys()))
    file_path = region_files[selected_region]
    
    if os.path.exists(file_path):
        df = pd.read_excel(file_path, sheet_name=0, header=1)
        df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
        
        dong_list = sorted(df['동리'].dropna().unique())
        target_dong = st.selectbox("📍 동/리 선택", options=["전체 지역"] + list(dong_list))
        search_jibun = st.text_input("🏠 지번 입력 (예: 1080-2)")
    else:
        st.error(f"파일이 없습니다: {file_path}")
        st.stop()

# 5. 데이터 필터링
filtered_df = df.copy()
if target_dong != "전체 지역":
    filtered_df = filtered_df[filtered_df['동리'] == target_dong]
if search_jibun:
    filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

# 6. 모바일 카드형 인터페이스 출력 (Woah 포인트!)
st.markdown(f"**총 {len(filtered_df):,}개의 필지가 조회되었습니다.**")

for idx, row in filtered_df.head(20).iterrows(): # 성능을 위해 상위 20개만 먼저 표시
    # 카드 시작
    with st.container():
        # HTML을 이용한 카드 디자인
        st.markdown(f"""
            <div class="info-card">
                <div class="card-header">
                    <span class="jibun-text">📍 {row['동리']} {row['번지']}</span>
                    <span class="jimok-badge">{row['지목']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div><span class="data-label">지적면적</span><br/><span class="data-value">{row['지적_m2']:,} ㎡</span></div>
                    <div style="text-align: right;"><span class="data-label" style="color:#e53e3e;">편입면적</span><br/><span class="data-value" style="color:#e53e3e;">{row['편입면적_m2']:,} ㎡</span></div>
                </div>
                <div style="border-top: 1px solid #f7fafc; padding-top: 8px; margin-top: 8px;">
                    <span class="data-label">소유자</span> <span class="data-value">{row['소유자_성명']}</span>
                </div>
                <a href="https://map.naver.com/v5/search/{row['시군']} {row['읍면']} {row['동리']} {row['번지']}" 
                   target="_blank" class="map-btn">네이버 지도에서 위치 확인</a>
            </div>
        """, unsafe_allow_html=True)

# 7. 푸터 디자인
st.markdown("---")
st.caption("📱 본 시스템은 모바일 환경에 최적화되어 있습니다.")