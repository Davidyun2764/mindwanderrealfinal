import streamlit as st
from mindswitch_utils import (
    APP_TITLE, init_state, render_sidebar,
    STIMULI, REST_CHOICES, DEFAULT_REST_MIN,
    bandit_recommend, reset_mind_anchors,
    start_timer_minutes, start_timer_seconds, go
)

st.set_page_config(page_title=APP_TITLE, layout="centered")
init_state()
render_sidebar()

st.title(APP_TITLE)
st.subheader("🧠 Mind-wander 준비")

rec, reason = bandit_recommend()
st.session_state.recommended_stim = rec
st.session_state.recommend_reason = reason
st.success(f"✅ 오늘의 추천 자극: **{STIMULI[rec]}** / {reason}")

chosen = st.selectbox(
    "유도 방식 선택",
    list(STIMULI.keys()),
    format_func=lambda k: STIMULI[k],
    index=list(STIMULI.keys()).index(rec)
)
st.session_state.chosen_stim = chosen

st.session_state.rest_min = st.selectbox(
    "멍때림 시간(분)",
    REST_CHOICES,
    index=REST_CHOICES.index(DEFAULT_REST_MIN)
)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("😶‍🌫️ 멍때림 시작"):
        reset_mind_anchors()
        start_timer_minutes(st.session_state.rest_min)
        go("pages/3_Mind.py")

with col2:
    if st.button("↩️ 다시 Work 모드로 가기"):
        rem_work = st.session_state.work_remaining_sec
        if rem_work is None:
            start_timer_minutes(st.session_state.work_min)
        else:
            start_timer_seconds(max(0, int(rem_work)))
        go("pages/1_Work.py")

with col3:
    if st.button("⛔ 종료(결과로)"):
        go("pages/5_Results.py")
