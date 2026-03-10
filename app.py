import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="낙동강 상류 조서 조회 서비스", layout="wide", initial_sidebar_state="collapsed")

# 2. 통합 UI/UX 디자인 (타이틀 1.0rem, 해치 제거, 본문 가독성 최적화)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    html, body { font-size: 0.98rem; }
    
    /* 최상단 제목 (1.0rem) */
    .main-service-title { 
        font-size: 1.0rem !important; font-weight: 800; color: #1e3a8a; 
        text-align: center; margin-bottom: 20px; 
    }
    
    /* 대시보드 메트릭 카드 */
    .metric-container { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
    .metric-card {
        flex: 1; min-width: 160px; background-color: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center;
    }
    .metric-label { font-size: 0.75rem; color: #64748b; margin-bottom: 5px; }
    .metric-value { font-size: 1.1rem; font-weight: 800; color: #1e3a8a; }

    /* 검색 팝오버 버튼 (0.85rem) */
    div[data-testid="stPopover"] > button {
        width: 100%; height: 42px !important; font-size: 0.85rem !important; 
        font-weight: 800 !important; border-radius: 10px !important; 
        background-color: #2563eb !important; color: white !important;
    }
    div[data-testid="stPopover"] label, div[data-testid="stPopover"] input { font-size: 0.65rem !important; }

    /* 조서 카드 공통 디자인 */
    .property-card { padding: 18px; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 18px; border: 1px solid #e2e8f0; }
    
    /* 하천구역 테마 (블루) */
    .national-card { background-color: #f0f7ff; border-left: 6px solid #3b82f6; }
    .private-card { background-color: #ffffff; border-left: 6px solid #e2e8f0; }
    
    /* 폐천부지 테마 (오렌지) */
    .abandoned-card { background-color: #fffaf0; border-left: 6px solid #f59e0b; }
    .plan-badge { 
        font-size: 0.7rem; font-weight: 700; color: #92400e; 
        background-color: #fef3c7; padding: 2px 8px; border-radius: 4px; margin-left: 5px;
    }

    .address-text { font-size: 1.05rem; font-weight: 800; color: #0f172a; line-height: 1.4; }
    .owner-badge { font-size: 0.82rem; font-weight: 700; color: #2563eb; background-color: #ffffff; padding: 3px 10px; border-radius: 8px; border: 1px solid #dbeafe; }
    
    .info-container { display: flex; justify-content: space-between; background: rgba(248, 250, 252, 0.8); padding: 12px; border-radius: 10px; }
    
    /* 지도 버튼 문구 수정 */
    .map-btn { display: block; text-align: center; background-color: #03c75a; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none !important; font-weight: 800; font-size: 0.95rem; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# [데이터 캐싱 및 로딩 함수]
@st.cache_data
def load_and_summarize(river_files, delete_files):
    summary_list = []
    # 하천구역 요약
    for region, path in river_files.items():
        if os.path.exists(path):
            try:
                df = pd.read_excel(path, sheet_name=0, header=1).iloc[:, :10]
                df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적', '편입', '주소', '성명']
                df['지적'] = pd.to_numeric(df['지적'], errors='coerce').fillna(0)
                df['편입'] = pd.to_numeric(df['편입'], errors='coerce').fillna(0)
                nat = df[df['성명'].astype(str).str.strip().str.startswith('국')].shape[0]
                summary_list.append({
                    "지역": region, "구분": "하천구역", "필지수": len(df), "국유지": nat, "사유지": len(df)-nat,
                    "지적합계": df['지적'].sum(), "편입합계": df['편입'].sum()
                })
            except: pass
    # 폐천부지 요약
    for region, path in delete_files.items():
        if os.path.exists(path):
            try:
                df = pd.read_excel(path, sheet_name=0, header=1).iloc[:, :11]
                df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적', '편입', '계획', '주소', '성명']
                df['지적'] = pd.to_numeric(df['지적'], errors='coerce').fillna(0)
                df['편입'] = pd.to_numeric(df['편입'], errors='coerce').fillna(0)
                nat = df[df['성명'].astype(str).str.strip().str.startswith('국')].shape[0]
                summary_list.append({
                    "지역": region, "구분": "폐천부지", "필지수": len(df), "국유지": nat, "사유지": len(df)-nat,
                    "지적합계": df['지적'].sum(), "편입합계": df['편입'].sum()
                })
            except: pass
    return pd.DataFrame(summary_list)

@st.cache_data
def load_single_file(path, mode="river"):
    if not os.path.exists(path): return None
    try:
        df_raw = pd.read_excel(path, sheet_name=0, header=1)
        if mode == "river":
            df = df_raw.iloc[:, :10].copy()
            df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적', '편입', '주소', '성명']
        else:
            df = df_raw.iloc[:, :11].copy()
            df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적', '편입', '계획', '주소', '성명']
        return df
    except: return None

# 파일 맵 설정
river_files = { "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm", "성주군": "11_seongju.xlsm", "고령군": "03_goryeong.xlsm", "달성군": "04_dalseong.xlsm", "문경시": "06_mungyeong.xlsm", "안동시": "07_andong.xlsm" }
delete_files = { "예천군": "01_yecheon_delete.xlsm", "구미시": "02_gumi_delete.xlsm", "의성군": "08_uiseong_delete.xlsm" }

st.markdown('<p class="main-service-title">낙동강 상류 조서 조회 서비스</p>', unsafe_allow_html=True)

tab0, tab1, tab2 = st.tabs(["📊 통합 요약 현황", "하천구역 조회", "폐천부지 조회"])

# --- [Tab 0: 통합 요약 현황] ---
with tab0:
    
    sum_df = load_and_summarize(river_files, delete_files)
    if not sum_df.empty:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-card"><div class="metric-label">총 필지 수</div><div class="metric-value">{sum_df["필지수"].sum():,}건</div></div>
                <div class="metric-card"><div class="metric-label">총 지적면적 합계</div><div class="metric-value">{sum_df["지적합계"].sum():,.0f}㎡</div></div>
                <div class="metric-card"><div class="metric-label">총 편입합계</div><div class="metric-value" style="color:#ef4444;">{sum_df["편입합계"].sum():,.0f}㎡</div></div>
                <div class="metric-card"><div class="metric-label">국유지 비율</div><div class="metric-value">{(sum_df["국유지"].sum()/sum_df["필지수"].sum()*100):.1f}%</div></div>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.markdown("**📍 상세 요약 현황**")
        st.dataframe(sum_df.style.format({"필지수": "{:,}", "국유지": "{:,}", "사유지": "{:,}", "지적합계": "{:,.0f}", "편입합계": "{:,.0f}"}), use_container_width=True, hide_index=True)
    else: st.info("데이터 파일을 올려주세요.")

# --- [Tab 1: 하천구역 조회] ---
with tab1:
    with st.popover("🔍 지역 및 지번 검색"):
        sel_reg = st.selectbox("🎯 지역", options=list(river_files.keys()), key="r_reg")
        df = load_single_file(river_files[sel_reg], "river")
        if df is not None:
            dong = st.selectbox("📍 동/리", options=["전체"] + sorted(df['동리'].dropna().unique().tolist()), key="r_dong")
            jb = st.text_input("🏠 지번", key="r_jb")
    
    if df is not None:
        res = df.copy()
        if dong != "전체": res = res[res['동리'] == dong]
        if jb: res = res[res['번지'].astype(str).str.contains(jb)]
        st.markdown(f"**조회: {len(res):,}건**")
        for _, row in res.head(30).iterrows():
            owner = str(row['주소']).strip() if str(row['성명']).strip() == '국' else str(row['성명']).strip()
            c_type = "national-card" if owner.startswith('국') else "private-card"
            st.markdown(f"""
                <div class="property-card {c_type}">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
                        <span class="address-text">📍 {row['시군']} {row['읍면']} {row['동리']} {row['번지']}</span>
                        <span class="owner-badge">{owner}</span>
                    </div>
                    <div class="info-container">
                        <div><span style="font-size:0.7rem; color:#64748b;">지적</span><br/><b>{row['지적']:,}㎡</b></div>
                        <div style="text-align:right;"><span style="font-size:0.7rem; color:#ef4444;">편입</span><br/><b style="color:#ef4444;">{row['편입']:,}㎡</b></div>
                    </div>
                    <a href="https://map.naver.com/v5/search/{row['시군']} {row['읍면']} {row['동리']} {row['번지']}" target="_blank" class="map-btn">지도확인(NAVER)</a>
                </div>
            """, unsafe_allow_html=True)

# --- [Tab 2: 폐천부지 조회] ---
with tab2:
    
    with st.popover("🔍 폐천부지 검색"):
        sel_reg_d = st.selectbox("🎯 지역", options=list(delete_files.keys()), key="d_reg")
        df_d = load_single_file(delete_files[sel_reg_d], "delete")
        if df_d is not None:
            dong_d = st.selectbox("📍 동/리", options=["전체"] + sorted(df_d['동리'].dropna().unique().tolist()), key="d_dong")
            jb_d = st.text_input("🏠 지번", key="d_jb")
    
    if df_d is not None:
        res_d = df_d.copy()
        if dong_d != "전체": res_d = res_d[res_d['동리'] == dong_d]
        if jb_d: res_d = res_d[res_d['번지'].astype(str).str.contains(jb_d)]
        st.markdown(f"**조회: {len(res_d):,}건**")
        for _, row in res_d.head(30).iterrows():
            owner = str(row['주소']).strip() if str(row['성명']).strip() == '국' else str(row['성명']).strip()
            st.markdown(f"""
                <div class="property-card abandoned-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
                        <span class="address-text">📍 {row['시군']} {row['읍면']} {row['동리']} {row['번지']} <span class="plan-badge">{row['계획']}</span></span>
                        <span class="owner-badge">{owner}</span>
                    </div>
                    <div class="info-container">
                        <div><span style="font-size:0.7rem; color:#64748b;">지적</span><br/><b>{row['지적']:,}㎡</b></div>
                        <div style="text-align:right;"><span style="font-size:0.7rem; color:#ef4444;">편입</span><br/><b style="color:#ef4444;">{row['편입']:,}㎡</b></div>
                    </div>
                    <a href="https://map.naver.com/v5/search/{row['시군']} {row['읍면']} {row['동리']} {row['번지']}" target="_blank" class="map-btn">지도확인(NAVER)</a>
                </div>
            """, unsafe_allow_html=True)