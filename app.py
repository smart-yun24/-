import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="하천구역 편입조회 시스템", layout="wide")

st.title("🌊 하천구역 편입면적 실시간 조회 시스템")
st.markdown("본 시스템은 하천기본계획 조서를 바탕으로 정보를 제공합니다.")

# 서버에 저장된 엑셀 파일을 직접 읽어오기
# (파일이 GitHub 저장소에 '예천군.xlsm' 이름으로 있어야 합니다)
file_path = "예천군.xlsm"

try:
    # 데이터 로드 (첫 번째 시트, 헤더는 2번째 줄 기준)
    df = pd.read_excel(file_path, sheet_name=0, header=1)
    
    # 컬럼명 자동 매핑 (매니저님의 엑셀 구조에 맞춤)
    df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '전체면적', '하천구역_편입', 
                  '예정지', '폐천', '홍수관리', '주소', '성명', '구분1', '구분2', '하천명', 
                  'PNU', '총면적_m2', '본번', '부번']

    # 검색 사이드바
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
    st.subheader(f"✅ 조회 결과 (총 {len(filtered_df)}건)")
    
    if not filtered_df.empty:
        # 주요 정보 출력
        display_cols = ['동리', '번지', '지목', '총면적_m2', '하천구역_편입', '성명', 'PNU']
        st.dataframe(filtered_df[display_cols], use_container_width=True)
        
        # 개별 필지 지도 연동 기능 추가
        st.markdown("---")
        st.subheader("📍 위치 확인 (네이버 지도)")
        for _, row in filtered_df.head(5).iterrows(): # 너무 많으면 복잡하므로 상위 5건만 버튼 생성
            pnu = str(row['PNU'])
            # PNU를 활용한 외부 지도 서비스 연동
            naver_map_url = f"https://map.naver.com/v5/search/{pnu}"
            st.link_button(f"👉 {row['동리']} {row['번지']} (편입: {row['하천구역_편입']}㎡) 위치 보기", naver_map_url)
            
    else:
        st.warning("일치하는 지번 정보가 없습니다.")

except FileNotFoundError:
    st.error("서버에서 '예천군.xlsm' 파일을 찾을 수 없습니다. GitHub에 파일을 먼저 업로드해주세요.")
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")