import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="낙동강 상류 조서 조회 서비스", layout="wide", initial_sidebar_state="collapsed")

# 2. UI/UX 디자인 (이모지 제거, 배경색 전면 적용, 필터 외부 노출 스타일)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    html, body { font-size: 0.98rem; }
    .main-service-title { font-size: 1.0rem !important; font-weight: 800; color: #1e3a8a; text-align: center; margin-bottom: 20px; }
    
    /* 요약 현황 전환 버튼 */
    .stButton > button { width: 100%; border-radius: 8px; font-weight: 700; height: 42px; border: 1px solid #d1d5db; background-color: white; color: #374151; }
    .stButton > button:hover { border-color: #2563eb; color: #2563eb; }

    /* 조서 카드 디자인 */
    .property-card { padding: 18px; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 18px; border: 1px solid #e2e8f0; }
    .national-card { background-color: #f0f7ff; border-left: 6px solid #3b82f6; }
    .private-card { background-color: #ffffff; border-left: 6px solid #e2e8f0; }
    
    .abandoned-card-보전 { background-color: #eff6ff !important; border-left: 6px solid #3b82f6; border: 1px solid #bfdbfe; }
    .abandoned-card-처분 { background-color: #fff7ed !important; border-left: 6px solid #f59e0b; border: 1px solid #fed7aa; }
    .abandoned-card-default { background-color: #ffffff; border-left: 6px solid #e2e8f0; }

    .address-text { font-size: 1.05rem; font-weight: 800; color: #0f172a; line-height: 1.4; }
    .owner-badge { font-size: 0.82rem; font-weight: 700; color: #2563eb; background-color: #ffffff; padding: 3px 10px; border-radius: 8px; border: 1px solid #dbeafe; }
    .info-container { display: flex; justify-content: space-between; background: rgba(255, 255, 255, 0.4); padding: 12px; border-radius: 10px; }
    
    div[data-testid="stPopover"] > button { width: 100%; height: 45px !important; font-size: 0.85rem !important; font-weight: 800 !important; background-color: #2563eb !important; color: white !important; border-radius: 10px !important; }
    .map-btn { display: block; text-align: center; background-color: #03c75a !important; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none !important; font-weight: 800; font-size: 0.95rem; margin-top: 15px; }
    
    .filter-box { background-color: #ffffff; padding: 10px 15px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 15px; }
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
                total_count = len(df_clean)
                data_list.append({
                    "지역명": region, "필지수": total_count, "국유지(필지)": nat_count, "사유지(필지)": total_count - nat_count,
                    "지적면적(㎡)": df_clean['지적'].sum(), "편입면적(㎡)": df_clean['편입'].sum()
                })
            except: pass
    
    summary_df = pd.DataFrame(data_list)
    
    # [요청 반영] 합계 행 추가 (표 하단에 자동 계산)
    if not summary_df.empty:
        total_row = pd.DataFrame([{
            "지역명": "전체 합계",
            "필지수": summary_df["필지수"].sum(),
            "국유지(필지)": summary_df["국유지(필지)"].sum(),
            "사유지(필지)": summary_df["사유지(필지)"].sum(),
            "지적면적(㎡)": summary_df["지적면적(㎡)"].sum(),
            "편입면적(㎡)": summary_df["편입면적(㎡)"].sum()
        }])
        summary_df = pd.concat([summary_df, total_row], ignore_index=True)
        
    return summary_df

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

# 파일 리스트
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
    
    if st.session_state.summary_mode == 'river':
        st.markdown("**하천구역 지역별 요약 및 전체 합계**")
        r_sum = get_summary(river_files, "river")
        if not r_sum.empty:
            # 합계 행 강조 스타일 적용
            st.dataframe(r_sum.style.format({"필지수": "{:,}", "국유지(필지)": "{:,}", "사유지(필지)": "{:,}", "지적면적(㎡)": "{:,.0f}", "편입면적(㎡)": "{:,.0f}"}), use_container_width=True, hide_index=True)
        else: st.info("데이터를 업로드해주세요.")
    else:
        st.markdown("**폐천부지 지역별 요약 및 전체 합계**")
        d_sum = get_summary(delete_files, "delete")
        if not d_sum.empty:
            st.dataframe(d_sum.style.format({"필지수": "{:,}", "국유지(필지)": "{:,}", "사유지(필지)": "{:,}", "지적면적(㎡)": "{:,.0f}", "편입면적(㎡)": "{:,.0f}"}), use_container_width=True, hide_index=True)
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
            st.markdown(f"""<div class="property-card {c_type}"><div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span class="address-text">📍 {row['시군']} {row['동리']} {row['번지']}</span><span class="owner-badge">{owner}</span></div><div class="info-container"><div><span style="font-size:0.7rem;">지적면적</span><br/><b>{row['지적']:,}㎡</b></div><div style="text-align:right;"><span style="font-size:0.7rem; color:red;">편입면적</span><br/><b>{row['편입']:,}㎡</b></div></div><a href="https://map.naver.com/v5/search/{row['시군']} {row['동리']} {row['번지']}" target="_blank" class="map-btn">지도확인(NAVER)</a></div>""", unsafe_allow_html=True)

# --- [Tab 2: 폐천부지 조회] ---
with tab2:
    st.markdown('<div class="filter-box">', unsafe_allow_html=True)
    f_col1, f_col2 = st.columns(2)
    # [요청 반영] 문구 수정: 보전데이터 포함 -> 보전 / 처분 데이터 포함 -> 처분
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
            st.markdown(f"""<div class="property-card {card_cls}"><div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span class="address-text">📍 {row['시군']} {row['동리']} {row['번지']} <span style="font-size:0.75rem; font-weight:800; border-bottom:2px solid currentColor;">({plan_val})</span></span><span class="owner-badge">{owner}</span></div><div class="info-container"><div><span style="font-size:0.7rem;">지적면적</span><br/><b>{row['지적']:,}㎡</b></div><div style="text-align:right;"><span style="font-size:0.7rem; color:red;">편입면적</span><br/><b>{row['편입']:,}㎡</b></div></div><a href="https://map.naver.com/v5/search/{row['시군']} {row['동리']} {row['번지']}" target="_blank" class="map-btn">지도확인(NAVER)</a></div>""", unsafe_allow_html=True)