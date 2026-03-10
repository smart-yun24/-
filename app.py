import streamlit as st
import pandas as pd
import os

# 1. 페이지 테마 설정
st.set_page_config(page_title="하천구역 통합 관리 시스템", layout="wide", initial_sidebar_state="expanded")

# 커스텀 CSS: 헤더, 라벨, 메트릭 숫자를 모두 동일한 작은 크기로 고정
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    /* 제목 및 모든 헤더 크기 통일 */
    h1, h2, h3, p, label { 
        font-size: 1.05rem !important; 
        color: #1e40af !important; 
        font-weight: 700 !important;
        margin-bottom: 5px !important;
    }
    
    /* 요약 지표(Metric) 라벨 크기 줄이기 */
    [data-testid="stMetricLabel"] > div {
        font-size: 0.95rem !important;
        color: #64748b !important;
    }
    
    /* 요약 지표(Metric) 숫자 크기 줄이기 */
    [data-testid="stMetricValue"] > div {
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        color: #1e293b !important;
    }

    /* 메트릭 박스 테두리 및 간격 조정 */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 8px 15px !important;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }

    .stDataFrame { border: 1px solid #e2e8f0; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 메인 제목
st.markdown("### 🌊 하천구역 통합 관리 시스템")

# 2. 지자체 파일 매핑
region_files = {
    "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "고령군": "03_goryeong.xlsm",
    "달성군": "04_dalseong.xlsm", "달서구": "05_dalseo.xlsm", "문경시": "06_mungyeong.xlsm",
    "안동시": "07_andong.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm",
    "상주시": "10_sangju.xlsm", "성주군": "11_seongju.xlsm"
}

# 3. 사이드바 구성
with st.sidebar:
    st.markdown("### ⚙️ 시스템 설정")
    selected_region = st.selectbox("🎯 지자체 선택", options=list(region_files.keys()))
    file_path = region_files[selected_region]
    
    st.divider()
    
    st.markdown("### 📊 표시 항목")
    all_columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
    default_active = ['동리', '번지', '지목', '지적_m2', '편입면적_m2']
    
    selected_cols = []
    c_a, c_b = st.columns(2)
    for i, col_name in enumerate(all_columns):
        target_c = c_a if i % 2 == 0 else c_b
        if target_c.checkbox(col_name, value=(col_name in default_active)):
            selected_cols.append(col_name)

# 4. 데이터 로드 및 본문 구성
if os.path.exists(file_path):
    try:
        # 엑셀 로드
        df = pd.read_excel(file_path, sheet_name=0, header=1)
        df.columns = all_columns 
        
        # 검색 영역
        st.markdown("### 🔍 필지 검색")
        sc1, sc2 = st.columns(2)
        with sc1:
            dong_list = sorted(df['동리'].dropna().unique())
            target_dong = st.selectbox("동/리", options=["전체 지역"] + list(dong_list))
        with sc2:
            search_jibun = st.text_input("지번 (예: 1080-2)")

        # 필터링
        filtered_df = df.copy()
        if target_dong != "전체 지역":
            filtered_df = filtered_df[filtered_df['동리'] == target_dong]
        if search_jibun:
            filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

        # 순번 1번부터 시작
        filtered_df.index = range(1, len(filtered_df) + 1)

        # 요약 지표 (폰트 사이즈 대폭 하향 조정)
        m1, m2, m3 = st.columns(3)
        m1.metric("조회 필지수", f"{len(filtered_df):,} 건")
        m2.metric("현재 지역", selected_region)
        if '편입면적_m2' in filtered_df.columns:
            total_sum = pd.to_numeric(filtered_df['편입면적_m2'], errors='coerce').sum()
            m3.metric("총 편입면적", f"{total_sum:,.1f} ㎡")

        # 데이터 테이블
        st.markdown(f"### 📋 {selected_region} 조서 데이터")
        if selected_cols:
            st.dataframe(filtered_df[selected_cols], use_container_width=True, height=450)
        else:
            st.warning("항목을 체크해 주세요.")

        # 지도 위치 확인
        st.markdown("### 📍 위치 확인")
        if not filtered_df.empty:
            btn_cols = st.columns(6) # 더 촘촘하게 배치
            for i, (_, row) in enumerate(filtered_df.head(12).iterrows()):
                with btn_cols[i % 6]:
                    addr = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
                    map_url = f"https://map.naver.com/v5/search/{addr}"
                    st.link_button(f"🚩 {row['번지']}", map_url, use_container_width=True)
                    
    except Exception as e:
        st.error(f"오류: {e}")
else:
    st.error(f"파일 없음: {file_path}")