import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="낙동강 상류 조서 조회 서비스", layout="wide", initial_sidebar_state="collapsed")

# 2. UI 디자인 (문구 수정 및 성능 최적화 스타일)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    html, body { font-size: 0.98rem; } 
    
    .main-service-title { 
        font-size: 0.85rem !important; 
        font-weight: 800; 
        color: #1e3a8a; 
        text-align: center; 
        margin-bottom: 15px; 
    }
    
    /* 검색 버튼 스타일 */
    div[data-testid="stPopover"] > button {
        width: 100%; height: 42px !important;
        font-size: 0.85rem !important; font-weight: 800 !important;
        border-radius: 10px !important; background-color: #2563eb !important;
        color: white !important;
    }

    /* 조서 카드 디자인 (해치 없이 색상으로만 구분하여 성능 극대화) */
    .property-card {
        padding: 18px; border-radius: 14px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 18px; 
        border: 1px solid #e2e8f0;
    }
    .national-card { background-color: #f0f7ff; border-left: 6px solid #3b82f6; } 
    .private-card { background-color: #ffffff; border-left: 6px solid #e2e8f0; }
    .abandoned-card { background-color: #fffaf0; border-left: 6px solid #f59e0b; }

    .address-text { font-size: 1.05rem; font-weight: 800; color: #0f172a; line-height: 1.4; flex: 1; }
    .owner-badge {
        font-size: 0.82rem; font-weight: 700; color: #2563eb;
        background-color: #ffffff; padding: 3px 10px; border-radius: 8px;
        white-space: nowrap; border: 1px solid #dbeafe;
    }

    .info-container { 
        display: flex; justify-content: space-between; 
        background-color: rgba(248, 250, 252, 0.8); padding: 12px; border-radius: 10px; 
    }
    
    /* 네이버 지도 버튼 스타일 */
    .map-btn {
        display: block; text-align: center; background-color: #03c75a; color: white !important; 
        padding: 12px; border-radius: 10px; text-decoration: none !important; 
        font-weight: 800; font-size: 0.95rem; margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# [데이터 캐싱]
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            df_raw = pd.read_excel(file_path, sheet_name=0, header=1)
            df = df_raw.iloc[:, :10].copy()
            df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
            return df
        except: return None
    return None

st.markdown('<p class="main-service-title">낙동강 상류 조서 조회 서비스</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["하천구역 조회", "폐천부지 조회"])

with tab1:
    region_files = {
        "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "고령군": "03_goryeong.xlsm",
        "달성군": "04_dalseong.xlsm", "달서구": "05_dalseo.xlsm", "문경시": "06_mungyeong.xlsm",
        "안동시": "07_andong.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm",
        "상주시": "10_sangju.xlsm", "성주군": "11_seongju.xlsm"
    }

    with st.popover("🔍 지역 및 지번 검색"):
        sel_reg = st.selectbox("🎯 대상 지역 선택", options=list(region_files.keys()), key="river_reg")
        df = load_data(region_files[sel_reg])
        
        if df is not None:
            dong_list = sorted(df['동리'].dropna().unique())
            sel_dong = st.selectbox("📍 동/리 선택", options=["전체 지역"] + list(dong_list), key="river_dong")
            search_jb = st.text_input("🏠 지번 입력 (예: 1080-2)", key="river_jb")
        else:
            st.warning(f"'{sel_reg}' 데이터 파일이 아직 업로드되지 않았습니다.")

    if df is not None:
        filtered = df.copy()
        if sel_dong != "전체 지역": filtered = filtered[filtered['동리'] == sel_dong]
        if search_jb: filtered = filtered[filtered['번지'].astype(str).str.contains(search_jb)]

        st.markdown(f"**현재 조회된 필지: {len(filtered):,}건**")

        for _, row in filtered.head(30).iterrows():
            full_addr = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
            owner_raw = str(row['소유자_성명']).strip()
            # [국유지 부처명 상세화]
            display_owner = str(row['소유자_주소']).strip() if owner_raw == '국' else owner_raw
            
            c_type = "national-card" if display_owner.startswith('국') else "private-card"
            
            st.markdown(f"""
                <div class="property-card {c_type}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <span class="address-text">📍 {full_addr}</span>
                        <span class="owner-badge">{display_owner}</span>
                    </div>
                    <div class="info-container">
                        <div><span style="font-size:0.75rem; color:#64748b;">지적면적</span><br/><b>{row['지적_m2']:,}㎡</b></div>
                        <div style="text-align:right;"><span style="font-size:0.75rem; color:#ef4444;">편입면적</span><br/><b style="color:#ef4444;">{row['편입면적_m2']:,}㎡</b></div>
                    </div>
                    <a href="https://map.naver.com/v5/search/{full_addr}" target="_blank" class="map-btn">🗺️ 지도확인(NAVER)</a>
                </div>
            """, unsafe_allow_html=True)

# --- [폐천부지 조회 서비스] ---
with tab2:
    st.markdown("""
        <div class="property-card abandoned-card" style="text-align:center; padding:40px 20px;">
            <h3 style="color:#d97706; margin-bottom:10px;">🚧 폐천부지 조회 준비 중</h3>
            <p style="color:#92400e;">폐천부지 엑셀 양식을 올려주시면 즉시 연결됩니다.</p>
        </div>
    """, unsafe_allow_html=True)