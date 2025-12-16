import streamlit as st
import time
from mindswitch_utils import (
    APP_TITLE, init_state, render_sidebar,
    remaining_seconds, stop_timer, reset_mind_anchors, go
)

st.set_page_config(page_title=APP_TITLE, layout="centered")
init_state()
render_sidebar()

st.title(APP_TITLE)
st.subheader("🧩 Work 모드")

rem = remaining_seconds()
st.info(f"⏱️ 남은 작업 시간: **{rem//60:02d}:{rem%60:02d}**")

colA, colB, colC = st.columns(3)
with colA:
    if st.button("😶‍🌫️ 지금 멍때리기(바로 전환)"):
        st.session_state.work_remaining_sec = rem
        stop_timer()
        reset_mind_anchors()
        go("pages/2_Choose.py")
with colB:
    if st.button("⏹️ 작업 종료(결과로)"):
        stop_timer()
        go("pages/5_Results.py")
with colC:
    if st.button("🔄 새로고침"):
        st.rerun()

if rem == 0:
    st.session_state.work_remaining_sec = 0
    stop_timer()
    reset_mind_anchors()
    go("pages/2_Choose.py")

time.sleep(1)
st.rerun()
