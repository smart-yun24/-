import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="낙동강 상류 조서 조회 서비스", layout="wide", initial_sidebar_state="collapsed")

# [핵심] 데이터 로딩 함수에 캐싱 적용 (렉 방지)
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        # 엑셀을 한 번만 읽고 메모리에 저장합니다.
        df_raw = pd.read_excel(file_path, sheet_name=0, header=1)
        df = df_raw.iloc[:, :10].copy()
        df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
        return df
    return None

# 디자인 CSS (기존과 동일)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    html, body { font-size: 0.98rem; } 
    .main-service-title { font-size: 1.15rem !important; font-weight: 800; color: #1e3a8a; text-align: center; margin-bottom: 15px; }
    .property-card { padding: 18px; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 18px; border: 1px solid #e2e8f0; }
    .national-card { background-color: #f0f7ff; border-left: 6px solid #3b82f6; }
    .private-card { background-color: #ffffff; border-left: 6px solid #e2e8f0; }
    .card-header-flex { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; margin-bottom: 12px; }
    .address-text { font-size: 1.05rem; font-weight: 800; color: #0f172a; line-height: 1.4; flex: 1; }
    .owner-badge { font-size: 0.82rem; font-weight: 700; color: #2563eb; background-color: #ffffff; padding: 4px 10px; border-radius: 8px; white-space: nowrap; border: 1px solid #dbeafe; }
    .info-container { display: flex; justify-content: space-between; background-color: rgba(248, 250, 252, 0.8); padding: 12px; border-radius: 10px; border: 1px solid rgba(0,0,0,0.03); }
    .map-action-btn { display: block; text-align: center; background-color: #03c75a; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none !important; font-weight: 800; font-size: 0.95rem; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-service-title">낙동강 상류 조서 조회 서비스</p>', unsafe_allow_html=True)

# 지자체 매핑
region_files = {
    "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "고령군": "03_goryeong.xlsm",
    "달성군": "04_dalseong.xlsm", "달서구": "05_dalseo.xlsm", "문경시": "06_mungyeong.xlsm",
    "안동시": "07_andong.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm",
    "상주시": "10_sangju.xlsm", "성주군": "11_seongju.xlsm"
}

with st.popover("🔍 지역 및 지번 검색"):
    selected_region = st.selectbox("🎯 대상 지역", options=list(region_files.keys()))
    file_path = region_files[selected_region]
    
    # 캐싱된 함수 호출
    df = load_data(file_path)
    
    if df is not None:
        dong_list = sorted(df['동리'].dropna().unique())
        target_dong = st.selectbox("📍 동/리 선택", options=["전체 지역"] + list(dong_list))
        search_jibun = st.text_input("🏠 지번 입력 (예: 1080-2)")
    else:
        st.error(f"파일 없음: {file_path}")
        st.stop()

# 필터링 및 출력 (하위 로직 동일)
filtered_df = df.copy()
if target_dong != "전체 지역":
    filtered_df = filtered_df[filtered_df['동리'] == target_dong]
if search_jibun:
    filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

st.markdown(f"**현재 조회된 필지: {len(filtered_df):,}건**")

for _, row in filtered_df.head(50).iterrows():
    full_addr = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
    owner_raw = str(row['소유자_성명']).strip()
    addr_raw = str(row['소유자_주소']).strip()
    display_owner = addr_raw if owner_raw == '국' else owner_raw
    is_national = display_owner.startswith('국')
    card_type = "national-card" if is_national else "private-card"
    
    st.markdown(f"""
        <div class="property-card {card_type}">
            <div class="card-header-flex">
                <span class="address-text">📍 {full_addr}</span>
                <span class="owner-badge">{display_owner}</span>
            </div>
            <div class="info-container">
                <div><span style="font-size:0.75rem; color:#64748b;">지적면적</span><br/><b>{row['지적_m2']:,}㎡</b></div>
                <div style="text-align:right;"><span style="font-size:0.75rem; color:#ef4444;">편입면적</span><br/><b style="color:#ef4444;">{row['편입면적_m2']:,}㎡</b></div>
            </div>
            <a href="https://map.naver.com/v5/search/{full_addr}" target="_blank" class="map-action-btn">🗺️ 위치 확인 (네이버 지도)</a>
        </div>
    """, unsafe_allow_html=True)