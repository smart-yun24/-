import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="낙동강 상류 조서 조회 서비스", layout="wide", initial_sidebar_state="collapsed")

# 2. UI 디자인 (대시보드 스타일)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    html, body { font-size: 0.98rem; }
    .main-service-title { font-size: 1.0rem !important; font-weight: 800; color: #1e3a8a; text-align: center; margin-bottom: 20px; }
    
    /* 대시보드 메트릭 카드 */
    .metric-card {
        background-color: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
        text-align: center;
    }
    .metric-label { font-size: 0.75rem; color: #64748b; margin-bottom: 5px; }
    .metric-value { font-size: 1.1rem; font-weight: 800; color: #1e3a8a; }

    /* 조서 카드 디자인 (기존 스타일 유지) */
    .property-card { padding: 18px; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 18px; border: 1px solid #e2e8f0; }
    .national-card { background-color: #f0f7ff; border-left: 6px solid #3b82f6; }
    .private-card { background-color: #ffffff; border-left: 6px solid #e2e8f0; }
    .map-btn { display: block; text-align: center; background-color: #03c75a; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none !important; font-weight: 800; font-size: 0.95rem; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# [데이터 집계 함수]
@st.cache_data
def get_total_summary(region_files):
    summary_list = []
    for region, path in region_files.items():
        if os.path.exists(path):
            try:
                df_raw = pd.read_excel(path, sheet_name=0, header=1)
                df = df_raw.iloc[:, :10].copy()
                df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
                
                df['지적_m2'] = pd.to_numeric(df['지적_m2'], errors='coerce').fillna(0)
                df['편입면적_m2'] = pd.to_numeric(df['편입면적_m2'], errors='coerce').fillna(0)
                
                nat_count = df[df['소유자_성명'].astype(str).str.strip().str.startswith('국')].shape[0]
                
                summary_list.append({
                    "지역": region, "필지수": len(df), "국유지": nat_count, "사유지": len(df) - nat_count,
                    "지적합계(㎡)": df['지적_m2'].sum(), "편입합계(㎡)": df['편입면적_m2'].sum()
                })
            except: continue
    return pd.DataFrame(summary_list)

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

region_files = {
    "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "의성군": "08_uiseong.xlsm", 
    "칠곡군": "09_chilgok.xlsm", "성주군": "11_seongju.xlsm", "고령군": "03_goryeong.xlsm",
    "달성군": "04_dalseong.xlsm", "달서구": "05_dalseo.xlsm", "문경시": "06_mungyeong.xlsm",
    "안동시": "07_andong.xlsm", "상주시": "10_sangju.xlsm"
}

tab0, tab1, tab2 = st.tabs(["📊 통합 요약 현황", "하천구역 조회", "폐천부지 조회"])

# --- [Tab 0: 통합 요약 현황] ---
with tab0:
    summary_df = get_total_summary(region_files)
    if not summary_df.empty:
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="metric-card"><div class="metric-label">총 필지 수</div><div class="metric-value">{summary_df["필지수"].sum():,} 건</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="metric-label">총 지적면적</div><div class="metric-value">{summary_df["지적합계(㎡)"].sum():,.0f} ㎡</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><div class="metric-label">국유지 비율</div><div class="metric-value">{(summary_df["국유지"].sum()/summary_df["필지수"].sum()*100):.1f}%</div></div>', unsafe_allow_html=True)
        
        st.write("")
        st.dataframe(summary_df.style.format({
            "필지수": "{:,}", "국유지": "{:,}", "사유지": "{:,}", "지적합계(㎡)": "{:,.0f}", "편입합계(㎡)": "{:,.0f}"
        }), use_container_width=True, hide_index=True)
    else:
        st.info("데이터 파일을 업로드하면 집계가 시작됩니다.")

# --- [Tab 1: 하천구역 조회] ---
with tab1:
    with st.popover("🔍 지역 및 지번 검색"):
        sel_reg = st.selectbox("🎯 대상 지역 선택", options=list(region_files.keys()), key="river_reg")
        df = load_data(region_files[sel_reg])
        if df is not None:
            dong_list = sorted(df['동리'].dropna().unique())
            sel_dong = st.selectbox("📍 동/리 선택", options=["전체 지역"] + list(dong_list), key="river_dong")
            search_jb = st.text_input("🏠 지번 입력 (예: 1080-2)", key="river_jb")

    if df is not None:
        filtered = df.copy()
        if sel_dong != "전체 지역": filtered = filtered[filtered['동리'] == sel_dong]
        if search_jb: filtered = filtered[filtered['번지'].astype(str).str.contains(search_jb)]
        
        st.markdown(f"**현재 조회된 필지: {len(filtered):,}건**")
        for _, row in filtered.head(30).iterrows():
            owner_raw = str(row['소유자_성명']).strip()
            display_owner = str(row['소유자_주소']).strip() if owner_raw == '국' else owner_raw
            c_type = "national-card" if display_owner.startswith('국') else "private-card"
            st.markdown(f"""
                <div class="property-card {c_type}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <span style="font-size:1.05rem; font-weight:800;">📍 {row['시군']} {row['읍면']} {row['동리']} {row['번지']}</span>
                        <span class="owner-badge">{display_owner}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; background: rgba(248, 250, 252, 0.8); padding: 12px; border-radius: 10px;">
                        <div><span style="font-size:0.75rem; color:#64748b;">지적면적</span><br/><b>{row['지적_m2']:,}㎡</b></div>
                        <div style="text-align:right;"><span style="font-size:0.75rem; color:#ef4444;">편입면적</span><br/><b style="color:#ef4444;">{row['편입면적_m2']:,}㎡</b></div>
                    </div>
                    <a href="https://map.naver.com/v5/search/{row['시군']} {row['읍면']} {row['동리']} {row['번지']}" target="_blank" class="map-btn">🗺️ 지도확인(NAVER)</a>
                </div>
            """, unsafe_allow_html=True)

# --- [Tab 2: 폐천부지 조회] ---
with tab2:
    st.info("폐천부지 양식을 올려주시면 이곳에 맞춤형 화면이 구성됩니다.")