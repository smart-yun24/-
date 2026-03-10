import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="하천구역 스마트 조회", layout="wide", initial_sidebar_state="collapsed")

# 2. UI 디자인 (좌우 분할 레이아웃 및 소유자 뱃지 추가)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    html, body { font-size: 0.85rem; }
    
    .mobile-header { 
        font-size: 1.0rem !important; 
        font-weight: 800; 
        color: #1e3a8a; 
        text-align: center; 
        margin-bottom: 12px; 
    }
    
    /* 팝오버 디자인 */
    div[data-testid="stPopover"] > button {
        width: 100%;
        height: 45px !important;
        font-size: 1.0rem !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        background-color: #2563eb !important;
        color: white !important;
    }

    /* 필터 내부 폰트 (지난번 설정 유지) */
    div[data-testid="stPopover"] label, 
    div[data-testid="stPopover"] div[data-baseweb="select"], 
    div[data-testid="stPopover"] input {
        font-size: 0.65rem !important; 
    }
    
    /* 카드 디자인 */
    .property-card {
        background-color: white; padding: 14px; border-radius: 12px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 15px; border: 1px solid #e2e8f0;
    }

    /* [2번 반영] 주소와 소유자 성명 좌우 분리 레이아웃 */
    .card-header-flex {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 8px;
        margin-bottom: 10px;
    }
    
    .address-text { 
        font-size: 0.9rem; 
        font-weight: 800; 
        color: #0f172a; 
        line-height: 1.3;
        flex: 1; /* 주소가 가용한 공간을 다 쓰도록 설정 */
    }

    /* 소유자 뱃지 스타일 */
    .owner-badge {
        font-size: 0.75rem;
        font-weight: 700;
        color: #2563eb;
        background-color: #eff6ff;
        padding: 3px 8px;
        border-radius: 6px;
        white-space: nowrap; /* 이름이 길어도 줄바꿈 방지 */
        border: 1px solid #dbeafe;
    }

    /* 지목 뱃지 */
    .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; margin-bottom: 6px; }
    .badge-천 { background-color: #e0f2fe; color: #0369a1; }
    .badge-임 { background-color: #dcfce7; color: #15803d; }
    .badge-전, .badge-답 { background-color: #fef9c3; color: #a16207; }
    .badge-제 { background-color: #f1f5f9; color: #475569; }
    .badge-default { background-color: #f3f4f6; color: #374151; }

    .info-container { 
        display: flex; justify-content: space-between; 
        background-color: #f8fafc; padding: 10px; border-radius: 8px; margin-bottom: 12px;
    }
    .label { font-size: 0.65rem; color: #64748b; }
    .value { font-size: 0.85rem; font-weight: 700; color: #1e293b; }
    .value-red { font-size: 0.85rem; font-weight: 700; color: #ef4444; }

    .map-action-btn {
        display: block; text-align: center; background-color: #03c75a; color: white !important; 
        padding: 10px; border-radius: 8px; text-decoration: none !important; 
        font-weight: 800; font-size: 0.85rem;
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
        df_raw = pd.read_excel(file_path, sheet_name=0, header=1)
        df = df_raw.iloc[:, :10].copy()
        df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
        
        dong_list = sorted(df['동리'].dropna().unique())
        target_dong = st.selectbox("📍 동/리 선택", options=["전체 지역"] + list(dong_list))
        search_jibun = st.text_input("🏠 지번 입력 (예: 1080-2)")
    else:
        st.error(f"파일을 찾을 수 없습니다: {file_path}")
        st.stop()

# 4. 필터링 및 출력
filtered_df = df.copy()
if target_dong != "전체 지역":
    filtered_df = filtered_df[filtered_df['동리'] == target_dong]
if search_jibun:
    filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

st.markdown(f"**총 {len(filtered_df):,}건**")

for _, row in filtered_df.head(50).iterrows():
    full_addr = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
    jimok = str(row['지목'])
    badge_class = f"badge-{jimok}" if jimok in ['천', '임', '전', '답', '제'] else "badge-default"
    
    st.markdown(f"""
        <div class="property-card">
            <span class="badge {badge_class}">{jimok}</span>
            <div class="card-header-flex">
                <span class="address-text">📍 {full_addr}</span>
                <span class="owner-badge">{row['소유자_성명']}</span>
            </div>
            <div class="info-container">
                <div><span class="label">지적면적</span><br/><span class="value">{row['지적_m2']:,}㎡</span></div>
                <div style="text-align:right;"><span class="label" style="color:#ef4444;">편입면적</span><br/><span class="value-red">{row['편입면적_m2']:,}㎡</span></div>
            </div>
            <a href="https://map.naver.com/v5/search/{full_addr}" target="_blank" class="map-action-btn">🗺️ 지도 확인</a>
        </div>
    """, unsafe_allow_html=True)