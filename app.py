import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정 및 레이아웃
st.set_page_config(page_title="하천구역 스마트 조회", layout="wide", initial_sidebar_state="collapsed")

# 2. 가독성을 고려한 적정 폰트 사이즈 CSS (축소 비율 조정)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    /* 전체 폰트 사이즈 (1.0rem 수준으로 조정) */
    html, body, [class*="css"] { font-size: 0.95rem; }

    /* 헤더 및 제목 디자인 */
    .mobile-header {
        font-size: 1.15rem !important;
        font-weight: 800;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 12px;
    }

    /* 카드 디자인 최적화 */
    .property-card {
        background-color: white;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.06);
        margin-bottom: 15px;
        border: 1px solid #e2e8f0;
    }

    /* 지번 제목 크기 */
    .address-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #1a202c;
        margin-bottom: 8px;
        display: block;
    }
    
    /* 주소 박스 디자인 */
    .full-address-value {
        font-size: 0.9rem;
        font-weight: 600;
        color: #334155;
        background-color: #f1f5f9;
        padding: 8px;
        border-radius: 6px;
        display: block;
        margin-bottom: 12px;
    }

    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 12px;
    }

    .label { font-size: 0.75rem; color: #64748b; display: block; }
    .value { font-size: 1.0rem; font-weight: 700; color: #1e293b; }
    .highlight-value { font-size: 1.0rem; font-weight: 700; color: #ef4444; }

    /* 네이버 스타일 버튼 */
    .map-action-btn {
        display: block;
        text-align: center;
        background-color: #03c75a;
        color: white !important;
        padding: 12px;
        border-radius: 10px;
        text-decoration: none !important;
        font-weight: 800;
        font-size: 0.95rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="mobile-header">🌊 하천구역 스마트 조회</p>', unsafe_allow_html=True)

# 3. 데이터 로드 설정 (항목 10개로 고정하여 에러 방지)
region_files = {
    "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "고령군": "03_goryeong.xlsm",
    "달성군": "04_dalseong.xlsm", "달서구": "05_dalseo.xlsm", "문경시": "06_mungyeong.xlsm",
    "안동시": "07_andong.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm",
    "상주시": "10_sangju.xlsm", "성주군": "11_seongju.xlsm"
}

# 10개 항목 정의
all_columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']

with st.popover("🔍 지역 및 지번 검색"):
    selected_region = st.selectbox("🎯 대상 지역", options=list(region_files.keys()))
    file_path = region_files[selected_region]
    
    if os.path.exists(file_path):
        # 엑셀 데이터 로드 (2행부터 데이터)
        df = pd.read_excel(file_path, sheet_name=0, header=1)
        
        # 엑셀 열 개수와 리스트 개수를 맞춰서 에러 해결
        df.columns = all_columns 
        
        dong_list = sorted(df['동리'].dropna().unique())
        target_dong = st.selectbox("📍 동/리", options=["전체 지역"] + list(dong_list))
        search_jibun = st.text_input("🏠 지번 입력 (예: 1080-2)")
    else:
        st.error(f"'{selected_region}' 파일을 찾을 수 없습니다.")
        st.stop()

# 4. 필터링 로직
filtered_df = df.copy()
if target_dong != "전체 지역":
    filtered_df = filtered_df[filtered_df['동리'] == target_dong]
if search_jibun:
    filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

# 5. 결과 출력
st.markdown(f"**총 {len(filtered_df):,}건 조회됨**")

for _, row in filtered_df.head(30).iterrows():
    # 전체 주소 조합
    full_addr = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
    
    st.markdown(f"""
        <div class="property-card">
            <span class="address-title">📍 {row['동리']} {row['번지']}</span>
            <span class="full-address-value">{full_addr}</span>

            <div class="info-grid">
                <div>
                    <span class="label">지적 면적</span>
                    <span class="value">{row['지적_m2']:,} ㎡</span>
                </div>
                <div>
                    <span class="label" style="color:#ef4444;">편입 면적</span>
                    <span class="highlight-value">{row['편입면적_m2']:,} ㎡</span>
                </div>
            </div>
            
            <div style="margin-bottom:12px; display: flex; justify-content: space-between;">
                <div><span class="label">지목</span><span class="value">{row['지목']}</span></div>
                <div style="text-align:right;"><span class="label">소유자</span><span class="value">{row['소유자_성명']}</span></div>
            </div>

            <a href="https://map.naver.com/v5/search/{full_addr}" target="_blank" class="map-action-btn">지도 위치 확인</a>
        </div>
    """, unsafe_allow_html=True)