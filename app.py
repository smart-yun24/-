import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="낙동강 상류 조서 조회 서비스", layout="wide", initial_sidebar_state="collapsed")

# 2. [최종] 디자인 통일 및 렉 방지 스타일링
# 모든 글자 크기를 검색 조건(Popover) 수준으로 통일합니다.
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    /* 전체 글자 크기 통일 (0.75rem~0.85rem 사이로 아주 촘촘하게) */
    html, body, [class*="css"] { font-size: 0.82rem; } 
    
    /* 타이틀 크기 조정 (검색 버튼과 균형) */
    .main-service-title { 
        font-size: 1.0rem !important; 
        font-weight: 800; 
        color: #1e3a8a; 
        text-align: center; 
        margin-bottom: 15px; 
    }
    
    /* 검색 팝오버 버튼 디자인 */
    div[data-testid="stPopover"] > button {
        width: 100%; height: 42px !important;
        font-size: 0.85rem !important; font-weight: 800 !important;
        border-radius: 10px !important; background-color: #2563eb !important;
        color: white !important; border: none !important;
    }

    /* 필터 내부 입력창 0.65rem 적용 */
    div[data-testid="stPopover"] label, 
    div[data-testid="stPopover"] div[data-baseweb="select"], 
    div[data-testid="stPopover"] input {
        font-size: 0.65rem !important; 
    }
    
    /* 필지 카드 디자인 (배경색으로만 구분) */
    .property-card {
        padding: 12px; border-radius: 10px; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.04); margin-bottom: 12px; 
        border: 1px solid #e2e8f0;
    }

    /* 국유지: 연파랑 배경 + 왼쪽 블루 바 */
    .national-card { background-color: #f0f7ff; border-left: 5px solid #3b82f6; }

    /* 사유지: 순백색 배경 + 왼쪽 회색 바 */
    .private-card { background-color: #ffffff; border-left: 5px solid #e2e8f0; }

    /* 좌우 분할 헤더 및 텍스트 크기 통일 */
    .card-header-flex { display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 8px; }
    .address-text { font-size: 0.82rem; font-weight: 800; color: #0f172a; line-height: 1.3; }
    .owner-badge {
        font-size: 0.65rem; font-weight: 700; color: #2563eb;
        background-color: #ffffff; padding: 2px 8px; border-radius: 4px;
        white-space: nowrap; border: 1px solid #dbeafe;
    }

    /* 데이터 그리드 스타일 */
    .info-container { 
        display: flex; justify-content: space-between; 
        background-color: rgba(248, 250, 252, 0.5); 
        padding: 8px; border-radius: 6px; 
    }
    .label { font-size: 0.65rem; color: #64748b; }
    .value { font-size: 0.8rem; font-weight: 700; color: #1e293b; }
    .value-red { font-size: 0.8rem; font-weight: 700; color: #ef4444; }

    .map-action-btn {
        display: block; text-align: center; background-color: #03c75a; color: white !important; 
        padding: 8px; border-radius: 8px; text-decoration: none !important; 
        font-weight: 800; font-size: 0.75rem; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# [데이터 캐싱 로직] 렉 방지를 위해 필수
@st.cache_data
def get_river_data(file_path):
    if os.path.exists(file_path):
        df_raw = pd.read_excel(file_path, sheet_name=0, header=1)
        df = df_raw.iloc[:, :10].copy()
        df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
        return df
    return None

st.markdown('<p class="main-service-title">낙동강 상류 조서 조회 서비스</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["하천구역 조회", "폐천부지 조회"])

# --- [Tab 1: 하천구역 서비스] ---
with tab1:
    region_files = {
        "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "고령군": "03_goryeong.xlsm",
        "달성군": "04_dalseong.xlsm", "달서구": "05_dalseo.xlsm", "문경시": "06_mungyeong.xlsm",
        "안동시": "07_andong.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm",
        "상주시": "10_sangju.xlsm", "성주군": "11_seongju.xlsm"
    }

    with st.popover("🔍 지역 및 지번 검색"):
        selected_region = st.selectbox("🎯 대상 지역", options=list(region_files.keys()), key="river_reg")
        df = get_river_data(region_files[selected_region])
        
        if df is not None:
            dong_list = sorted(df['동리'].dropna().unique())
            target_dong = st.selectbox("📍 동/리", options=["전체 지역"] + list(dong_list), key="river_dong")
            search_jibun = st.text_input("🏠 지번 입력 (예: 1080-2)", key="river_jibun")

    if df is not None:
        filtered_df = df.copy()
        if target_dong != "전체 지역":
            filtered_df = filtered_df[filtered_df['동리'] == target_dong]
        if search_jibun:
            filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

        st.markdown(f"**조회: {len(filtered_df):,}건**")

        # 렉 방지를 위해 상위 30개씩 노출
        for _, row in filtered_df.head(30).iterrows():
            full_addr = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
            # [요청 사항 반영] '국'일 경우 주소에서 부처명 추출
            owner_raw = str(row['소유자_성명']).strip()
            display_owner = str(row['소유자_주소']).strip() if owner_raw == '국' else owner_raw
            
            is_national = display_owner.startswith('국')
            card_type = "national-card" if is_national else "private-card"
            
            st.markdown(f"""
                <div class="property-card {card_type}">
                    <div class="card-header-flex">
                        <span class="address-text">📍 {full_addr}</span>
                        <span class="owner-badge">{display_owner}</span>
                    </div>
                    <div class="info-container">
                        <div><span class="label">지적</span><span class="value">{row['지적_m2']:,}㎡</span></div>
                        <div style="text-align:right;"><span class="label" style="color:#ef4444;">편입</span><span class="value-red">{row['편입면적_m2']:,}㎡</span></div>
                    </div>
                    <a href="https://map.naver.com/v5/search/{full_addr}" target="_blank" class="map-action-btn">지도 확인</a>
                </div>
            """, unsafe_allow_html=True)

# --- [Tab 2: 폐천부지 서비스] ---
with tab2:
    st.info("폐천부지 엑셀 양식을 공유해 주시면 이곳에 조서 화면을 구성해 드립니다.")