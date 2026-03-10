import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="낙동강 상류 조서 조회 서비스", layout="wide", initial_sidebar_state="collapsed")

# 2. 유신 시그니처 테마 (Professional Deep Ocean & Glassmorphism)
st.markdown("""
    <style>
    /* 전체 배경: 눈이 편안한 Off-white */
    .stApp { background-color: #f8fafc; }
    html, body { font-size: 0.98rem; font-family: 'Pretendard', -apple-system, sans-serif; }
    
    /* 타이틀 스타일 (1.0rem, Deep Navy) */
    .main-service-title { 
        font-size: 1.0rem !important; font-weight: 800; color: #1e3a8a; 
        text-align: center; margin-bottom: 25px; letter-spacing: -0.02em;
    }
    
    /* 요약 현황 전환 버튼 (Slate 스타일) */
    .stButton > button { 
        width: 100%; border-radius: 10px; font-weight: 700; height: 45px; 
        border: 1px solid #e2e8f0; background-color: white; color: #475569;
        transition: all 0.2s ease;
    }
    .stButton > button:hover { border-color: #1e3a8a; color: #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }

    /* 메트릭 카드 (Glassmorphism Lite) */
    .metric-container { display: flex; gap: 12px; margin-bottom: 25px; flex-wrap: wrap; }
    .metric-card {
        flex: 1; min-width: 170px; background-color: white; padding: 20px; border-radius: 14px;
        border: 1px solid #f1f5f9; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    .metric-label { font-size: 0.75rem; color: #64748b; margin-bottom: 8px; font-weight: 600; }
    .metric-value { font-size: 1.15rem; font-weight: 800; color: #1e3a8a; }
    .metric-value-red { color: #dc2626; }

    /* 조서 카드 공통 디자인 */
    .property-card { 
        padding: 20px; border-radius: 16px; margin-bottom: 20px; 
        border: 1px solid #f1f5f9; background-color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    .property-card:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
    
    .national-card { border-left: 5px solid #1e3a8a; }
    .private-card { border-left: 5px solid #94a3b8; }
    
    /* 폐천부지 카드 배경색 전체 적용 */
    .abandoned-card-보전 { background-color: #f0f7ff !important; border-left: 5px solid #2563eb; border: 1px solid #dbeafe; }
    .abandoned-card-처분 { background-color: #fff7ed !important; border-left: 5px solid #ea580c; border: 1px solid #ffedd5; }

    .address-text { font-size: 1.05rem; font-weight: 800; color: #0f172a; line-height: 1.5; }
    .owner-badge { font-size: 0.8rem; font-weight: 700; color: #1e3a8a; background-color: #eff6ff; padding: 4px 12px; border-radius: 8px; border: 1px solid #dbeafe; }
    
    .info-container { display: flex; justify-content: space-between; background: rgba(255, 255, 255, 0.6); padding: 14px; border-radius: 12px; margin-top: 10px; border: 1px solid rgba(0,0,0,0.03); }
    
    /* 버튼 레이아웃 및 스타일 */
    .btn-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 18px; }
    .map-btn { 
        display: block; text-align: center; background-color: #03c75a !important; color: white !important; 
        padding: 12px; border-radius: 10px; text-decoration: none !important; 
        font-weight: 800; font-size: 0.9rem; box-shadow: 0 4px 6px rgba(3, 199, 90, 0.2);
    }
    .eum-btn { 
        display: block; text-align: center; background-color: #1e3a8a !important; color: white !important; 
        padding: 12px; border-radius: 10px; text-decoration: none !important; 
        font-weight: 800; font-size: 0.9rem; box-shadow: 0 4px 6px rgba(30, 58, 138, 0.2);
    }
    
    /* 필터 박스 */
    .filter-box { background-color: white; padding: 15px 20px; border-radius: 14px; border: 1px solid #e2e8f0; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    
    div[data-testid="stPopover"] > button { width: 100%; height: 45px !important; font-size: 0.85rem !important; font-weight: 800 !important; background-color: #2563eb !important; color: white !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# [데이터 처리 로직]
@st.cache_data
def get_summary(file_map, mode="river"):
    data_list = []
    for region, path in file_map.items():
        if os.path.exists(path):
            try:
                df = pd.read_excel(path, sheet_name=0, header=1)
                owner_idx = 9 if mode == "river" else 10
                df_clean = df.iloc[:, [1, 6, 7]].copy()
                df_clean.columns = ['시군', '지적', '편입']
                df_clean['지적'] = pd.to_numeric(df_clean['지적'], errors='coerce').fillna(0)
                df_clean['편입'] = pd.to_numeric(df_clean['편입'], errors='coerce').fillna(0)
                nat_count = df[df.columns[owner_idx]].astype(str).str.strip().str.startswith('국').sum()
                data_list.append({
                    "지역명": region, "필지수": len(df_clean), "국유지(필지)": nat_count, "사유지(필지)": len(df_clean)-nat_count,
                    "지적면적 합계(㎡)": df_clean['지적'].sum(), "편입면적 합계(㎡)": df_clean['편입'].sum()
                })
            except: pass
    return pd.DataFrame(data_list)

@st.cache_data
def load_file(path, mode="river"):
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

# 파일 리스트 설정
river_files = { "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm", "성주군": "11_seongju.xlsm", "고령군": "03_goryeong.xlsm", "달성군": "04_dalseong.xlsm", "문경시": "06_mungyeong.xlsm", "안동시": "07_andong.xlsm", "상주시": "10_sangju.xlsm", "달서구": "05_dalseo.xlsm" }
delete_files = { "예천군": "01_yecheon_delete.xlsm", "구미시": "02_gumi_delete.xlsm", "의성군": "08_uiseong_delete.xlsm" }

st.markdown('<p class="main-service-title">낙동강 상류 조서 조회 서비스</p>', unsafe_allow_html=True)

tab0, tab1, tab2 = st.tabs(["통합 요약 현황", "하천구역 조회", "폐천부지 조회"])

# --- [Tab 0: 통합 요약 현황] ---
with tab0:
    col_l, col_r = st.columns(2)
    if 'summary_mode' not in st.session_state: st.session_state.summary_mode = 'river'
    with col_l:
        if st.button("하천구역 현황"): st.session_state.summary_mode = 'river'
    with col_r:
        if st.button("폐천부지 현황"): st.session_state.summary_mode = 'delete'
    st.write("---")
    
    current_mode = st.session_state.summary_mode
    sum_df = get_summary(river_files if current_mode == 'river' else delete_files, current_mode)
    
    if not sum_df.empty:
        st.markdown(f"**전체 합계 요약 ({'하천구역' if current_mode == 'river' else '폐천부지'})**")
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-card"><div class="metric-label">필지수 합계</div><div class="metric-value">{sum_df["필지수"].sum():,}건</div></div>
                <div class="metric-card"><div class="metric-label">국유지 합계</div><div class="metric-value">{sum_df["국유지(필지)"].sum():,}건</div></div>
                <div class="metric-card"><div class="metric-label">사유지 합계</div><div class="metric-value">{sum_df["사유지(필지)"].sum():,}건</div></div>
                <div class="metric-card"><div class="metric-label">편입면적 합계</div><div class="metric-value metric-value-red">{sum_df["편입면적 합계(㎡)"].sum():,.0f}㎡</div></div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("**지역별 상세 요약**")
        st.dataframe(sum_df.style.format({"필지수": "{:,}", "국유지(필지)": "{:,}", "사유지(필지)": "{:,}", "지적면적 합계(㎡)": "{:,.0f}", "편입면적 합계(㎡)": "{:,.0f}"}), use_container_width=True, hide_index=True)
    else: st.info("데이터를 업로드해주세요.")

# --- [Tab 1: 하천구역 조회] ---
with tab1:
    with st.popover("지역 및 지번 검색"):
        sel_reg = st.selectbox("대상 지역", options=list(river_files.keys()), key="r_reg")
        df = load_file(river_files[sel_reg], "river")
        if df is not None:
            dong = st.selectbox("동/리", options=["전체"] + sorted(df['동리'].dropna().unique().tolist()), key="r_dong")
            jb = st.text_input("지번 입력", key="r_jb")
    if df is not None:
        res = df.copy()
        if dong != "전체": res = res[res['동리'] == dong]
        if jb: res = res[res['번지'].astype(str).str.contains(jb)]
        st.markdown(f"**조회된 필지: {len(res):,}건**")
        for _, row in res.head(30).iterrows():
            owner = str(row['주소']).strip() if str(row['성명']).strip() == '국' else str(row['성명']).strip()
            c_type = "national-card" if owner.startswith('국') else "private-card"
            st.markdown(f"""
                <div class="property-card {c_type}">
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <span class="address-text">📍 {row['시군']} {row['동리']} {row['번지']}</span>
                        <span class="owner-badge">{owner}</span>
                    </div>
                    <div class="info-container">
                        <div><span style="font-size:0.75rem; color:#64748b;">지적면적</span><br/><b>{row['지적']:,}㎡</b></div>
                        <div style="text-align:right;"><span style="font-size:0.75rem; color:#dc2626;">편입면적</span><br/><b style="color:#dc2626;">{row['편입']:,}㎡</b></div>
                    </div>
                    <div class="btn-grid">
                        <a href="https://map.naver.com/v5/search/{row['시군']} {row['동리']} {row['번지']}" target="_blank" class="map-btn">지도확인(NAVER)</a>
                        <a href="https://www.eum.go.kr/web/am/amMain.jsp?searchType=address&query={row['시군']} {row['동리']} {row['번지']}" target="_blank" class="eum-btn">토지이용확인(이음)</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- [Tab 2: 폐천부지 조회] ---
with tab2:
    st.markdown('<div class="filter-box">', unsafe_allow_html=True)
    st.write("**관리계획 필터**")
    f_col1, f_col2 = st.columns(2)
    with f_col1: check_bojeon = st.checkbox("보전", value=True)
    with f_col2: check_cheobun = st.checkbox("처분", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.popover("지역 및 지번 상세 검색"):
        sel_reg_d = st.selectbox("대상 지역 ", options=list(delete_files.keys()), key="d_reg")
        df_d = load_file(delete_files[sel_reg_d], "delete")
        if df_d is not None:
            dong_d = st.selectbox("동/리 ", options=["전체"] + sorted(df_d['동리'].dropna().unique().tolist()), key="d_dong")
            jb_d = st.text_input("지번 입력 ", key="d_jb")
    
    if df_d is not None:
        res_d = df_d.copy()
        status_list = []
        if check_bojeon: status_list.append("보전")
        if check_cheobun: status_list.append("처분")
        res_d = res_d[res_d['계획'].apply(lambda x: any(s in str(x) for s in status_list))]
        
        if dong_d != "전체": res_d = res_d[res_d['동리'] == dong_d]
        if jb_d: res_d = res_d[res_d['번지'].astype(str).str.contains(jb_d)]
        
        st.markdown(f"**조회된 필지: {len(res_d):,}건**")
        for _, row in res_d.head(30).iterrows():
            owner = str(row['주소']).strip() if str(row['성명']).strip() == '국' else str(row['성명']).strip()
            plan_val = str(row['계획']).strip()
            card_cls = "abandoned-card-보전" if "보전" in plan_val else "abandoned-card-처분" if "처분" in plan_val else "abandoned-card-default"
            st.markdown(f"""
                <div class="property-card {card_cls}">
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <span class="address-text">📍 {row['시군']} {row['동리']} {row['번지']} <span style="font-size:0.75rem; font-weight:800; border-bottom:2px solid currentColor;">({plan_val})</span></span>
                        <span class="owner-badge">{owner}</span>
                    </div>
                    <div class="info-container">
                        <div><span style="font-size:0.75rem; color:#64748b;">지적면적</span><br/><b>{row['지적']:,}㎡</b></div>
                        <div style="text-align:right;"><span style="font-size:0.75rem; color:#dc2626;">편입면적</span><br/><b style="color:#dc2626;">{row['편입']:,}㎡</b></div>
                    </div>
                    <div class="btn-grid">
                        <a href="https://map.naver.com/v5/search/{row['시군']} {row['동리']} {row['번지']}" target="_blank" class="map-btn">지도확인(NAVER)</a>
                        <a href="https://www.eum.go.kr/web/am/amMain.jsp?searchType=address&query={row['시군']} {row['동리']} {row['번지']}" target="_blank" class="eum-btn">토지이용확인(이음)</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)