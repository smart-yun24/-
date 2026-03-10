import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="하천구역 통합 조회 시스템", layout="wide")

st.title("🌊 하천구역 편입면적 통합 조회 시스템")

# 1. 지역별 파일 매핑 (여기에 새로운 지역을 계속 추가하시면 됩니다)
region_files = {
    "예천군": "data.xlsm",
    "안동시": "andong.xlsm",
    "의성군": "uiseong.xlsm"
}

# 2. 사이드바 - 지역 선택
st.sidebar.header("📍 지역 설정")
selected_region = st.sidebar.selectbox("대상 지자체 선택", options=list(region_files.keys()))

# 선택된 지역의 파일 경로
file_path = region_files[selected_region]

# 데이터 로드 로직
if os.path.exists(file_path):
    try:
        # 매니저님 양식에 맞춘 데이터 로드 (header=1)
        df = pd.read_excel(file_path, sheet_name=0, header=1)
        
        # 컬럼명 자동 지정
        df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '전체면적', '하천구역_편입', 
                      '예정지', '폐천', '홍수관리', '주소', '성명', '구분1', '구분2', '하천명', 
                      'PNU', '총면적_m2', '본번', '부번']

        # 3. 사이드바 - 상세 검색
        st.sidebar.header("🔍 필지 검색")
        target_dong = st.sidebar.selectbox("동/리 선택", options=["전체"] + list(df['동리'].unique()))
        search_jibun = st.sidebar.text_input("지번 입력 (예: 659 또는 산59-1)")

        # 필터링 로직
        filtered_df = df.copy()
        if target_dong != "전체":
            filtered_df = filtered_df[filtered_df['동리'] == target_dong]
        if search_jibun:
            filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

        # 결과 출력
        st.subheader(f"✅ {selected_region} 조회 결과 (총 {len(filtered_df)}건)")
        display_cols = ['동리', '번지', '지목', '총면적_m2', '하천구역_편입', '성명', 'PNU']
        st.dataframe(filtered_df[display_cols], use_container_width=True)

        # 지도 연동 버튼
        st.markdown("---")
        st.subheader("📍 위치 확인 (네이버 지도)")
        for _, row in filtered_df.head(5).iterrows():
            pnu = str(row['PNU'])
            naver_map_url = f"https://map.naver.com/v5/search/{pnu}"
            st.link_button(f"👉 {row['동리']} {row['번지']} 위치 보기", naver_map_url)

    except Exception as e:
        st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
else:
    st.warning(f"서버에서 '{selected_region}' 데이터를 찾을 수 없습니다. GitHub에 파일을 먼저 업로드해주세요.")