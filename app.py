import streamlit as st
import pandas as pd
import os

# 1. 페이지 테마 및 스타일 설정 (Naver 디자인 가이드 반영)
st.set_page_config(page_title="하천구역 통합 조회 시스템", layout="wide", initial_sidebar_state="expanded")

# 커스텀 CSS: 네이버 특유의 깔끔한 화이트&그린 스타일
st.markdown("""
    <style>
    /* 전체 배경색 조정 */
    .stApp { background-color: #f5f6f7; }
    
    /* 카드 스타일 컨테이너 */
    div[data-testid="stVerticalBlock"] > div > div {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e1e4e8;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* 제목 스타일 */
    h1 { color: #03C75A; font-weight: 800; font-size: 2.2rem !important; margin-bottom: 30px !important; }
    h2, h3 { color: #202020; border-left: 5px solid #03C75A; padding-left: 15px; margin-top: 20px !important; }
    
    /* 메트릭(지표) 디자인 */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-right: 1px solid #f0f0f0;
        padding: 10px;
    }
    
    /* 사이드바 스타일 */
    section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e1e4e8; }
    
    /* 버튼 스타일 */
    .stButton>button {
        background-color: #03C75A;
        color: white;
        border-radius: 8px;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover { background-color: #02a84c; border: none; transform: translateY(-2px); }
    </style>
    """, unsafe_allow_html=True)

# 헤더 영역
st.title("🌊 하천구역 통합 조회 시스템")

# 2. 지자체 매핑 정보
region_files = {
    "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "고령군": "03_goryeong.xlsm",
    "달성군": "04_dalseong.xlsm", "달서구": "05_dalseo.xlsm", "문경시": "06_mungyeong.xlsm",
    "안동시": "07_andong.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm",
    "상주시": "10_sangju.xlsm", "성주군": "11_seongju.xlsm"
}

# 3. 사이드바 구성 (설정 및 필터)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/23/Naver_Logotype.svg", width=120) # 네이버 느낌 강조
    st.markdown("### 📍 지역 설정")
    selected_region = st.selectbox("조회 대상을 선택하세요", options=list(region_files.keys()))
    file_path = region_files[selected_region]
    
    st.divider()
    
    st.markdown("### 📊 표시 정보 설정")
    all_columns = ['구역', '시군', '구면', '동리', '번지', '지목', '지적', '하천구역', '예정지', '폐천구역', '홍수관리구역', '주소', '성명', '구분1', '구분2', '하천명', 'PNU', '전필지면적_m2', '본번', '부번']
    default_active = ['동리', '번지', '지목', '전필지면적_m2', '하천구역', '성명'] #
    
    selected_cols = []
    # 네이버 스타일의 깔끔한 체크박스 리스트
    for col_name in all_columns:
        if st.checkbox(col_name, value=(col_name in default_active)):
            selected_cols.append(col_name)

# 4. 데이터 로드 및 본문 구성
if os.path.exists(file_path):
    try:
        # 엑셀 시트 분석 결과 반영 (첫 행이 데이터 레이블임)
        df = pd.read_excel(file_path, sheet_name=0, header=1)
        df.columns = all_columns
        
        # 검색 영역 (메인 화면 상단 카드)
        with st.container():
            st.markdown("### 🔍 상세 필지 검색")
            c1, c2 = st.columns(2)
            with c1:
                dong_list = sorted(df['동리'].dropna().unique())
                target_dong = st.selectbox("동/리", options=["전체 지역"] + list(dong_list))
            with c2:
                search_jibun = st.text_input("지번 (예: 659 또는 산59-1)")

        # 필터링 로직
        filtered_df = df.copy()
        if target_dong != "전체 지역":
            filtered_df = filtered_df[filtered_df['동리'] == target_dong]
        if search_jibun:
            filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

        # 순번 1번부터 시작하도록 인덱스 조정
        filtered_df.index = range(1, len(filtered_df) + 1)

        # 요약 정보 메트릭 (네이버 금융 스타일)
        m1, m2, m3 = st.columns(3)
        m1.metric("총 검색 결과", f"{len(filtered_df):,} 건")
        m2.metric("현재 지역", selected_region)
        if '하천구역' in filtered_df.columns:
            total_area = pd.to_numeric(filtered_df['하천구역'], errors='coerce').sum()
            m3.metric("총 편입면적 합계", f"{total_area:,.2f} ㎡", delta="실시간 계산됨", delta_color="normal")

        # 결과 데이터 테이블
        st.markdown(f"### 📋 {selected_region} 조서 데이터")
        if selected_cols:
            st.dataframe(filtered_df[selected_cols], use_container_width=True, height=450)
        else:
            st.warning("표시할 항목을 사이드바에서 선택해 주세요.")

        # 5. 지도 위치 확인 (네이버 지도 스타일 버튼)
        st.markdown("### 📍 위치 확인 (네이버 지도 연동)")
        if not filtered_df.empty:
            btn_container = st.container()
            with btn_container:
                cols = st.columns(4) # 버튼을 4열로 더 조밀하게 배치
                for i, (_, row) in enumerate(filtered_df.head(12).iterrows()):
                    with cols[i % 4]:
                        pnu = str(row['PNU'])
                        map_url = f"https://map.naver.com/v5/search/{pnu}"
                        st.link_button(f"🚩 {row['동리']} {row['번지']}", map_url, use_container_width=True)
        
    except Exception as e:
        st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
else:
    st.error(f"'{selected_region}' 데이터 파일을 찾을 수 없습니다. (파일명: {file_path})")

# 하단 정보
st.markdown("---")
st.caption("© 2026 하천관리 시스템 - 네이버 스타일 대시보드 인터페이스")