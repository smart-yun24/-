import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="낙동강 상류 조서 조회 서비스", layout="wide", initial_sidebar_state="collapsed")

# 2. UI/UX 디자인 (이모지 제거, 배경색 전면 적용, 버튼 토글 스타일)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    html, body { font-size: 0.98rem; }
    .main-service-title { font-size: 1.0rem !important; font-weight: 800; color: #1e3a8a; text-align: center; margin-bottom: 20px; }
    
    /* 요약 현황 버튼 스타일 */
    .stButton > button { width: 100%; border-radius: 8px; font-weight: 700; height: 40px; }

    /* 조서 카드 디자인 */
    .property-card { padding: 18px; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 18px; border: 1px solid #e2e8f0; }
    
    /* 하천구역 카드 */
    .national-card { background-color: #f0f7ff; border-left: 6px solid #3b82f6; }
    .private-card { background-color: #ffffff; border-left: 6px solid #e2e8f0; }
    
    /* 폐천부지 카드 배경색 전체 적용 (보전=블루, 처분=오렌지) */
    .abandoned-card-보전 { background-color: #eff6ff !important; border-left: 6px solid #3b82f6; border: 1px solid #bfdbfe; }
    .abandoned-card-처분 { background-color: #fff7ed !important; border-left: 6px solid #f59e0b; border: 1px solid #fed7aa; }
    .abandoned-card-default { background-color: #ffffff; border-left: 6px solid #e2e8f0; }

    .address-text { font-size: 1.05rem; font-weight: 800; color: #0f172a; line-height: 1.4; }
    .owner-badge { font-size: 0.82rem; font-weight: 700; color: #2563eb; background-color: #ffffff; padding: 3px 10px; border-radius: 8px; border: 1px solid #dbeafe; }
    .info-container { display: flex; justify-content: space-between; background: rgba(255, 255, 255, 0.4); padding: 12px; border-radius: 10px; }
    
    /* 검색 팝오버 및 지도 버튼 */
    div[data-testid="stPopover"] > button { width: 100%; height: 42px !important; font-size: 0.85rem !important; font-weight: 800 !important; background-color: #2563eb !important; color: white !important; border-radius: 10px !important; }
    .map-btn { display: block; text-align: center; background-color: #03c75a; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none !important; font-weight: 800; font-size: 0.95rem; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# 데이터 로딩 함수 (캐싱 적용)
@st.cache_data
def get_summary(file_map, mode="river"):
    data_list = []
    for region, path in file_map.items():
        if os.path.exists(path):
            try:
                df = pd.read_excel(path, sheet_name=0, header=1)
                cols = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적', '편입']
                df_clean = df.iloc[:, :len(cols)].copy()
                df_clean.columns = cols
                df_clean['지적'] = pd.to_numeric(df_clean['지적'], errors='coerce').fillna(0)
                df_clean['편입'] = pd.to_numeric(df_clean['편입'], errors='coerce').fillna(0)
                owner_idx = 9 if mode == "river" else 10
                nat_count = df[df.columns[owner_idx]].astype(str).str.strip().str.startswith('국').sum()
                data_list.append({
                    "지역": region, "필지수": len(df_clean), "국유지": nat_count, "사유지": len(df_clean)-nat_count,
                    "지적합계": df_clean['지적'].sum(), "편입합계": df_clean['편입'].sum()
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
river_files = { "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm", "성주군": "11_seongju.xlsm", "고령군": "03_goryeong.xlsm", "달성군": "04_dalseong.xlsm", "문경시": "06_mungyeong.xlsm", "안동시": "07_andong.xlsm" }
delete_files = { "예천군": "01_yecheon_delete.xlsm", "구미시": "02_gumi_delete.xlsm", "의성군": "08_uiseong_delete.xlsm" }

st.markdown('<p class="main-service-title">낙동강 상류 조서 조회 서비스</p>', unsafe_allow_html=True)

tab0, tab1, tab2 = st.tabs(["통합 요약 현황", "하천구역 조회", "폐천부지 조회"])

# --- [Tab 0: 통합 요약 현황 (버튼식 전환)] ---
with tab0:
    col_l, col_r = st.columns(2)
    if 'summary_mode' not in st.session_state:
        st.session_state.summary_mode = 'river'
    
    with col_l:
        if st.button("하천구역 현황"):
            st.session_state.summary_mode = 'river'
    with col_r:
        if st.button("폐천부지 현황"):
            st.session_state.summary_mode = 'delete'
    
    st.write("---")
    
    if st.session_state.summary_mode == 'river':
        st.markdown("**하천구역 현황 요약**")
        r_sum = get_summary(river_files, "river")
        if not r_sum.empty:
            st.dataframe(r_sum.style.format({"필지수": "{:,}", "국유지": "{:,}", "사유지": "{:,}", "지적합계": "{:,.0f}", "편입합계": "{:,.0f}"}), use_container_width=True, hide_index=True)
        else: st.info("데이터를 업로드해주세요.")
    else:
        st.markdown("**폐천부지 현황 요약**")
        d_sum = get_summary(delete_files, "delete")
        if not d_sum.empty:
            st.dataframe(d_sum.style.format({"필지수": "{:,}", "국유지": "{:,}", "사유지": "{:,}", "지적합계": "{:,.0f}", "편입합계": "{:,.0f}"}), use_container_width=True, hide_index=True)
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
        for _, row in res.head(30).iterrows():
            owner = str(row['주소']).strip() if str(row['성명']).strip() == '국' else str(row['성명']).strip()
            c_type = "national-card" if owner.startswith('국') else "private-card"
            st.markdown(f"""<div class="property-card {c_type}"><div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span class="address-text">📍 {row['시군']} {row['동리']} {row['번지']}</span><span class="owner-badge">{owner}</span></div><div class="info-container"><div><span style="font-size:0.7rem;">지적</span><br/><b>{row['지적']:,}㎡</b></div><div style="text-align:right;"><span style="font-size:0.7rem; color:red;">편입</span><br/><b>{row['편입']:,}㎡</b></div></div><a href="https://map.naver.com/v5/search/{row['시군']} {row['동리']} {row['번지']}" target="_blank" class="map-btn">지도확인(NAVER)</a></div>""", unsafe_allow_html=True)

# --- [Tab 2: 폐천부지 조회] ---
with tab2:
    with st.popover("폐천부지 검색"):
        sel_reg_d = st.selectbox("대상 지역 ", options=list(delete_files.keys()), key="d_reg")
        df_d = load_file(delete_files[sel_reg_d], "delete")
        if df_d is not None:
            # 보전/처분 필터링 박스 추가
            plan_filter = st.selectbox("관리계획 선택", options=["전체", "보전", "처분"], key="d_plan_filter")
            dong_d = st.selectbox("동/리 ", options=["전체"] + sorted(df_d['동리'].dropna().unique().tolist()), key="d_dong")
            jb_d = st.text_input("지번 입력 ", key="d_jb")
    
    if df_d is not None:
        res_d = df_d.copy()
        # 관리계획 필터링 적용
        if plan_filter != "전체":
            res_d = res_d[res_d['계획'].str.contains(plan_filter, na=False)]
        if dong_d != "전체": res_d = res_d[res_d['동리'] == dong_d]
        if jb_d: res_d = res_d[res_d['번지'].astype(str).str.contains(jb_d)]
        
        st.markdown(f"**조회된 필지: {len(res_d):,}건**")
        for _, row in res_d.head(30).iterrows():
            owner = str(row['주소']).strip() if str(row['성명']).strip() == '국' else str(row['성명']).strip()
            plan_val = str(row['계획']).strip()
            card_cls = "abandoned-card-보전" if "보전" in plan_val else "abandoned-card-처분" if "처분" in plan_val else "abandoned-card-default"
            st.markdown(f"""<div class="property-card {card_cls}"><div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span class="address-text">📍 {row['시군']} {row['동리']} {row['번지']} <span style="font-size:0.75rem; font-weight:800; border-bottom:2px solid currentColor;">({plan_val})</span></span><span class="owner-badge">{owner}</span></div><div class="info-container"><div><span style="font-size:0.7rem;">지적</span><br/><b>{row['지적']:,}㎡</b></div><div style="text-align:right;"><span style="font-size:0.7rem; color:red;">편입</span><br/><b>{row['편입']:,}㎡</b></div></div><a href="https://map.naver.com/v5/search/{row['시군']} {row['동리']} {row['번지']}" target="_blank" class="map-btn">지도확인(NAVER)</a></div>""", unsafe_allow_html=True)