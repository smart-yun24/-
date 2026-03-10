import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="하천구역 스마트 조회", layout="wide", initial_sidebar_state="collapsed")

# CSS 설정 (글자 크기 최적화)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    html, body, [class*="css"] { font-size: 0.95rem; }
    .mobile-header { font-size: 1.1rem !important; font-weight: 800; color: #1e3a8a; text-align: center; margin-bottom: 12px; }
    .property-card { background-color: white; padding: 16px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 15px; border: 1px solid #e2e8f0; }
    .address-title { font-size: 1.0rem; font-weight: 800; color: #1a202c; margin-bottom: 5px; display: block; }
    .full-address-value { font-size: 0.85rem; font-weight: 600; color: #475569; background-color: #f1f5f9; padding: 8px; border-radius: 6px; display: block; margin-bottom: 10px; }
    .map-btn { display: block; text-align: center; background-color: #03c75a; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none !important; font-weight: 800; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="mobile-header">🌊 하천구역 스마트 조회</p>', unsafe_allow_html=True)

# 2. 지자체 파일 매핑
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
        # 데이터 로드
        df = pd.read_excel(file_path, sheet_name=0, header=1)
        
        # [에러 방지 핵심] 항목 개수에 따라 자동으로 이름을 붙여줍니다.
        if len(df.columns) == 10:
            df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
        else:
            # 10개가 아닐 경우 에러를 내지 않고 기본 이름을 유지함
            st.warning(f"참고: '{selected_region}' 파일은 신규 양식(10칸)이 아닙니다. 현재 {len(df.columns)}칸입니다.")

        dong_list = sorted(df['동리'].dropna().unique())
        target_dong = st.selectbox("📍 동/리", options=["전체 지역"] + list(dong_list))
        search_jibun = st.text_input("🏠 지번 입력 (예: 1080-2)")
    else:
        st.error(f"파일을 찾을 수 없습니다: {file_path}")
        st.stop()

# 3. 필터링 및 출력
filtered_df = df.copy()
if target_dong != "전체 지역":
    filtered_df = filtered_df[filtered_df['동리'] == target_dong]
if search_jibun:
    filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

st.markdown(f"**총 {len(filtered_df):,}건**")

# 결과 카드 출력 (상위 50개)
for _, row in filtered_df.head(50).iterrows():
    try:
        full_addr = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
        st.markdown(f"""
            <div class="property-card">
                <span class="address-title">📍 {row['동리']} {row['번지']} ({row['지목']})</span>
                <span class="full-address-value">{full_addr}</span>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <div><span style="font-size:0.7rem; color:gray;">지적</span><br/><b>{row['지적_m2']:,}㎡</b></div>
                    <div style="text-align:right;"><span style="font-size:0.7rem; color:red;">편입</span><br/><b style="color:red;">{row['편입면적_m2']:,}㎡</b></div>
                </div>
                <a href="https://map.naver.com/v5/search/{full_addr}" target="_blank" class="map-btn">지도 위치 확인</a>
            </div>
        """, unsafe_allow_html=True)
    except:
        st.error("일부 데이터를 표시할 수 없습니다. 양식을 확인해 주세요.")