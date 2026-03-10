import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="하천구역 통합 조회 시스템", layout="wide")

st.title("🌊 하천구역 편입면적 통합 조회 시스템")
st.markdown("본 시스템은 2026년 최신 하천기본계획 조서 양식을 바탕으로 정보를 제공합니다.")

# 1. 지자체별 파일 매핑 (GitHub에 올린 영문 파일명과 일치해야 함)
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
        # 새 양식 기준: 첫 번째 줄(index 0)이 헤더임
        df = pd.read_excel(file_path, sheet_name=0, header=0)
        
        # 컬럼명 정리 (사용자 제공 01_yecheon.xlsm 기준)
        # 데이터 정합성을 위해 명칭을 강제로 맞춤
        df.columns = [
            '구역', '시군', '구면', '동리', '번지', '지목', '지적', '하천구역', 
            '예정지', '폐천구역', '홍수관리구역', '주소', '성명', '구분1', '구분2', 
            '하천명', 'PNU', '전필지면적_m2', '본번', '부번'
        ]

        # 검색 필터
        target_dong = st.sidebar.selectbox("동/리 선택", options=["전체"] + sorted(list(df['동리'].dropna().unique())))
        search_jibun = st.sidebar.text_input("지번 입력 (예: 659 또는 산59-1)")

        # 필터링 로직
        filtered_df = df.copy()
        if target_dong != "전체":
            filtered_df = filtered_df[filtered_df['동리'] == target_dong]
        if search_jibun:
            # 지번 컬럼에서 검색어 포함 여부 확인
            filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

        # 결과 출력
        st.subheader(f"✅ {selected_region} 조회 결과 (총 {len(filtered_df)}건)")
        
        # 주요 정보 위주로 테이블 구성
        display_cols = ['동리', '번지', '지목', '전필지면적_m2', '하천구역', '성명', 'PNU']
        st.dataframe(filtered_df[display_cols], use_container_width=True)

        # 3. 위치 확인 (네이버 지도 연동)
        st.markdown("---")
        st.subheader("📍 위치 확인 (네이버 지도)")
        
        if not filtered_df.empty:
            # 너무 많은 버튼 방지를 위해 상위 10건만 표시
            for _, row in filtered_df.head(10).iterrows():
                pnu = str(row['PNU'])
                # 지번 정보와 편입 면적을 버튼 이름에 표시
                btn_label = f"📍 {row['동리']} {row['번지']} (편입: {row['하천구역']:,}㎡) 위치 보기"
                naver_map_url = f"https://map.naver.com/v5/search/{pnu}"
                st.link_button(btn_label, naver_map_url)
        else:
            st.info("검색 결과가 없어 지도를 표시할 수 없습니다.")

    except Exception as e:
        st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
        st.info("엑셀 파일의 컬럼 개수나 순서가 업로드하신 '01_yecheon.xlsm'과 동일한지 확인해주세요.")
else:
    st.warning(f"서버에 '{selected_region}' 데이터 파일({file_path})이 없습니다. GitHub에 해당 이름으로 파일을 업로드해 주세요.")