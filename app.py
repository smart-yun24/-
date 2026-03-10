import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="하천구역 통합 조회 시스템", layout="wide")

st.title("🌊 하천구역 편입면적 통합 조회 시스템")
st.markdown("본 시스템은 2026년 최신 하천기본계획 조서 양식을 바탕으로 정보를 제공합니다.")

# 1. 지자체별 파일 매핑
region_files = {
    "예천군": "01_yecheon.xlsm",
    "구미시": "02_gumi.xlsm",
    "고령군": "03_goryeong.xlsm",
    "달성군": "04_dalseong.xlsm",
    "달서구": "05_dalseo.xlsm",
    "문경시": "06_mungyeong.xlsm",
    "안동시": "07_andong.xlsm",
    "의성군": "08_uiseong.xlsm",
    "칠곡군": "09_chilgok.xlsm",
    "상주시": "10_sangju.xlsm",
    "성주군": "11_seongju.xlsm"
}

# 2. 사이드바 - 지역 및 항목 설정
st.sidebar.header("📍 시스템 설정")
selected_region = st.sidebar.selectbox("대상 지자체 선택", options=list(region_files.keys()))

# 전체 항목 리스트 정의
all_columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']

# 보고 싶은 항목 선택 필터 (기본값 설정)
selected_cols = st.sidebar.multiselect(
    "📊 표시할 항목 선택",
    options=all_columns,
    default=['동리', '번지', '지목', '지적_m2', '편입면적_m2']
)

# 파일 경로 설정
file_path = region_files[selected_region]

# 데이터 로드 및 처리
if os.path.exists(file_path):
    try:
        # 데이터 로드 (2행부터 데이터로 인식)
        df = pd.read_excel(file_path, sheet_name=0, header=1)
        df.columns = all_columns # 컬럼명 강제 매핑

        # 🔍 필지 검색 필터
        st.sidebar.header("🔍 필지 검색")
        dong_list = sorted(df['동리'].dropna().unique())
        target_dong = st.sidebar.selectbox("동/리 선택", options=["전체"] + list(dong_list))
        search_jibun = st.sidebar.text_input("지번 입력 (예: 1080-2)")

        # 데이터 필터링
        filtered_df = df.copy()
        if target_dong != "전체":
            filtered_df = filtered_df[filtered_df['동리'] == target_dong]
        if search_jibun:
            filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

        # 🔢 순번을 1번부터 시작하게 만들기
        filtered_df.index = range(1, len(filtered_df) + 1)

        # 결과 출력
        st.subheader(f"✅ {selected_region} 조회 결과 (총 {len(filtered_df)}건)")
        
        # 선택된 항목이 있을 때만 표 표시
        if selected_cols:
            st.dataframe(filtered_df[selected_cols], use_container_width=True)
        else:
            st.warning("표시할 항목을 하나 이상 선택해 주세요.")

        # 📍 위치 확인 (네이버 지도 연동)
        st.markdown("---")
        st.subheader("📍 위치 확인 (네이버 지도)")
        
        if not filtered_df.empty:
            # 상위 10건 지도 보기 버튼
            for _, row in filtered_df.head(10).iterrows():
                full_address = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
                map_url = f"https://map.naver.com/v5/search/{full_address}"
                btn_label = f"👉 {row['동리']} {row['번지']} 위치 보기"
                st.link_button(btn_label, map_url)
        else:
            st.info("검색 조건에 맞는 필지가 없습니다.")

    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
else:
    st.warning(f"서버에 '{selected_region}' 데이터가 없습니다.")