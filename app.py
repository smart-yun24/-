import streamlit as st
import pandas as pd
import os
import urllib.parse  # 주소 인코딩 최적화

# 1. 페이지 설정
st.set_page_config(page_title="낙동강 상류 조서 조회 서비스", layout="wide", initial_sidebar_state="collapsed")

# 2. 유신 시그니처 테마 (Professional Deep Ocean)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    html, body { font-size: 0.98rem; font-family: 'Pretendard', sans-serif; }
    .main-service-title { font-size: 1.0rem !important; font-weight: 800; color: #1e3a8a; text-align: center; margin-bottom: 25px; }
    
    /* 카드 디자인 */
    .property-card { padding: 20px; border-radius: 16px; margin-bottom: 20px; border: 1px solid #f1f5f9; background-color: white; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
    .national-card { border-left: 6px solid #1e3a8a; }
    .private-card { border-left: 6px solid #94a3b8; }
    .abandoned-card-보전 { background-color: #f0f7ff !important; border-left: 6px solid #2563eb; }
    .abandoned-card-처분 { background-color: #fff7ed !important; border-left: 6px solid #ea580c; }

    .address-text { font-size: 1.05rem; font-weight: 800; color: #0f172a; line-height: 1.5; }
    .owner-badge { font-size: 0.8rem; font-weight: 700; color: #1e3a8a; background-color: #eff6ff; padding: 4px 12px; border-radius: 8px; border: 1px solid #dbeafe; }
    
    .info-container { display: flex; justify-content: space-between; background: rgba(255, 255, 255, 0.6); padding: 14px; border-radius: 12px; margin-top: 10px; }
    
    /* 버튼 레이아웃 */
    .btn-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 18px; }
    .map-btn { display: block; text-align: center; background-color: #03c75a !important; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none !important; font-weight: 800; font-size: 0.85rem; }
    .eum-btn { display: block; text-align: center; background-color: #1e3a8a !important; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none !important; font-weight: 800; font-size: 0.85rem; }
    
    div[data-testid="stPopover"] > button { width: 100%; height: 45px !important; font-size: 0.85rem !important; font-weight: 800 !important; background-color: #2563eb !important; color: white !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# [데이터 처리 함수]
@st.cache_data
def load_file(path, mode="river"):
    if not os.path.exists(path): return None
    try:
        df_raw = pd.read_excel(path, sheet_name=0, header=1)
        # 읍면 컬럼 누락 방지를 위한 안전한 슬라이싱
        df = df_raw.iloc[:, :11].copy()
        cols = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적', '편입']
        if mode == "river":
            df.columns = cols + ['주소', '성명', 'Extra']
        else:
            df.columns = cols + ['계획', '주소', '성명']
        return df
    except: return None

# 파일 설정
river_files = { "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm", "성주군": "11_seongju.xlsm", "고령군": "03_goryeong.xlsm", "달성군": "04_dalseong.xlsm", "문경시": "06_mungyeong.xlsm", "안동시": "07_andong.xlsm", "상주시": "10_sangju.xlsm" }
delete_files = { "예천군": "01_yecheon_delete.xlsm", "구미시": "02_gumi_delete.xlsm", "의성군": "08_uiseong_delete.xlsm" }

st.markdown('<p class="main-service-title">낙동강 상류 조서 조회 서비스</p>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["하천구역 조회", "폐천부지 조회"])

def display_cards(res_df, mode="river"):
    for _, row in res_df.head(30).iterrows():
        # [주소 생성 최적화] nan 값 제거 및 공백 정리
        addr_parts = [str(row['시군']), str(row['읍면']), str(row['동리']), str(row['번지'])]
        clean_parts = [p.strip() for p in addr_parts if p and p.lower() != 'nan']
        full_addr = " ".join(clean_parts)
        
        # 토지이음용 인코딩 (quote_plus가 더 확실함)
        encoded_addr = urllib.parse.quote_plus(full_addr)
        
        owner = str(row['성명']).strip() if str(row['성명']).strip() != '국' else str(row['주소']).strip()
        card_cls = "national-card" if "국" in str(row['성명']) else "private-card"
        if mode == "delete":
            card_cls = f"abandoned-card-{row['계획']}" if row['계획'] in ["보전", "처분"] else "property-card"

        st.markdown(f"""
            <div class="property-card {card_cls}">
                <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                    <span class="address-text">📍 {full_addr}</span>
                    <span class="owner-badge">{owner}</span>
                </div>
                <div class="info-container">
                    <div><span style="font-size:0.7rem; color:#64748b;">지적면적</span><br/><b>{row['지적']:,}㎡</b></div>
                    <div style="text-align:right;"><span style="font-size:0.7rem; color:#dc2626;">편입면적</span><br/><b style="color:#dc2626;">{row['편입']:,}㎡</b></div>
                </div>
                <div class="btn-grid">
                    <a href="https://map.naver.com/v5/search/{encoded_addr}" target="_blank" class="map-btn">네이버 지도</a>
                    <a href="https://www.eum.go.kr/web/am/amMain.jsp?searchType=address&query={encoded_addr}" target="_blank" class="eum-btn">토지이음(열람)</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

# 탭별 화면 구성 (기존 로직 유지)
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
        display_cards(res, "river")

with tab2:
    st.write("**관리계획 필터**")
    c1, c2 = st.columns(2)
    with c1: check_bojeon = st.checkbox("보전", value=True)
    with c2: check_cheobun = st.checkbox("처분", value=True)
    with st.popover("지역 상세 검색"):
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
        display_cards(res_d, "delete")