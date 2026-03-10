import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="하천구역 통합 조회 시스템", layout="wide")

st.title("🌊 하천구역 편입면적 통합 조회 시스템")
st.markdown("본 시스템은 업로드된 하천구역 지번조서를 바탕으로 정보를 제공합니다.")

# 1. 지자체별 파일 매핑 (GitHub에 올린 파일명과 일치해야 합니다)
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

# 2. 사이드바 - 지자체 선택
st.sidebar.header("📍 지역 설정")
selected_region = st.sidebar.selectbox("대상 지자체 선택", options=list(region_files.keys()))

# 파일 경로 설정
file_path = region_files[selected_region]

# 데이터 로드
if os.path.exists(file_path):
    try:
        # 데이터 로드 (첫 번째 행은 시.군, 구.면 등 레이블이므로 2행부터 데이터로 인식)
        # header=1 설정을 통해 '좌174, 예천군...' 줄부터 읽습니다.
        df = pd.read_excel(file_path, sheet_name=0, header=1)
        
        # 컬럼명 수동 지정 (새로운 양식에 맞춤)
        df.columns = [
            '구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명'
        ]

        # 3. 사이드바 - 상세 검색
        st.sidebar.header("🔍 필지 검색")
        
        # 동리 목록 추출 및 정렬
        dong_list = sorted(df['동리'].dropna().unique())
        target_dong = st.sidebar.selectbox("동/리 선택", options=["전체"] + list(dong_list))
        
        search_jibun = st.sidebar.text_input("지번 입력 (예: 1080-2)")

        # 데이터 필터링
        filtered_df = df.copy()
        if target_dong != "전체":
            filtered_df = filtered_df[filtered_df['동리'] == target_dong]
        if search_jibun:
            filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

        # 결과 출력
        st.subheader(f"✅ {selected_region} 조회 결과 (총 {len(filtered_df)}건)")
        
        # 테이블 표시
        st.dataframe(filtered_df, use_container_width=True)

        # 4. 지도 연동 버튼 (네이버 지도 검색 연동)
        st.markdown("---")
        st.subheader("📍 위치 확인 (네이버 지도)")
        
        if not filtered_df.empty:
            # 상위 10건에 대해 지도 보기 버튼 생성
            for _, row in filtered_df.head(10).iterrows():
                # 주소 조합: 시군 + 읍면 + 동리 + 번지
                full_address = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
                map_url = f"https://map.naver.com/v5/search/{full_address}"
                
                btn_label = f"👉 {row['동리']} {row['번지']} (편입: {row['편입면적_m2']:,}㎡) 지도 보기"
                st.link_button(btn_label, map_url)
        else:
            st.info("검색 조건에 맞는 필지가 없습니다.")

    except Exception as e:
        st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
        st.info("엑셀 파일 양식이 '01_yecheon.xlsm'과 동일한지 확인해 주세요.")
else:
    st.warning(f"서버에 '{selected_region}' 데이터 파일({file_path})이 없습니다. GitHub에 업로드해 주세요.")