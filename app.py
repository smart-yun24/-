import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정 (서비스 명칭 변경 및 레이아웃 최적화)
st.set_page_config(page_title="낙동강 상류 조서 조회 서비스", layout="wide", initial_sidebar_state="collapsed")

# 2. 고도화된 UI 디자인 (국유지/사유지 배경 차별화 및 글자 크기 확대)
st.markdown("""
    <style>
    /* 전체 배경 및 기본 폰트 크기 확대 (0.85rem -> 0.98rem) */
    .stApp { background-color: #f8fafc; }
    html, body { font-size: 0.98rem; } 
    
    /* [요청 3] 메인 타이틀 디자인 */
    .main-service-title { 
        font-size: 1.15rem !important; 
        font-weight: 800; 
        color: #1e3a8a; 
        text-align: center; 
        margin-bottom: 15px; 
        letter-spacing: -0.5px;
    }
    
    /* 팝오버 검색 버튼 */
    div[data-testid="stPopover"] > button {
        width: 100%; height: 50px !important;
        font-size: 1.0rem !important; font-weight: 800 !important;
        border-radius: 12px !important; background-color: #2563eb !important;
        color: white !important; border: none !important;
    }

    /* 필터 내부 0.65rem 유지 */
    div[data-testid="stPopover"] label, 
    div[data-testid="stPopover"] div[data-baseweb="select"], 
    div[data-testid="stPopover"] input {
        font-size: 0.65rem !important; 
    }
    
    /* [요청 4] 필지 카드 디자인 (국유지 vs 사유지) */
    .property-card {
        padding: 18px; border-radius: 14px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 18px; 
        border: 1px solid #e2e8f0; position: relative; overflow: hidden;
    }

    /* 국유지 전용 스타일: 연한 파랑 배경 + 빗금(Hatch) 패턴 */
    .national-card {
        background-color: #f0f7ff;
        background-image: repeating-linear-gradient(
            45deg, 
            transparent, 
            transparent 10px, 
            rgba(37, 99, 235, 0.03) 10px, 
            rgba(37, 99, 235, 0.03) 20px
        );
    }

    /* 사유지 전용 스타일: 순백색 배경 */
    .private-card {
        background-color: #ffffff;
    }

    /* 좌우 분할 헤더 */
    .card-header-flex {
        display: flex; justify-content: space-between; align-items: flex-start;
        gap: 10px; margin-bottom: 12px;
    }
    
    .address-text { 
        font-size: 1.05rem; font-weight: 800; color: #0f172a; 
        line-height: 1.4; flex: 1; 
    }

    /* 소유자 뱃지 (상세 정보 노출) */
    .owner-badge {
        font-size: 0.8rem; font-weight: 700; color: #2563eb;
        background-color: rgba(255, 255, 255, 0.8);
        padding: 4px 10px; border-radius: 8px;
        white-space: nowrap; border: 1px solid #dbeafe;
    }

    /* 지목 뱃지 */
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; margin-bottom: 8px; }
    .badge-천 { background-color: #bae6fd; color: #0369a1; }
    .badge-임 { background-color: #bbf7d0; color: #15803d; }
    .badge-제 { background-color: #f1f5f9; color: #475569; }
    .badge-default { background-color: #f3f4f6; color: #374151; }

    /* 데이터 그리드 */
    .info-container { 
        display: flex; justify-content: space-between; 
        background-color: rgba(255, 255, 255, 0.5); 
        padding: 12px; border-radius: 10px; border: 1px solid rgba(0,0,0,0.03);
    }
    .label { font-size: 0.75rem; color: #64748b; margin-bottom: 2px; display: block; }
    .value { font-size: 1.0rem; font-weight: 700; color: #1e293b; }
    .value-red { font-size: 1.0rem; font-weight: 700; color: #ef4444; }

    .map-action-btn {
        display: block; text-align: center; background-color: #03c75a; color: white !important; 
        padding: 12px; border-radius: 10px; text-decoration: none !important; 
        font-weight: 800; font-size: 0.95rem; margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# [요청 3] 타이틀 변경 반영
st.markdown('<p class="main-service-title">🏞️ 낙동강 상류 조서 조회 서비스</p>', unsafe_allow_html=True)

# 3. 데이터 로딩 설정
region_files = {
    "예천군": "01_yecheon.xlsm", "구미시": "02_gumi.xlsm", "고령군": "03_goryeong.xlsm",
    "달성군": "04_dalseong.xlsm", "달서구": "05_dalseo.xlsm", "문경시": "06_mungyeong.xlsm",
    "안동시": "07_andong.xlsm", "의성군": "08_uiseong.xlsm", "칠곡군": "09_chilgok.xlsm",
    "상주시": "10_sangju.xlsm", "성주군": "11_seongju.xlsm"
}

with st.popover("🔍 지역 및 지번 검색"):
    selected_region = st.selectbox("🎯 대상 지역", options=list(region_files.keys()))
    file_path = region_files[selected_region]
    
    if os.path.exists(file_path):
        df_raw = pd.read_excel(file_path, sheet_name=0, header=1)
        df = df_raw.iloc[:, :10].copy()
        df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
        
        dong_list = sorted(df['동리'].dropna().unique())
        target_dong = st.selectbox("📍 동/리 선택", options=["전체 지역"] + list(dong_list))
        search_jibun = st.text_input("🏠 지번 입력 (예: 1080-2)")
    else:
        st.error(f"파일 없음: {file_path}")
        st.stop()

# 4. 필터링 로직
filtered_df = df.copy()
if target_dong != "전체 지역":
    filtered_df = filtered_df[filtered_df['동리'] == target_dong]
if search_jibun:
    filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

st.markdown(f"**현재 조회된 필지: {len(filtered_df):,}건**")

# 5. 결과 카드 출력 (국유지/사유지 시각적 구분 적용)
for _, row in filtered_df.head(50).iterrows():
    full_addr = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
    jimok = str(row['지목'])
    badge_class = f"badge-{jimok}" if jimok in ['천', '임', '제'] else "badge-default"
    
    # [요청 1, 4] 소유자 성함 상세화 및 배경 차별화 판단
    owner_name = str(row['소유자_성명'])
    is_national = owner_name.startswith('국')
    card_type = "national-card" if is_national else "private-card"
    
    st.markdown(f"""
        <div class="property-card {card_type}">
            <span class="badge {badge_class}">{jimok}</span>
            <div class="card-header-flex">
                <span class="address-text">📍 {full_addr}</span>
                <span class="owner-badge">{owner_name}</span>
            </div>
            <div class="info-container">
                <div><span class="label">지적면적</span><span class="value">{row['지적_m2']:,}㎡</span></div>
                <div style="text-align:right;"><span class="label" style="color:#ef4444;">편입면적</span><span class="value-red">{row['편입면적_m2']:,}㎡</span></div>
            </div>
            <a href="https://map.naver.com/v5/search/{full_addr}" target="_blank" class="map-action-btn">🗺️ 위치 확인 (네이버 지도)</a>
        </div>
    """, unsafe_allow_html=True)