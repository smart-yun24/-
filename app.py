import streamlit as st
import pandas as pd
import os

# 1. 페이지 테마 및 스타일 설정
st.set_page_config(page_title="하천구역 통합 조회 시스템", layout="wide", initial_sidebar_state="expanded")

# 커스텀 CSS로 디자인 강화
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    h1 { color: #1e3a8a; font-weight: 800; }
    .sidebar-content { background-color: #ffffff; padding: 20px; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌊 하천구역 편입면적 통합 조회 시스템")
st.info("💡 사이드바에서 지역을 선택하고, 아래 '표시 항목 설정'에서 보고 싶은 정보만 체크하세요.")

# 2. 지자체 매핑 정보
region_files = {
    "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "고령군": "03_goryeong.xlsm",
    "달성군": "04_dalseong.xlsm", "달서구": "05_dalseo.xlsm", "문경시": "06_mungyeong.xlsm",
    "안동시": "07_andong.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm",
    "상주시": "10_sangju.xlsm", "성주군": "11_seongju.xlsm"
}

# 3. 사이드바 구성
with st.sidebar:
    st.header("📍 지역 및 검색")
    selected_region = st.selectbox("🎯 대상 지자체", options=list(region_files.keys()))
    file_path = region_files[selected_region]
    
    st.divider()
    
    # 4. 항목 선택 (체크박스 스타일)
    st.subheader("📊 표시 항목 설정")
    all_columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
    
    selected_cols = []
    # 기본 체크 항목 설정
    default_active = ['동리', '번지', '지목', '지적_m2', '편입면적_m2']
    
    # 클릭하기 편하도록 2열로 배치
    col_a, col_b = st.columns(2)
    for i, col_name in enumerate(all_columns):
        target_col = col_a if i % 2 == 0 else col_b
        if target_col.checkbox(col_name, value=(col_name in default_active)):
            selected_cols.append(col_name)

# 데이터 로드 및 본문 구성
if os.path.exists(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name=0, header=1)
        df.columns = all_columns
        
        # 필지 검색 필터 (사이드바 하단)
        with st.sidebar:
            st.divider()
            st.subheader("🔍 상세 검색")
            dong_list = sorted(df['동리'].dropna().unique())
            target_dong = st.selectbox("동/리 선택", options=["전체"] + list(dong_list))
            search_jibun = st.text_input("지번 입력 (예: 1080-2)")

        # 필터링 로직
        filtered_df = df.copy()
        if target_dong != "전체":
            filtered_df = filtered_df[filtered_df['동리'] == target_dong]
        if search_jibun:
            filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

        # 순번 1번부터 시작하도록 수정
        filtered_df.index = range(1, len(filtered_df) + 1)

        # 요약 정보 상단 배치 (디자인 포인트)
        m1, m2, m3 = st.columns(3)
        m1.metric("총 조회 필지", f"{len(filtered_df):,} 건")
        m2.metric("선택 지역", selected_region)
        if '편입면적_m2' in filtered_df.columns:
            total_area = filtered_df['편입면적_m2'].sum()
            m3.metric("총 편입면적", f"{total_area:,.2f} ㎡")

        # 결과 테이블 출력
        st.subheader(f"📋 {selected_region} 데이터 조서")
        if selected_cols:
            st.dataframe(filtered_df[selected_cols], use_container_width=True, height=500)
        else:
            st.warning("⚠️ 왼쪽 사이드바에서 표시할 항목을 하나 이상 체크해 주세요.")

        # 5. 지도 버튼 (더 이쁘게 정리)
        st.divider()
        st.subheader("📍 주요 필지 위치 (네이버 지도)")
        if not filtered_df.empty:
            btn_cols = st.columns(3)
            for i, (_, row) in enumerate(filtered_df.head(9).iterrows()):
                with btn_cols[i % 3]:
                    full_addr = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
                    map_url = f"https://map.naver.com/v5/search/{full_addr}"
                    st.link_button(f"🔗 {row['동리']} {row['번지']}", map_url, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ 데이터 로드 중 오류가 발생했습니다: {e}")
else:
    st.error(f"📂 '{selected_region}' 파일을 찾을 수 없습니다. (파일명: {file_path})")