import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="하천구역 편입조회 시스템", layout="wide")

st.title("🌊 하천구역 편입면적 스마트 조회기")
st.markdown("엑셀 조서를 바탕으로 지번별 편입 면적을 실시간으로 조회합니다.")

# 파일 업로드 (예천군.xlsm 기준)
uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요 (.xlsm 또는 .xlsx)", type=["xlsm", "xlsx"])

if uploaded_file:
    # 데이터 로드 (첫 번째 시트 기준, 실제 시트명에 맞춰 수정 가능)
    df = pd.read_excel(uploaded_file, sheet_name=0, header=1) # 2번째 줄이 헤더인 경우 header=1
    
    # 컬럼 정리 (사용자 파일 구조에 맞춤)
    # 실제 파일에서는 'Unnamed'로 읽힐 수 있으므로 컬럼명을 수동으로 지정하거나 매핑합니다.
    df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '전체면적', '하천구역_편입', 
                  '예정지', '폐천', '홍수관리', '주소', '성명', '구분1', '구분2', '하천명', 
                  'PNU', '총면적_m2', '본번', '부번']

    # 검색 사이드바
    st.sidebar.header("🔍 검색 필터")
    target_dong = st.sidebar.selectbox("동/리 선택", options=["전체"] + list(df['동리'].unique()))
    search_jibun = st.sidebar.text_input("지번 입력 (예: 659 또는 산59-1)")

    # 데이터 필터링 로직
    filtered_df = df.copy()
    if target_dong != "전체":
        filtered_df = filtered_df[filtered_df['동리'] == target_dong]
    if search_jibun:
        filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

    # 결과 출력
    st.subheader(f"✅ 조회 결과 (총 {len(filtered_df)}건)")
    
    if not filtered_df.empty:
        # 주요 정보만 하이라이트해서 보여주기
        display_df = filtered_df[['동리', '번지', '지목', '총면적_m2', '하천구역_편입', 'PNU', '성명']]
        st.dataframe(display_df, use_container_width=True)
        
        # 선택된 필지 요약 정보 카드
        if len(filtered_df) == 1:
            row = filtered_df.iloc[0]
            col1, col2, col3 = st.columns(3)
            col1.metric("지번", f"{row['동리']} {row['번지']}")
            col2.metric("전체 면적", f"{row['총면적_m2']:,} ㎡")
            col3.metric("편입 면적", f"{row['하천구역_편입']:,} ㎡", delta_color="inverse")
    else:
        st.warning("검색 결과가 없습니다. 지번을 다시 확인해주세요.")

else:
    st.info("왼쪽에서 '예천군.xlsm' 파일을 업로드하면 조회가 시작됩니다.")