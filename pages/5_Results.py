import streamlit as st
import numpy as np
from mindswitch_utils import (
    APP_TITLE, init_state, render_sidebar,
    load_log, today_df, STIMULI, go
)

st.set_page_config(page_title=APP_TITLE, layout="centered")
init_state()
render_sidebar()

st.title(APP_TITLE)
st.subheader("📊 오늘 결과")

df_all = load_log()
df_today = today_df(df_all)

last = st.session_state.last_result
if last is not None:
    st.markdown("### ✅ 이번 세션 요약")
    st.write(f"- Work: **{last.get('work_min')}분** / Rest: **{last.get('rest_min')}분**")
    st.write(f"- 추천 자극: **{STIMULI.get(last.get('recommended_stim'), last.get('recommended_stim'))}** ({last.get('recommend_reason')})")
    st.write(f"- 선택 자극: **{STIMULI.get(last.get('chosen_stim'), last.get('chosen_stim'))}**")

    mwi = last.get("mwi", None)
    if mwi is None or (isinstance(mwi, float) and np.isnan(mwi)):
        st.warning("MWI가 계산되지 않았어요(휴식 전/후 측정값이 부족). 그래도 로그/추천 결과는 저장되었습니다.")
    else:
        st.success(f"🧠 MWI: **{float(mwi):.4f}**")
        st.caption("MWI는 ‘휴식 전/후 개선율’을 휴식시간(분)으로 나눈 값(분당 효율)입니다.")

st.markdown("---")
st.markdown("### 🗂️ 오늘 로그")

if df_today.empty:
    st.info("오늘 저장된 로그가 없습니다.")
else:
    show_cols = [
        "ts", "work_min", "rest_min",
        "recommend_reason", "recommended_stim", "chosen_stim",
        "pre_rt", "post_rt", "pre_err", "post_err", "pre_idea", "post_idea", "mwi"
    ]
    show_cols = [c for c in show_cols if c in df_today.columns]
    df_view = df_today[show_cols].copy()

    if "recommended_stim" in df_view.columns:
        df_view["recommended_stim"] = df_view["recommended_stim"].map(lambda x: STIMULI.get(x, x))
    if "chosen_stim" in df_view.columns:
        df_view["chosen_stim"] = df_view["chosen_stim"].map(lambda x: STIMULI.get(x, x))

    st.dataframe(df_view.sort_values("ts", ascending=False), use_container_width=True)

    if "mwi" in df_today.columns and df_today["mwi"].notna().any():
        st.markdown("### 📈 자극별 평균 MWI(오늘)")
        tmp = df_today.copy()
        tmp = tmp[tmp["mwi"].notna()]
        tmp["chosen_name"] = tmp["chosen_stim"].map(lambda x: STIMULI.get(x, x))
        by_stim = tmp.groupby("chosen_name")["mwi"].mean().sort_values(ascending=False)
        st.bar_chart(by_stim)

st.markdown("---")
colA, colB = st.columns(2)
with colA:
    if st.button("🔁 새로 시작(Setup으로)"):
        # 필요한 상태 초기화(기능 유지)
        for k in [
            "running", "timer_start", "timer_total",
            "pre_metrics", "last_result",
            "recommended_stim", "recommend_reason", "chosen_stim",
            "rest_min", "work_remaining_sec",
            "prompt_anchor", "fixed_prompt", "breath_anchor"
        ]:
            if k in st.session_state:
                del st.session_state[k]
        go("Home.py")

with colB:
    if not df_all.empty:
        st.download_button(
            "⬇️ 전체 로그 CSV 다운로드",
            data=df_all.to_csv(index=False).encode("utf-8"),
            file_name="mindwand_log.csv",
            mime="text/csv"
        )
