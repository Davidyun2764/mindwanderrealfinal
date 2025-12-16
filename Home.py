import streamlit as st
from mindswitch_utils import (
    APP_TITLE, init_state, render_sidebar,
    start_timer_minutes, reset_mind_anchors, go
)

st.set_page_config(page_title=APP_TITLE, layout="centered")
init_state()
render_sidebar()

st.title(APP_TITLE)
st.caption("멀티페이지 구조: Setup → Work → Choose → Mind → Post → Results")

st.subheader("⚙️ 시작 설정 (Setup)")

st.markdown("### 📌 MWI(멍때림 지수)가 뭐야?")
st.markdown(
    """
**MWI(Mind-Wandering Index)**는 “멍때림(휴식) 후에 내 인지 성능이 얼마나 회복/개선되었는지”를  
간단한 숫자로 표현한 **사용자 정의 지표**예요.

- 반응시간(초): **줄면(빨라지면)** 좋음  
- 오류 개수: **줄면** 좋음  
- 아이디어 개수: **늘면** 좋음  

이 개선율들을 합쳐 점수로 만들고, **휴식 시간(분)**으로 나눠서 “분당 효율”처럼 계산합니다.
"""
)

st.session_state.work_min = st.slider(
    "작업 시간(분) 설정", 5, 90, int(st.session_state.work_min), step=5
)

st.markdown("### (선택) 휴식 전 측정값 입력")
st.caption("MWI 계산을 위해 ‘휴식 전/후’ 값이 필요해요. 귀찮으면 0으로 두고 진행해도 됩니다.")

c1, c2, c3 = st.columns(3)
with c1:
    pre_rt = st.number_input("반응시간(초, 평균)", min_value=0.0, value=0.0, step=0.01)
with c2:
    pre_err = st.number_input("오류 개수", min_value=0, value=0, step=1)
with c3:
    pre_idea = st.number_input("아이디어 개수", min_value=0, value=0, step=1)

if st.button("🚀 Work 모드 시작"):
    st.session_state.pre_metrics = {
        "rt": None if pre_rt <= 0 else float(pre_rt),
        "err": int(pre_err),
        "idea": int(pre_idea)
    }
    st.session_state.work_remaining_sec = None
    reset_mind_anchors()
    start_timer_minutes(st.session_state.work_min)
    go("pages/1_Work.py")