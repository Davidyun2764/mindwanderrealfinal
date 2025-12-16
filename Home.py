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
**MWI(Mind-Wandering Index)**는 멍때림(휴식) 후에 내 상태가 얼마나 회복/개선됐는지를 점수로 표현하기 위한 지표예요.

- ✅ **Easy-MWI(체크형)**: 질문1~3에 체크만 하면 자동 계산  
- 🔧 **정량 MWI(선택)**: 반응시간/오류/아이디어 수 같은 숫자 입력으로 계산
"""
)

# ----------------------------
# ✅ (추가) Easy-MWI 시작 전 기록(질문1)
# ----------------------------
st.markdown("### 🟢 (선택) 시작 전 간이 체크(Easy-MWI 사전 기록)")
st.caption("체크만 하고 시작할 수 있어요. (안 해도 OK)")

if "pre_easy" not in st.session_state:
    st.session_state.pre_easy = {"q1_pre": None}

q1_opts_pre = [
    "1. 전혀 아니다",
    "2. 아니다",
    "3. 보통이다",
    "4. 꽤 맑아졌다",
    "5. 매우 맑아졌다"
]
q1_score_pre = {q1_opts_pre[0]: 0, q1_opts_pre[1]: 1, q1_opts_pre[2]: 2, q1_opts_pre[3]: 3, q1_opts_pre[4]: 4}

pre_q1_choice = st.radio(
    "시작 전) 지금 머리 상태는 어떤가요?",
    options=q1_opts_pre,
    index=2
)
st.session_state.pre_easy["q1_pre"] = q1_score_pre[pre_q1_choice]

# ----------------------------
# 작업 시간 설정(기존)
# ----------------------------
st.session_state.work_min = st.slider(
    "작업 시간(분) 설정", 5, 90, int(st.session_state.work_min), step=5
)

# ----------------------------
# (기존 기능 유지) 정량 MWI 사전 입력(선택)
# ----------------------------
with st.expander("🔧 (선택) 휴식 전 정량 측정값 입력(기존 기능 그대로)", expanded=False):
    st.caption("MWI 정량 계산을 위해 ‘휴식 전/후’ 값이 필요해요. 귀찮으면 0으로 두고 진행해도 됩니다.")

    c1, c2, c3 = st.columns(3)
    with c1:
        pre_rt = st.number_input("반응시간(초, 평균)", min_value=0.0, value=0.0, step=0.01)
    with c2:
        pre_err = st.number_input("오류 개수", min_value=0, value=0, step=1)
    with c3:
        pre_idea = st.number_input("아이디어 개수", min_value=0, value=0, step=1)

if "pre_rt" not in locals():
    pre_rt = 0.0
if "pre_err" not in locals():
    pre_err = 0
if "pre_idea" not in locals():
    pre_idea = 0

# ----------------------------
# Work 모드 시작(기존)
# ----------------------------
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
