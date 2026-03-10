import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정 및 레이아웃
st.set_page_config(page_title="하천구역 스마트 조회", layout="wide", initial_sidebar_state="collapsed")

# 2. 글자 크기 20% 축소를 적용한 커스텀 CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    /* 전체 기본 폰트 사이즈 조정 (기존 대비 약 20% 축소) */
    html, body, [class*="css"] {
        font-size: 0.9rem;
    }

    /* 상단 헤더 크기 축소 (1.3rem -> 1.05rem) */
    .mobile-header {
        font-size: 1.05rem !important;
        font-weight: 800;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 12px;
    }

    /* 카드 디자인 및 여백 조정 */
    .property-card {
        background-color: white;
        padding: 16px;
        border-radius: 14px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.06);
        margin-bottom: 15px;
        border: 1px solid #e2e8f0;
    }

    /* 지번 제목 크기 축소 (1.25rem -> 1.0rem) */
    .address-title {
        font-size: 1.0rem;
        font-weight: 800;
        color: #1a202c;
        margin-bottom: 8px;
        display: block;
    }
    
    .full-address-label {
        font-size: 0.7rem;
        color: #64748b;
        margin-bottom: 2px;
        display: block;
    }

    /* 전체 주소 박스 크기 축소 (1.0rem -> 0.8rem) */
    .full-address-value {
        font-size: 0.8rem;
        font-weight: 600;
        color: #334155;
        background-color: #f1f5f9;
        padding: 8px;
        border-radius: 6px;
        display: block;
        margin-bottom: 12px;
        line-height: 1.3;
    }

    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 12px;
    }

    /* 라벨 및 수치 크기 축소 (0.8rem -> 0.65rem / 1.1rem -> 0.88rem) */
    .label { font-size: 0.65rem; color: #94a3b8; margin-bottom: 1px; display: block; }
    .value { font-size: 0.88rem; font-weight: 700; color: #1e293b; }
    .highlight-value { font-size: 0.88rem; font-weight: 700; color: #ef4444; }

    /* 버튼 크기 및 폰트 축소 (1.05rem -> 0.85rem) */
    .map-action-btn {
        display: block;
        text-align: center;
        background-color: #03c75a;
        color: white !important;
        padding: 12px;
        border-radius: 10px;
        text-decoration: none !important;
        font-weight: 800;
        font-size: 0.85rem;
    }
    
    /* 검색 팝오버 버튼 크기 축소 */
    div[data-testid="stPopover"] > button {
        width: 100%;
        height: 45px !important;
        font-size: 0.9rem !important;
        border-radius: 10px !important;
        background-color: #2563eb !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="mobile-header">🌊 하천구역 스마트 조회</p>', unsafe_allow_html=True)

# 3. 데이터 로드 설정
region_files = {
    "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "고령군": "03_goryeong.xlsm",
    "달성군": "04_dalseong.xlsm", "달서구": "05_dalseo.xlsm", "문경시": "06_mungyeong.xlsm",
    "안동시": "07_andong.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm",
    "상주시": "10_sangju.xlsm", "성주군": "11_seongju.xlsm"
}

with st.popover("🔍 지역 및 지번 검색"):
    selected_region = st.selectbox("🎯 대상 지역", options=list(region_files.keys()))
    file_path = region_files[selected_region]
    
    if os.path.exists(file_path):
        df = pd.read_excel(file_path, sheet_name=0, header=1)
        df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
        
        dong_list = sorted(df['동리'].dropna().unique())
        target_dong = st.selectbox("📍 동/리", options=["전체 지역"] + list(dong_list))
        search_jibun = st.text_input("🏠 지번 입력 (예: 1080-2)")
    else:
        st.error("데이터 파일이 없습니다.")
        st.stop()

# 4. 필터링 로직
filtered_df = df.copy()
if target_dong != "전체 지역":
    filtered_df = filtered_df[filtered_df['동리'] == target_dong]
if search_jibun:
    filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

# 5. 카드형 결과 출력
st.markdown(f"**총 {len(filtered_df):,}건**")

for _, row in filtered_df.head(30).iterrows():
    full_addr = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
    
    st.markdown(f"""
        <div class="property-card">
            <span class="address-title">📍 {row['동리']} {row['번지']}</span>
            
            <span class="full-address-label">전체 주소</span>
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
            
            <div style="margin-bottom:12px;">
                <span class="label">지목 / 소유자</span>
                <span class="value">{row['지목']} / {row['소유자_성명']}</span>
            </div>

            <a href="https://map.naver.com/v5/search/{full_addr}" target="_blank" class="map-action-btn">📍 네이버 지도 확인</a>
        </div>
    """, unsafe_allow_html=True)