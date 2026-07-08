import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta, timezone
import streamlit.components.v1 as components

# 1. 모바일 화면 설정
st.set_page_config(page_title="아차사고 신고", page_icon="🚨", layout="centered", initial_sidebar_state="collapsed")

# --- UI 및 워터마크 완벽 숨기기 + 상단 맞춤 최적화 ---
hide_streamlit_style = """
<style>
/* 1. 모바일(기본)에서는 전체 콘텐츠를 맨 위 상단으로 바짝 붙이기 */
[data-testid="stMainBlockContainer"] {
    padding-top: 0rem !important;
    padding-bottom: 1rem !important;
}

/* 2. PC 화면(화면 너비 768px 이상)일 때만 로고가 잘리지 않도록 상단 여백을 2rem으로 자동 확보 */
@media (min-width: 768px) {
    [data-testid="stMainBlockContainer"] {
        padding-top: 2rem !important;
    }
}

/* 3. 앱 내부 기본 요소 숨기기 */
[data-testid="stToolbar"] {visibility: hidden !important;}
footer {display: none !important;}
footer:after {content: "" !important;}
.stDeployButton {display: none !important;}
[data-testid="stStatusWidget"] {visibility: hidden !important;}
[data-testid="stHeaderActionElements"] {display: none !important;}

/* 4. 외부 배지 클래스 미리 숨기기 */
.viewerBadge, [class*="ViewerBadge"], [class*="viewerBadge"] {
    display: none !important;
    visibility: hidden !important;
}
/* 입력창 하단 "Press Ctrl+Enter..." 안내 문구 숨기기 */
[data-testid="InputInstructions"] {
    display: none !important;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 실시간 감시기를 이용해 로딩 잔상 차단 (자바스크립트)
components.html(
    """
    <script>
    const topDoc = window.top.document;
    function purgeBadges() {
        topDoc.querySelectorAll('[href*="streamlit"], [href*="github"], .viewerBadge, [class*="ViewerBadge"], [class*="viewerBadge"]').forEach(function(e) {
            e.setAttribute("style", "display: none !important;");
        });
    }
    purgeBadges();
    const observer = new MutationObserver(function(mutations) { purgeBadges(); });
    observer.observe(topDoc.body, { childList: true, subtree: true });
    </script>
    """,
    height=0,
    width=0,
)
# --- 숨기기 설정 끝 ---

# 🔴 [주의] 본인의 구글 주소를 꼭 따옴표"" 안에 다시 넣어주세요!
WEBAPP_URL = st.secrets["WEBAPP_URL"]
SHEET_ID = st.secrets["SHEET_ID"]

# 1. 상단 인천여성가족재단 CI 로고
col1, col2, col3 = st.columns([1.2, 1.6, 1.2])
with col2:
    st.image("logo.jpg", use_container_width=True) 

# 2. 아랫줄 타이틀 및 안내 문구
st.markdown("<h1 style='text-align: center; margin-top: -40px; margin-bottom: 15px;'>아차사고 신고 🚨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666666; font-size: 1.1rem;'>위험 요소를 알려주세요!</p>", unsafe_allow_html=True)

# 3. 작업자용 신고 폼
with st.form("report_form"):
    location = st.radio("발견 위치", ["1층", "2층", "3층", "4층", "별관", "지상주차장", "지하주차장", "외곽", "기타"], horizontal=True)
    description = st.text_area("어떤 위험 요소가 있나요?", placeholder="예: 벽, 바닥 손상 등, 미끄러짐 위험, 부딪힘 위험 등")
    
    submitted = st.form_submit_button("신고 제출하기", use_container_width=True)

    if submitted:
        if description == "":
            st.warning("상황 설명을 간단히 적어주세요.")
        else:
            KST = timezone(timedelta(hours=9))
            now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
            payload = {"date": now, "location": location, "description": description}
            try:
                response = requests.post(WEBAPP_URL, data=json.dumps(payload))
                if response.status_code == 200:
                    st.success("✅ 신고가 접수되었습니다! 안전한 환경을 만드는데 도움주셔서 감사합니다.")
                else:
                    st.error("전송에 실패했습니다.")
            except Exception as e:
                st.error(f"연결 오류 발생: {e}")

# 4. 하단 아차사고 정의 안내 문구 박스 (회색 배경에 깔끔한 빨간 포인트 선)
st.markdown(
    "<div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #ff4b4b; margin-top: -10px; margin-bottom: 20px;'>"
    "<p style='margin: 0; font-weight: bold; color: #333333; font-size: 0.95rem;'>💡 아차사고(Near Miss)란?</p>"
    "<p style='margin: 6px 0 0 0; color: #555555; font-size: 0.85rem; line-height: 1.5; text-align: justify;'>"
    "부상이나 질병으로 이어질 뻔했던 아슬아슬한 위험 상황을 뜻합니다. "
    "동일하거나 유사한 위험 요인이 방치될 경우 향후 큰 중대재해로 발전할 수 있으므로, "
    "사전에 위험 요소를 발굴하고 개선하는 것이 무엇보다 중요합니다."
    "</p>"
    "</div>",
    unsafe_allow_html=True
)

# 5. 관리자 확인용 메뉴 (사이드바)
with st.sidebar:
    st.subheader("📋 관리자 전용")
    admin_password = st.text_input("관리자 암호", type="password")
    # ✅ 수정 후 (비밀 금고의 비밀번호와 비교하기)
if admin_password == st.secrets["ADMIN_PW"]:
        st.success("✅ 관리자 인증 완료")
        st.divider()
        try:
            csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
            df = pd.read_csv(csv_url)
            if df.empty:
                st.info("현재 접수된 아차사고 신고가 없습니다.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.caption(f"총 접수 건수: {len(df)}건")
        except Exception as e:
            st.error("구글 시트 데이터를 불러오는데 실패했습니다.")
