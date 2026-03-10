import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="하천구역 통합 조회 시스템", layout="wide")

st.title("🌊 하천구역 편입면적 통합 조회 시스템")
st.markdown("전국 지자체별 하천기본계획 조서를 실시간으로 조회합니다.")

# 1. 지자체별 파일 매핑 (GitHub에 올릴 파일명과 일치해야 합니다)
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

# 2. 사이드바 - 지역 및 검색 설정
st.sidebar.header("📍 지역 및 필지 설정")
selected_region = st.sidebar.selectbox("대상 지자체 선택", options=list(region_files.keys()))

# 선택된 파일 경로
file_path = region_files[selected_region]

# 데이터 로드
if os.path.exists(file_path):
    try:
        # 매니저님 엑셀 양식 기준 (2번째 줄이 제목)
        df = pd.read_excel(file_path, sheet_name=0, header=1)
        
        # 컬럼명 고정 매핑
        df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '전체면적', '하천구역_편입', 
                      '예정지', '폐천', '홍수관리', '주소', '성명', '구분1', '구분2', '하천명', 
                      'PNU', '총면적_m2', '본번', '부번']

        # 검색 필터
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

        # 3. 위치 확인 (지도 연동)
        st.markdown("---")
        st.subheader("📍 위치 확인 (네이버 지도)")
        for _, row in filtered_df.head(5).iterrows():
            pnu = str(row['PNU'])
            naver_map_url = f"https://map.naver.com/v5/search/{pnu}"
            st.link_button(f"👉 {row['동리']} {row['번지']} (편입: {row['하천구역_편입']}㎡) 위치 보기", naver_map_url)

    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
else:
    st.warning(f"서버에 '{selected_region}' 데이터 파일({file_path})이 없습니다. GitHub에 업로드해 주세요.")