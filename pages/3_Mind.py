import streamlit as st
import time
from mindswitch_utils import (
    APP_TITLE, init_state, render_sidebar,
    remaining_seconds, stop_timer,
    start_timer_minutes, start_timer_seconds,
    render_stimulus, go
)

st.set_page_config(page_title=APP_TITLE, layout="centered")
init_state()
render_sidebar()

st.title(APP_TITLE)
st.subheader("😶‍🌫️ Mind-wander 모드")

rem = remaining_seconds()
st.info(f"⏱️ 남은 멍때림 시간: **{rem//60:02d}:{rem%60:02d}**")

# ✅ 버튼을 자극 렌더링보다 먼저 처리 → 페이지 전환이 “확실”
colA, colB, colC = st.columns(3)
with colA:
    end_to_post = st.button("✅ 멍때림 종료(측정으로)")
with colB:
    back_to_work = st.button("↩️ 다시 Work 모드로 가기")
with colC:
    exit_to_results = st.button("⛔ 종료(결과로)")

if end_to_post:
    stop_timer()
    go("pages/4_Post.py")

if back_to_work:
    stop_timer()
    rem_work = st.session_state.work_remaining_sec
    if rem_work is None:
        start_timer_minutes(st.session_state.work_min)
    else:
        start_timer_seconds(max(0, int(rem_work)))
    go("pages/1_Work.py")

if exit_to_results:
    stop_timer()
    go("pages/5_Results.py")

if rem == 0:
    stop_timer()
    go("pages/4_Post.py")

# 버튼 처리 후 자극 렌더링
render_stimulus(st.session_state.chosen_stim, int(st.session_state.rest_min))

time.sleep(1)
st.rerun()
