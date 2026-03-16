import streamlit as st
import pandas as pd
import os
import urllib.parse

# 1. 페이지 설정 (브라우저 탭 이름 및 레이아웃)
st.set_page_config(page_title="낙동강 상류 조서 조회 서비스", layout="wide", initial_sidebar_state="collapsed")

# 2. 유신 시그니처 테마 (Professional Deep Ocean & Glassmorphism)
st.markdown("""
    <style>
    /* 전체 배경: 눈이 편안한 Off-white */
    .stApp { background-color: #f8fafc; }
    html, body { font-size: 0.98rem; font-family: 'Pretendard', sans-serif; }
    
    /* 타이틀 스타일 (1.0rem, Deep Navy, No Emoji) */
    .main-service-title { 
        font-size: 1.0rem !important; font-weight: 800; color: #1e3a8a; 
        text-align: center; margin-bottom: 25px; letter-spacing: -0.02em;
    }
    
    /* 현황 전환 버튼 스타일 */
    .stButton > button { 
        width: 100%; border-radius: 10px; font-weight: 700; height: 45px; 
        border: 1px solid #e2e8f0; background-color: white; color: #475569;
    }
    .stButton > button:hover { border-color: #1e3a8a; color: #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }

    /* 전체 합계 메트릭 대시보드 */
    .metric-container { display: flex; gap: 12px; margin-bottom: 25px; flex-wrap: wrap; }
    .metric-card {
        flex: 1; min-width: 170px; background-color: white; padding: 20px; border-radius: 14px;
        border: 1px solid #f1f5f9; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); text-align: center;
    }
    .metric-label { font-size: 0.75rem; color: #64748b; margin-bottom: 8px; font-weight: 600; }
    .metric-value { font-size: 1.15rem; font-weight: 800; color: #1e3a8a; }
    .metric-value-red { color: #dc2626; }

    /* 조서 카드 디자인 */
    .property-card { 
        padding: 20px; border-radius: 16px; margin-bottom: 20px; 
        border: 1px solid #f1f5f9; background-color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .national-card { border-left: 6px solid #1e3a8a; }
    .private-card { border-left: 6px solid #94a3b8; }
    
    /* 폐천부지 관리계획별 배경색 */
    .abandoned-card-보전 { background-color: #f0f7ff !important; border-left: 6px solid #2563eb; border: 1px solid #dbeafe; }
    .abandoned-card-처분 { background-color: #fff7ed !important; border-left: 6px solid #ea580c; border: 1px solid #ffedd5; }

    .address-text { font-size: 1.05rem; font-weight: 800; color: #0f172a; line-height: 1.5; }
    .owner-badge { font-size: 0.8rem; font-weight: 700; color: #1e3a8a; background-color: #eff6ff; padding: 4px 12px; border-radius: 8px; border: 1px solid #dbeafe; }
    
    .info-container { display: flex; justify-content: space-between; background: rgba(255, 255, 255, 0.6); padding: 14px; border-radius: 12px; margin-top: 10px; }
    
    /* 네이버 지도 버튼 (Full Width) */
    .map-btn { 
        display: block; text-align: center; background-color: #03c75a !important; color: white !important; 
        padding: 14px; border-radius: 12px; text-decoration: none !important; 
        font-weight: 800; font-size: 0.95rem; margin-top: 18px; 
        box-shadow: 0 4px 6px rgba(3, 199, 90, 0.2);
    }
    
    /* 필터 박스 */
    .filter-box { background-color: white; padding: 15px 20px; border-radius: 14px; border: 1px solid #e2e8f0; margin-bottom: 20px; }
    div[data-testid="stPopover"] > button { width: 100%; height: 45px !important; font-size: 0.85rem !important; font-weight: 800 !important; background-color: #2563eb !important; color: white !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# [데이터 로직: 요약 및 로드]
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
                    "지적면적(㎡)": df_clean['지적'].sum(), "편입면적(㎡)": df_clean['편입'].sum()
                })
            except: pass
    return pd.DataFrame(data_list)

# 단일 데이터프레임을 그룹화하여 요약하는 함수 (폐천부지 및 홍수관리구역용)
@st.cache_data
def get_single_file_summary(df):
    if df is None or df.empty: return pd.DataFrame()
    data_list = []
    # '시군' 컬럼을 기준으로 그룹화하여 통계 생성
    for region, group in df.groupby('시군'):
        nat_count = group['성명'].astype(str).str.strip().str.startswith('국').sum()
        data_list.append({
            "지역명": region, "필지수": len(group), "국유지(필지)": nat_count, "사유지(필지)": len(group)-nat_count,
            "지적면적(㎡)": group['지적'].sum(), "편입면적(㎡)": group['편입'].sum()
        })
    return pd.DataFrame(data_list)

@st.cache_data
def load_file(path, mode="river"):
    if not os.path.exists(path): return None
    try:
        df_raw = pd.read_excel(path, sheet_name=0, header=1)
        # 컬럼 구조 정의 (시군, 읍면, 동리, 번지 포함)
        cols = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적', '편입']
        if mode == "delete":
            df = df_raw.iloc[:, :11].copy()
            df.columns = cols + ['계획', '주소', '성명']
        else: # river, flood
            df = df_raw.iloc[:, :10].copy()
            df.columns = cols + ['주소', '성명']
        
        # 숫자형 데이터 전처리
        df['지적'] = pd.to_numeric(df['지적'], errors='coerce').fillna(0)
        df['편입'] = pd.to_numeric(df['편입'], errors='coerce').fillna(0)
        return df
    except: return None

# 파일 리스트 및 상수 매핑
river_files = { "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm", "성주군": "11_seongju.xlsm", "고령군": "03_goryeong.xlsm", "달성군": "04_dalseong.xlsm", "문경시": "06_mungyeong.xlsm", "안동시": "07_andong.xlsm", "상주시": "10_sangju.xlsm", "달서구": "05_dalseo.xlsm" }

DELETE_ALL_FILE = "01_all_delete.xlsm"
FLOOD_ALL_FILE = "01_all_flood.xlsm"

st.markdown('<p class="main-service-title">낙동강 상류 조서 조회 서비스</p>', unsafe_allow_html=True)
tab0, tab1, tab2, tab3 = st.tabs(["통합 요약 현황", "하천구역 조회", "폐천부지 조회", "홍수관리구역 조회"])

# --- [Tab 0: 통합 요약 현황] ---
with tab0:
    col_1, col_2, col_3 = st.columns(3)
    if 'summary_mode' not in st.session_state: st.session_state.summary_mode = 'river'
    
    with col_1:
        if st.button("하천구역 현황"): st.session_state.summary_mode = 'river'
    with col_2:
        if st.button("폐천부지 현황"): st.session_state.summary_mode = 'delete'
    with col_3:
        if st.button("홍수관리구역 현황"): st.session_state.summary_mode = 'flood'
        
    st.write("---")
    
    current_mode = st.session_state.summary_mode
    mode_name = "하천구역" if current_mode == 'river' else ("폐천부지" if current_mode == 'delete' else "홍수관리구역")
    
    # 모드에 따라 다르게 요약 데이터 생성
    if current_mode == 'river':
        sum_df = get_summary(river_files, "river")
    elif current_mode == 'delete':
        df_all_delete = load_file(DELETE_ALL_FILE, "delete")
        sum_df = get_single_file_summary(df_all_delete)
    else: # flood
        df_all_flood = load_file(FLOOD_ALL_FILE, "flood")
        sum_df = get_single_file_summary(df_all_flood)
    
    if not sum_df.empty:
        st.markdown(f"**전체 합계 요약 ({mode_name})**")
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-card"><div class="metric-label">필지수 합계</div><div class="metric-value">{sum_df["필지수"].sum():,}건</div></div>
                <div class="metric-card"><div class="metric-label">국유지 합계</div><div class="metric-value">{sum_df["국유지(필지)"].sum():,}건</div></div>
                <div class="metric-card"><div class="metric-label">사유지 합계</div><div class="metric-value">{sum_df["사유지(필지)"].sum():,}건</div></div>
                <div class="metric-card"><div class="metric-label">편입면적 합계</div><div class="metric-value metric-value-red">{sum_df["편입면적(㎡)"].sum():,.0f}㎡</div></div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("**지역별 상세 현황표**")
        st.dataframe(sum_df.style.format({"필지수": "{:,}", "국유지(필지)": "{:,}", "사유지(필지)": "{:,}", "지적면적(㎡)": "{:,.0f}", "편입면적(㎡)": "{:,.0f}"}), use_container_width=True, hide_index=True)
    else: st.info(f"{mode_name} 데이터 파일이 존재하지 않습니다.")

# --- [카드 출력 공통 함수] ---
def display_cards(res_df, mode="river"):
    for _, row in res_df.head(30).iterrows():
        full_addr = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}".replace('nan', '').strip()
        encoded_addr = urllib.parse.quote(full_addr)
        owner = str(row['성명']).strip() if str(row['성명']).strip() != '국' else str(row['주소']).strip()
        
        if mode == "delete":
            p_val = str(row['계획']).strip()
            card_cls = f"abandoned-card-{p_val}" if p_val in ["보전", "처분"] else "property-card"
            plan_label = f'<span style="font-size:0.75rem; font-weight:800; border-bottom:2px solid currentColor;">({p_val})</span>'
        else: # river or flood
            card_cls = "national-card" if str(row['성명']).strip() == '국' else "private-card"
            plan_label = ""

        st.markdown(f"""
            <div class="property-card {card_cls}">
                <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                    <span class="address-text">📍 {full_addr} {plan_label}</span>
                    <span class="owner-badge">{owner}</span>
                </div>
                <div class="info-container">
                    <div><span style="font-size:0.75rem; color:#64748b;">지적면적</span><br/><b>{row['지적']:,}㎡</b></div>
                    <div style="text-align:right;"><span style="font-size:0.75rem; color:#dc2626;">편입면적</span><br/><b style="color:#dc2626;">{row['편입']:,}㎡</b></div>
                </div>
                <a href="https://map.naver.com/v5/search/{encoded_addr}" target="_blank" class="map-btn">지도확인(NAVER)</a>
            </div>
        """, unsafe_allow_html=True)

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
        st.markdown(f"**조회 필지: {len(res):,}건**")
        display_cards(res, "river")

# --- [Tab 2: 폐천부지 조회] ---
with tab2:
    st.markdown('<div class="filter-box">**관리계획 필터**', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: check_bojeon = st.checkbox("보전", value=True)
    with c2: check_cheobun = st.checkbox("처분", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.popover("상세 지역 검색"):
        df_d_all = load_file(DELETE_ALL_FILE, "delete")
        
        if df_d_all is not None and not df_d_all.empty:
            regions = sorted(df_d_all['시군'].dropna().unique().tolist())
            sel_reg_d = st.selectbox("대상 지역 ", options=regions, key="d_reg")
            df_d = df_d_all[df_d_all['시군'] == sel_reg_d]
            dong_d = st.selectbox("동/리 ", options=["전체"] + sorted(df_d['동리'].dropna().unique().tolist()), key="d_dong")
            jb_d = st.text_input("지번 입력 ", key="d_jb")
        else:
            df_d = None
    
    if df_d is not None:
        res_d = df_d.copy()
        
        status_list = []
        if check_bojeon: status_list.append("보전")
        if check_cheobun: status_list.append("처분")
        res_d = res_d[res_d['계획'].apply(lambda x: any(s in str(x) for s in status_list))]
        
        if dong_d != "전체": res_d = res_d[res_d['동리'] == dong_d]
        if jb_d: res_d = res_d[res_d['번지'].astype(str).str.contains(jb_d)]
        
        st.markdown(f"**조회 필지: {len(res_d):,}건**")
        display_cards(res_d, "delete")

# --- [Tab 3: 홍수관리구역 조회 (신규)] ---
with tab3:
    with st.popover("상세 지역 검색"):
        # 단일 파일 로드
        df_f_all = load_file(FLOOD_ALL_FILE, "flood")
        
        if df_f_all is not None and not df_f_all.empty:
            # 엑셀 데이터 안의 '시군' 컬럼을 추출해서 자동으로 셀렉트박스 목록 생성
            regions_f = sorted(df_f_all['시군'].dropna().unique().tolist())
            sel_reg_f = st.selectbox("대상 지역", options=regions_f, key="f_reg")
            
            # 선택된 지역으로 미리 필터링
            df_f = df_f_all[df_f_all['시군'] == sel_reg_f]
            dong_f = st.selectbox("동/리", options=["전체"] + sorted(df_f['동리'].dropna().unique().tolist()), key="f_dong")
            jb_f = st.text_input("지번 입력", key="f_jb")
        else:
            df_f = None
    
    if df_f is not None:
        res_f = df_f.copy()
        
        if dong_f != "전체": res_f = res_f[res_f['동리'] == dong_f]
        if jb_f: res_f = res_f[res_f['번지'].astype(str).str.contains(jb_f)]
        
        st.markdown(f"**조회 필지: {len(res_f):,}건**")
        display_cards(res_f, "flood")