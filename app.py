import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정 및 모바일 최적화
st.set_page_config(page_title="하천구역 스마트 조회", layout="wide", initial_sidebar_state="collapsed")

# 2. 전구간 폰트 20% 축소 및 지목별 컬러 디자인
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    html, body { font-size: 0.85rem; } /* 전체 글자 크기 축소 반영 */
    
    .mobile-header { font-size: 1.0rem !important; font-weight: 800; color: #1e3a8a; text-align: center; margin-bottom: 12px; }
    
    .property-card {
        background-color: white; padding: 14px; border-radius: 12px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 15px; border: 1px solid #e2e8f0;
    }

    /* 지목 뱃지 스타일 (배경색만 존재) */
    .badge {
        display: inline-block; padding: 2px 8px; border-radius: 4px; 
        font-size: 0.7rem; font-weight: 700; margin-bottom: 6px;
    }
    .badge-천 { background-color: #e0f2fe; color: #0369a1; } /* 하천 - 하늘색 */
    .badge-임 { background-color: #dcfce7; color: #15803d; } /* 임야 - 초록색 */
    .badge-전, .badge-답 { background-color: #fef9c3; color: #a16207; } /* 농지 - 노란색 */
    .badge-제 { background-color: #f1f5f9; color: #475569; } /* 제방 - 회색 */
    .badge-default { background-color: #f3f4f6; color: #374151; }

    /* 주소 및 소유자 통합 헤더 디자인 */
    .card-header-box { display: flex; flex-direction: column; margin-bottom: 10px; gap: 2px; }
    .address-text { font-size: 0.95rem; font-weight: 800; color: #0f172a; line-height: 1.3; }
    .owner-tag { font-size: 0.8rem; font-weight: 600; color: #2563eb; }

    /* 면적 정보 레이아웃 */
    .info-container { 
        display: flex; justify-content: space-between; 
        background-color: #f8fafc; padding: 10px; border-radius: 8px; margin-bottom: 12px;
    }
    .label { font-size: 0.65rem; color: #64748b; }
    .value { font-size: 0.85rem; font-weight: 700; color: #1e293b; }
    .value-red { font-size: 0.85rem; font-weight: 700; color: #ef4444; }

    /* 지도 버튼 디자인 */
    .map-action-btn {
        display: block; text-align: center; background-color: #03c75a; color: white !important; 
        padding: 12px; border-radius: 10px; text-decoration: none !important; 
        font-weight: 800; font-size: 0.85rem; box-shadow: 0 4px 6px rgba(3, 199, 90, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="mobile-header">🌊 하천구역 스마트 조회</p>', unsafe_allow_html=True)

# 3. 지자체 파일 매핑
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
        df = pd.read_excel(file_path, sheet_name=0, header=1)
        # 10개 항목 강제 매핑
        df.columns = ['구역', '시군', '읍면', '동리', '번지', '지목', '지적_m2', '편입면적_m2', '소유자_주소', '소유자_성명']
        
        dong_list = sorted(df['동리'].dropna().unique())
        target_dong = st.selectbox("📍 동/리", options=["전체 지역"] + list(dong_list))
        search_jibun = st.text_input("🏠 지번 입력 (예: 1080-2)")
    else:
        st.error(f"파일 없음: {file_path}")
        st.stop()

# 4. 필터링 및 카드 출력
filtered_df = df.copy()
if target_dong != "전체 지역":
    filtered_df = filtered_df[filtered_df['동리'] == target_dong]
if search_jibun:
    filtered_df = filtered_df[filtered_df['번지'].astype(str).str.contains(search_jibun)]

st.markdown(f"**총 {len(filtered_df):,}건**")

for _, row in filtered_df.head(50).iterrows():
    # 요청대로 시군/읍면 포함한 풀 주소 생성
    full_addr = f"{row['시군']} {row['읍면']} {row['동리']} {row['번지']}"
    
    # 지목별 클래스 결정 (배경색 전용)
    jimok = str(row['지목'])
    badge_class = f"badge-{jimok}" if jimok in ['천', '임', '전', '답', '제'] else "badge-default"
    
    # [핵심] st.markdown 안에 unsafe_allow_html=True가 반드시 있어야 함
    st.markdown(f"""
        <div class="property-card">
            <span class="badge {badge_class}">{jimok}</span>
            <div class="card-header-box">
                <span class="address-text">📍 {full_addr}</span>
                <span class="owner-tag">👤 소유자: {row['소유자_성명']}</span>
            </div>
            
            <div class="info-container">
                <div>
                    <span class="label">지적면적</span><br/>
                    <span class="value">{row['지적_m2']:,}㎡</span>
                </div>
                <div style="text-align:right;">
                    <span class="label" style="color:#ef4444;">편입면적</span><br/>
                    <span class="value-red">{row['편입면적_m2']:,}㎡</span>
                </div>
            </div>
            
            <a href="https://map.naver.com/v5/search/{full_addr}" target="_blank" class="map-action-btn">
                🗺️ 지도 위치 확인
            </a>
        </div>
    """, unsafe_allow_html=True)