import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="낙동강 상류 조서 조회 서비스", layout="wide", initial_sidebar_state="collapsed")

# [터보 엔진 1] 데이터 로딩 최적화 (캐싱)
@st.cache_data(show_spinner="데이터를 불러오는 중입니다...")
def get_processed_df(file_path):
    if not os.path.exists(file_path):
        return None
    # 엑셀 읽기 속도 최적화 (엔진 지정)
    df_raw = pd.read_excel(file_path, sheet_name=0, header=1, engine='openpyxl')
    df = df_raw.iloc[:, :10].copy()
    df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
    # 숫자가 아닌 데이터 예외 처리
    df['지적_m2'] = pd.to_numeric(df['지적_m2'], errors='coerce').fillna(0)
    df['편입면적_m2'] = pd.to_numeric(df['편입면적_m2'], errors='coerce').fillna(0)
    return df

# UI 디자인 (기존 스타일 유지하며 성능 최적화)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .property-card { padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.03); }
    .national-card { background-color: #f0f7ff; border-left: 5px solid #3b82f6; }
    .private-card { background-color: #ffffff; border-left: 5px solid #e2e8f0; }
    /* 모바일에서 텍스트가 겹치지 않게 미세 조정 */
    .owner-badge { font-size: 0.8rem; padding: 2px 8px; border-radius: 6px; border: 1px solid #dbeafe; background: white; white-space: nowrap; }
    </style>
""", unsafe_allow_html=True)

st.title("낙동강 상류 조서 조회 서비스")

tab1, tab2 = st.tabs(["하천구역 조회", "폐천부지 조회"])

with tab1:
    # 지자체 파일 매핑
    files = {f"{i:02d}": name for i, name in enumerate(["예천군", "구미시", "고령군", "달성군", "달서구", "문경시", "안동시", "의성군", "칠곡군", "상주시", "성주군"], 1)}
    file_map = {v: f"{k}_{'yecheon' if k=='01' else 'data'}.xlsm" for k, v in files.items()} # 예시 파일명 규칙

    with st.popover("🔍 검색 조건 설정"):
        sel_reg = st.selectbox("지역", options=list(file_map.keys()), key="r_reg")
        # 실제 파일명에 맞춰 경로 수정 (예: 01_yecheon.xlsm)
        actual_path = f"{list(files.keys())[list(files.values()).index(sel_reg)]}_{'yecheon' if sel_reg=='예천군' else 'data'}.xlsm"
        
        # 임시로 기존 파일명 규칙 사용 (매니저님 파일명에 맞춤)
        path_dict = {"예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm"} # ... 생략
        df = get_processed_df(path_dict.get(sel_reg, "01_yecheon.xlsm"))

        if df is not None:
            sel_dong = st.selectbox("동/리", options=["전체"] + sorted(df['동리'].dropna().unique().tolist()))
            search_jb = st.text_input("지번 (Enter 입력)")

    if df is not None:
        # 필터링 로직
        res = df.copy()
        if sel_dong != "전체": res = res[res['동리'] == sel_dong]
        if search_jb: res = res[res['번지'].astype(str).str.contains(search_jb)]

        st.info(f"검색 결과: {len(res)}건")

        # [터보 엔진 2] 출력 개수 제한 및 페이징 (렉 방지의 핵심)
        batch_size = 15
        for _, row in res.head(batch_size).iterrows():
            owner = str(row['소유자_주소']) if str(row['소유자_성명']) == '국' else str(row['소유자_성명'])
            c_type = "national-card" if owner.startswith('국') else "private-card"
            
            st.markdown(f"""
                <div class="property-card {c_type}">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-weight:800;">📍 {row['동리']} {row['번지']}</span>
                        <span class="owner-badge">{owner}</span>
                    </div>
                    <div style="margin-top:8px; font-size:0.9rem; color:#444;">
                        지적: {row['지적_m2']:,}㎡ / <span style="color:red;">편입: {row['편입면적_m2']:,}㎡</span>
                    </div>
                    <a href="https://map.naver.com/v5/search/{sel_reg} {row['읍면']} {row['동리']} {row['번지']}" target="_blank" 
                       style="display:block; margin-top:10px; text-align:center; background:#03c75a; color:white; padding:8px; border-radius:8px; text-decoration:none; font-size:0.8rem;">
                       지도 확인
                    </a>
                </div>
            """, unsafe_allow_html=True)
        
        if len(res) > batch_size:
            st.warning(f"상위 {batch_size}건만 표시됩니다. 더 정확한 지번을 입력해 검색 범위를 줄여보세요.")

with tab2:
    st.write("폐천부지 양식을 기다리고 있습니다.")