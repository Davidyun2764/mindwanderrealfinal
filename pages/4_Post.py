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

st.caption("✅ Easy-MWI는 체크만 하면 자동 계산됩니다. 🔧 정량 MWI는 선택 입력(기존 기능 유지)")

# ---------------------------------------------------------
# ✅ Easy-MWI: 질문1~3 (요청 반영)
# ---------------------------------------------------------
st.markdown("### 🟢 Easy-MWI (체크형 질문 1~3)")

rest_min = int(st.session_state.rest_min)

# Home에서 pre 저장이 없을 수도 있어 안전 처리
if "pre_easy" not in st.session_state:
    st.session_state.pre_easy = {"q1_pre": None}

# 질문1: 5단계(전혀 아니다/아니다/보통이다/꽤 맑아졌다/매우 맑아졌다)
q1_opts = [
    "1. 전혀 아니다",
    "2. 아니다",
    "3. 보통이다",
    "4. 꽤 맑아졌다",
    "5. 매우 맑아졌다"
]
q1_score = {q1_opts[0]: 0, q1_opts[1]: 1, q1_opts[2]: 2, q1_opts[3]: 3, q1_opts[4]: 4}

post_q1_choice = st.radio(
    "질문1) 멍 때린 후, 머리는 얼마나 맑아졌나요?",
    options=q1_opts,
    index=2
)
easy_q1 = q1_score[post_q1_choice]

# 질문2: 4단계(더 힘들다/보통이다/조금 쉬워졌다/매우 쉬워졌다)
q2_opts = [
    "1. 더 힘들다",
    "2. 보통이다",
    "3. 조금 쉬워졌다",
    "4. 매우 쉬워졌다"
]
q2_score = {q2_opts[0]: 0, q2_opts[1]: 1, q2_opts[2]: 2, q2_opts[3]: 3}

post_q2_choice = st.radio(
    "질문2) 멍 때린 후, 다시 집중하는 게 쉬워졌나요?",
    options=q2_opts,
    index=1
)
easy_q2 = q2_score[post_q2_choice]

# 질문3: 4단계(전혀 없음/보통이다/몇 개 떠올랐다/계속 떠올랐다)
q3_opts = [
    "1. 전혀 없음",
    "2. 보통이다",
    "3. 몇 개 떠올랐다",
    "4. 계속 떠올랐다"
]
q3_score = {q3_opts[0]: 0, q3_opts[1]: 1, q3_opts[2]: 2, q3_opts[3]: 3}

post_q3_choice = st.radio(
    "질문3) 멍 때리는 동안 새로운 생각이나 아이디어가 떠올랐나요?",
    options=q3_opts,
    index=1
)
easy_q3 = q3_score[post_q3_choice]

easy_mwi = (easy_q1 + easy_q2 + easy_q3) / max(1, rest_min)
st.success(f"✅ Easy-MWI(분당 효율): **{easy_mwi:.4f}**")

# ---------------------------------------------------------
# ✅ (기존 기능 그대로) 정량 측정 입력
# ---------------------------------------------------------
st.markdown("---")
st.markdown("### 🔧 (선택) 정량 측정 입력(기존 MWI 계산용)")
st.caption("MWI 정량 계산을 위해 휴식 후 값을 입력하세요. (입력 안 해도 Easy-MWI는 저장됩니다)")

c1, c2, c3 = st.columns(3)
with c1:
    post_rt = st.number_input("반응시간(초, 평균)", min_value=0.0, value=0.0, step=0.01)
with c2:
    post_err = st.number_input("오류 개수", min_value=0, value=0, step=1)
with c3:
    post_idea = st.number_input("아이디어 개수", min_value=0, value=0, step=1)

# ---------------------------------------------------------
# ✅ 저장 버튼: 기존 흐름 유지 + Easy-MWI 필드 추가 저장
# ---------------------------------------------------------
if st.button("💾 저장하고 결과 보기"):
    pre = st.session_state.pre_metrics
    pre_rt, pre_err, pre_idea = pre.get("rt"), pre.get("err"), pre.get("idea")
    post_rt_val = None if post_rt <= 0 else float(post_rt)

    stim = st.session_state.chosen_stim
    rec = st.session_state.recommended_stim
    reason = st.session_state.recommend_reason
    work_min = int(st.session_state.work_min)

    # (기존) 정량 MWI 계산
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

    pre_q1 = st.session_state.pre_easy.get("q1_pre", None)

    # ✅ 기존 필드 유지 + Easy-MWI 필드만 추가
    row = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "work_min": work_min,
        "rest_min": rest_min,
        "recommended_stim": rec,
        "recommend_reason": reason,
        "chosen_stim": stim,

        # 기존 정량 필드
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

        # ✅ Easy-MWI 추가 필드(질문1~3 반영)
        "easy_pre_q1": pre_q1,
        "easy_q1": easy_q1,
        "easy_q2": easy_q2,
        "easy_q3": easy_q3,
        "easy_mwi": float(easy_mwi),
    }

    append_log(row)
    st.session_state.last_result = row
    go("pages/5_Results.py")
