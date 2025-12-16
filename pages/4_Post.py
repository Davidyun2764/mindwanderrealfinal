import streamlit as st
from datetime import datetime
import numpy as np
from mindswitch_utils import (
    APP_TITLE, init_state, render_sidebar,
    compute_mwi, bandit_update,
    append_log, go
)

st.set_page_config(page_title=APP_TITLE, layout="centered")
init_state()
render_sidebar()

st.title(APP_TITLE)
st.subheader("📏 멍때림 후 측정 & 저장")

st.caption("MWI 계산을 위해 휴식 후 값을 입력하세요. (입력 안 해도 로그/추천은 저장 가능)")

c1, c2, c3 = st.columns(3)
with c1:
    post_rt = st.number_input("반응시간(초, 평균)", min_value=0.0, value=0.0, step=0.01)
with c2:
    post_err = st.number_input("오류 개수", min_value=0, value=0, step=1)
with c3:
    post_idea = st.number_input("아이디어 개수", min_value=0, value=0, step=1)

if st.button("💾 저장하고 결과 보기"):
    pre = st.session_state.pre_metrics
    pre_rt, pre_err, pre_idea = pre.get("rt"), pre.get("err"), pre.get("idea")
    post_rt_val = None if post_rt <= 0 else float(post_rt)

    stim = st.session_state.chosen_stim
    rec = st.session_state.recommended_stim
    reason = st.session_state.recommend_reason
    work_min = int(st.session_state.work_min)
    rest_min = int(st.session_state.rest_min)

    mwi = None
    d_rt = d_err = d_idea = None

    if (pre_rt is not None and post_rt_val is not None) or (pre_err is not None) or (pre_idea is not None):
        mwi_val, d_rt, d_err, d_idea = compute_mwi(
            pre_rt, post_rt_val,
            pre_err, int(post_err),
            pre_idea, int(post_idea),
            rest_min
        )
        mwi = mwi_val
        if mwi is not None and not np.isnan(mwi):
            bandit_update(stim, mwi_val)

    row = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "work_min": work_min,
        "rest_min": rest_min,
        "recommended_stim": rec,
        "recommend_reason": reason,
        "chosen_stim": stim,
        "pre_rt": pre_rt,
        "post_rt": post_rt_val,
        "pre_err": pre_err,
        "post_err": int(post_err),
        "pre_idea": pre_idea,
        "post_idea": int(post_idea),
        "d_rt": d_rt,
        "d_err": d_err,
        "d_idea": d_idea,
        "mwi": mwi,
    }
    append_log(row)
    st.session_state.last_result = row
    go("pages/5_Results.py")
