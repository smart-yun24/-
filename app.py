import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="낙동강 상류 조서 조회 서비스", layout="wide", initial_sidebar_state="collapsed")

# 2. 통합 플랫폼 UI 디자인 (탭 디자인 및 기존 카드 스타일 통합)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    html, body { font-size: 0.98rem; } 
    
    /* 메인 타이틀 스타일 */
    .main-service-title { 
        font-size: 1.2rem !important; 
        font-weight: 800; 
        color: #1e3a8a; 
        text-align: center; 
        margin-bottom: 20px; 
    }
    
    /* 상단 메뉴 탭 스타일 조정 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #ffffff;
        border-radius: 10px 10px 0px 0px;
        padding: 0px 20px;
        font-weight: 700;
    }

    /* 필지 카드 및 색상 구분 디자인 */
    .property-card {
        padding: 18px; border-radius: 14px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 18px; 
        border: 1px solid #e2e8f0;
    }
    .national-card { background-color: #f0f7ff; border-left: 6px solid #3b82f6; }
    .private-card { background-color: #ffffff; border-left: 6px solid #e2e8f0; }

    /* 텍스트 및 뱃지 스타일 */
    .address-text { font-size: 1.05rem; font-weight: 800; color: #0f172a; line-height: 1.4; }
    .owner-badge {
        font-size: 0.82rem; font-weight: 700; color: #2563eb;
        background-color: #ffffff; padding: 4px 10px; border-radius: 8px;
        white-space: nowrap; border: 1px solid #dbeafe;
    }
    
    /* 검색 팝오버 및 버튼 */
    div[data-testid="stPopover"] > button {
        width: 100%; height: 50px !important; font-size: 1.0rem !important; font-weight: 800 !important;
        border-radius: 12px !important; background-color: #2563eb !important; color: white !important;
    }
    div[data-testid="stPopover"] label, div[data-testid="stPopover"] input { font-size: 0.65rem !important; }

    .map-action-btn {
        display: block; text-align: center; background-color: #03c75a; color: white !important; 
        padding: 12px; border-radius: 10px; text-decoration: none !important; font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# [데이터 로딩 캐싱]
@st.cache_data
def load_river_data(file_path):
    if os.path.exists(file_path):
        df_raw = pd.read_excel(file_path, sheet_name=0, header=1)
        df = df_raw.iloc[:, :10].copy()
        df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
        return df
    return None

# 메인 타이틀
st.markdown('<p class="main-service-title">낙동강 상류 조서 조회 서비스</p>', unsafe_allow_html=True)

# 3. 서비스 전환 탭 생성
tab1, tab2 = st.tabs(["🌊 하천구역 조회", "🍂 폐천부지 조회"])

# --- [Tab 1: 하천구역 서비스] ---
with tab1:
    region_files = {
        "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "고령군": "03_goryeong.xlsm",
        "달성군": "04_dalseong.xlsm", "달서구": "05_dalseo.xlsm", "문경시": "06_mungyeong.xlsm",
        "안동시": "07_andong.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm",
        "상주시": "10_sangju.xlsm", "성주군": "11_seongju.xlsm"
    }

    with st.popover("🔍 하천구역 필지 검색"):
        selected_region = st.selectbox("🎯 대상 지역 선택", options=list(region_files.keys()), key="river_reg")
        file_path = region_files[selected_region]
        df = load_river_data(file_path)
        
        if df is not None:
            dong_list = sorted(df['동리'].dropna().unique())
            target_dong = st.selectbox("📍 동/리 선택", options=["전체 지역"] + list(dong_list), key="river_dong")
            search_jibun = st.text_input("🏠 지번 입력 (예: 1080-2)", key="river_jibun")
        else:
            st.error("데이터 파일을 찾을 수 없습니다.")

    if df is not None:
        filtered_df = df.copy()
        if target_dong != "전체 지역":
            filtered_df = filtered_df[filtered_df['동리'] == target_dong]
        if search_jibun:
            filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

        st.markdown(f"**조회 결과: {len(filtered_df):,}건**")

        for _, row in filtered_df.head(50).iterrows():
            full_addr = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
            owner_raw = str(row['소유자_성명']).strip()
            display_owner = str(row['소유자_주소']).strip() if owner_raw == '국' else owner_raw
            card_type = "national-card" if display_owner.startswith('국') else "private-card"
            
            st.markdown(f"""
                <div class="property-card {card_type}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <span class="address-text">📍 {full_addr}</span>
                        <span class="owner-badge">{display_owner}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; background: rgba(255,255,255,0.5); padding: 10px; border-radius: 8px;">
                        <div><span style="font-size:0.75rem; color:#64748b;">지적</span><br/><b>{row['지적_m2']:,}㎡</b></div>
                        <div style="text-align:right;"><span style="font-size:0.75rem; color:#ef4444;">편입</span><br/><b style="color:#ef4444;">{row['편입면적_m2']:,}㎡</b></div>
                    </div>
                    <a href="https://map.naver.com/v5/search/{full_addr}" target="_blank" class="map-action-btn">🗺️ 네이버 지도 확인</a>
                </div>
            """, unsafe_allow_html=True)

# --- [Tab 2: 폐천부지 서비스 (뼈대)] ---
with tab2:
    st.info("🍂 폐천부지 조회 서비스를 준비 중입니다.")
    st.warning("매니저님, 폐천부지 엑셀 파일을 공유해주시면 여기에 맞춤형 조서 화면을 바로 구성해 드릴게요!")
    
    # 향후 폐천부지 전용 검색 필터가 들어갈 자리
    st.markdown("""
        ### 📋 폐천부지 기능 예정 사항
        * 폐천부지 전용 필지 조회
        * 용도폐지 여부 및 폐천일자 확인
        * 국유재산 관리 번호 연동 등
    """)