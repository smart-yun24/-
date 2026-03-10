import streamlit as st
import pandas as pd
import os

# 1. 페이지 테마 설정 (Naver 문구 제거 및 블루 톤 복구)
st.set_page_config(page_title="하천구역 통합 조회 시스템", layout="wide", initial_sidebar_state="expanded")

# 커스텀 CSS: 신뢰감을 주는 블루&화이트 스타일
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    h1 { color: #1e40af; font-weight: 800; border-bottom: 3px solid #1e40af; padding-bottom: 10px; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .sidebar .sidebar-content { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌊 하천구역 통합 관리 시스템")
st.info("💡 왼쪽 설정창에서 지역과 표시할 항목을 선택해 주세요.")

# 2. 지자체 파일 매핑
region_files = {
    "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "고령군": "03_goryeong.xlsm",
    "달성군": "04_dalseong.xlsm", "달서구": "05_dalseo.xlsm", "문경시": "06_mungyeong.xlsm",
    "안동시": "07_andong.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm",
    "상주시": "10_sangju.xlsm", "성주군": "11_seongju.xlsm"
}

# 3. 사이드바 구성
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    selected_region = st.selectbox("🎯 대상 지자체 선택", options=list(region_files.keys()))
    file_path = region_files[selected_region]
    
    st.divider()
    
    # 표시 항목 설정 (10개 항목으로 수정하여 에러 해결)
    st.subheader("📊 표시 항목 선택")
    all_columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
    default_active = ['동리', '번지', '지목', '지적_m2', '편입면적_m2']
    
    selected_cols = []
    # 2열 체크박스 배치
    c_a, c_b = st.columns(2)
    for i, col_name in enumerate(all_columns):
        target_c = c_a if i % 2 == 0 else c_b
        if target_c.checkbox(col_name, value=(col_name in default_active)):
            selected_cols.append(col_name)

# 4. 데이터 로드 및 본문 구성
if os.path.exists(file_path):
    try:
        # 엑셀 로드 (2행부터 데이터 인식)
        df = pd.read_excel(file_path, sheet_name=0, header=1)
        
        # [핵심] 10개 항목 이름 강제 매핑 (에러 해결 포인트)
        df.columns = all_columns
        
        # 상세 검색 영역
        st.subheader("🔍 필지 상세 검색")
        sc1, sc2 = st.columns(2)
        with sc1:
            dong_list = sorted(df['동리'].dropna().unique())
            target_dong = st.selectbox("동/리 선택", options=["전체 지역"] + list(dong_list))
        with sc2:
            search_jibun = st.text_input("지번 입력 (예: 1080-2)")

        # 필터링
        filtered_df = df.copy()
        if target_dong != "전체 지역":
            filtered_df = filtered_df[filtered_df['동리'] == target_dong]
        if search_jibun:
            filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

        # 순번 1번부터 시작하도록 수정
        filtered_df.index = range(1, len(filtered_df) + 1)

        # 요약 지표
        m1, m2, m3 = st.columns(3)
        m1.metric("조회 필지수", f"{len(filtered_df):,} 건")
        m2.metric("현재 지역", selected_region)
        if '편입면적_m2' in filtered_df.columns:
            total_sum = pd.to_numeric(filtered_df['편입면적_m2'], errors='coerce').sum()
            m3.metric("총 편입면적 합계", f"{total_sum:,.2f} ㎡")

        # 데이터 테이블 출력
        st.subheader(f"📋 {selected_region} 하천구역 조서")
        if selected_cols:
            st.dataframe(filtered_df[selected_cols], use_container_width=True, height=500)
        else:
            st.warning("표시할 항목을 왼쪽에서 체크해 주세요.")

        # 지도 위치 확인 (버튼형)
        st.divider()
        st.subheader("📍 필지 위치 확인")
        if not filtered_df.empty:
            btn_cols = st.columns(4)
            for i, (_, row) in enumerate(filtered_df.head(12).iterrows()):
                with btn_cols[i % 4]:
                    addr = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
                    map_url = f"https://map.naver.com/v5/search/{addr}"
                    st.link_button(f"🚩 {row['동리']} {row['번지']}", map_url, use_container_width=True)
                    
    except Exception as e:
        st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
else:
    st.error(f"파일을 찾을 수 없습니다: {file_path}")