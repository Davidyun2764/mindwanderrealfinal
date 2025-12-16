import streamlit as st
import pandas as pd
import numpy as np
import time
import os
from datetime import datetime, date

APP_TITLE = "MindSwitch - 멍때림 유도 프로그램"
LOG_PATH = "mindwand_log.csv"

STIMULI = {
    "S1_VisualPulse": "🟦 시각 유도(느린 파동)",
    "S2_AudioNoise": "🌊 청각 유도(화이트노이즈)",
    "S3_BreathGuide": "🫁 호흡 유도(4-4-6)",
    "S4_ThoughtPrompt": "📝 문장 유도(10초마다 변경)"
}

PROMPTS = [
    "지금 떠오르는 생각을 판단하지 말고 그냥 흘려보내세요.",
    "떠오르는 장면 하나를 떠올렸다가, 스쳐가게 두세요.",
    "‘해야 한다’는 생각이 오면 ‘아, 생각이 왔네’ 하고 지나가세요.",
    "지금 눈앞의 색/빛만 가만히 관찰해보세요.",
    "소리 하나를 골라 그 소리만 따라가다 놓아주세요.",
    "지금은 ‘아무 것도 해결하지 않아도 되는 시간’이라고 스스로 허락하세요."
]

DEFAULT_REST_MIN = 3
REST_CHOICES = [1, 2, 3, 4, 5]

EPSILON = 0.20
W_RT = 0.4
W_ERR = 0.4
W_IDEA = 0.2


# ---------------------------
# State init
# ---------------------------
def init_state():
    if "running" not in st.session_state:
        st.session_state.running = False
    if "timer_start" not in st.session_state:
        st.session_state.timer_start = None
    if "timer_total" not in st.session_state:
        st.session_state.timer_total = 0

    if "work_min" not in st.session_state:
        st.session_state.work_min = 25
    if "rest_min" not in st.session_state:
        st.session_state.rest_min = DEFAULT_REST_MIN

    # Work 남은 시간 이어가기
    if "work_remaining_sec" not in st.session_state:
        st.session_state.work_remaining_sec = None

    if "chosen_stim" not in st.session_state:
        st.session_state.chosen_stim = "S1_VisualPulse"
    if "recommended_stim" not in st.session_state:
        st.session_state.recommended_stim = None
    if "recommend_reason" not in st.session_state:
        st.session_state.recommend_reason = None

    if "pre_metrics" not in st.session_state:
        st.session_state.pre_metrics = {"rt": None, "err": None, "idea": None}
    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    # 밴딧 추천 상태(표시 + 학습)
    if "bandit_q" not in st.session_state:
        st.session_state.bandit_q = {k: 0.0 for k in STIMULI.keys()}
    if "bandit_n" not in st.session_state:
        st.session_state.bandit_n = {k: 0 for k in STIMULI.keys()}

    # anchors
    if "prompt_anchor" not in st.session_state:
        st.session_state.prompt_anchor = None
    if "fixed_prompt" not in st.session_state:
        st.session_state.fixed_prompt = None
    if "breath_anchor" not in st.session_state:
        st.session_state.breath_anchor = None


def reset_mind_anchors():
    st.session_state.prompt_anchor = None
    st.session_state.fixed_prompt = None
    st.session_state.breath_anchor = None


# ---------------------------
# Navigation
# ---------------------------
def go(page_path: str):
    """
    page_path 예:
      "pages/1_Work.py"
      "pages/5_Results.py"
      "Home.py"
    """
    st.switch_page(page_path)


# ---------------------------
# Timers
# ---------------------------
def start_timer_seconds(seconds: int):
    st.session_state.timer_start = time.time()
    st.session_state.timer_total = int(seconds)
    st.session_state.running = True

def start_timer_minutes(minutes: int):
    start_timer_seconds(int(minutes * 60))

def remaining_seconds() -> int:
    if not st.session_state.running or st.session_state.timer_start is None:
        return 0
    elapsed = int(time.time() - st.session_state.timer_start)
    return max(0, st.session_state.timer_total - elapsed)

def stop_timer():
    st.session_state.running = False


# ---------------------------
# Bandit recommend
# ---------------------------
def bandit_recommend():
    q = st.session_state.bandit_q
    keys = list(STIMULI.keys())
    if np.random.rand() < EPSILON:
        return str(np.random.choice(keys)), "explore(랜덤 추천)"
    best = max(keys, key=lambda x: q.get(x, 0.0))
    return best, "exploit(학습된 최선 추천)"

def bandit_update(stim_key: str, reward: float):
    n = st.session_state.bandit_n
    q = st.session_state.bandit_q
    n[stim_key] = n.get(stim_key, 0) + 1
    cnt = n[stim_key]
    old = q.get(stim_key, 0.0)
    q[stim_key] = old + (reward - old) / cnt


# ---------------------------
# Logs
# ---------------------------
def load_log():
    if os.path.exists(LOG_PATH):
        try:
            return pd.read_csv(LOG_PATH)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def append_log(row: dict):
    df = load_log()
    df2 = pd.DataFrame([row])
    out = pd.concat([df, df2], ignore_index=True)
    out.to_csv(LOG_PATH, index=False)

def today_df(df: pd.DataFrame):
    if df.empty or "ts" not in df.columns:
        return pd.DataFrame()
    tmp = df.copy()
    tmp["ts_dt"] = pd.to_datetime(tmp["ts"], errors="coerce")
    tmp = tmp[tmp["ts_dt"].dt.date == date.today()]
    return tmp


# ---------------------------
# MWI
# ---------------------------
def safe_div(a, b):
    if b is None or b == 0:
        return 0.0
    return a / b

def compute_mwi(pre_rt, post_rt, pre_err, post_err, pre_idea, post_idea, rest_min):
    d_rt = 0.0
    if pre_rt is not None and post_rt is not None and pre_rt > 0:
        d_rt = (pre_rt - post_rt) / pre_rt

    d_err = 0.0
    if pre_err is not None and post_err is not None:
        d_err = (pre_err - post_err) / max(1, pre_err)

    d_idea = 0.0
    if pre_idea is not None and post_idea is not None:
        d_idea = (post_idea - pre_idea) / max(1, pre_idea)

    core = (W_RT * d_rt) + (W_ERR * d_err) + (W_IDEA * d_idea)
    mwi = safe_div(core, max(1, rest_min))
    return float(mwi), float(d_rt), float(d_err), float(d_idea)


# ---------------------------
# Sidebar
# ---------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("## ⛔ 종료")
        if st.button("프로그램 종료(오늘 결과 보기)"):
            stop_timer()
            go("pages/5_Results.py")

        st.markdown("---")
        st.markdown("## (참고) 추천 학습 상태")
        st.write("Q(평균보상):", st.session_state.bandit_q)
        st.write("N(선택횟수):", st.session_state.bandit_n)


# ---------------------------
# Stimuli
# ---------------------------
@st.cache_data(show_spinner=False)
def make_white_noise_wav(seconds: int, sr: int = 16000, amp: float = 0.12):
    import struct
    n = int(sr * seconds)
    noise = (np.random.randn(n) * amp).clip(-1, 1)
    pcm = (noise * 32767).astype(np.int16).tobytes()

    num_channels = 1
    bits_per_sample = 16
    byte_rate = sr * num_channels * (bits_per_sample // 8)
    block_align = num_channels * (bits_per_sample // 8)
    subchunk2_size = len(pcm)
    chunk_size = 36 + subchunk2_size

    header = b"RIFF" + struct.pack("<I", chunk_size) + b"WAVE"
    fmt = b"fmt " + struct.pack("<IHHIIHH", 16, 1, num_channels, sr, byte_rate, block_align, bits_per_sample)
    data = b"data" + struct.pack("<I", subchunk2_size)
    return header + fmt + data + pcm

def stimulus_visual_pulse():
    st.markdown("### 🟦 시각 유도: 느린 파동")
    st.caption("단순한 움직임만 바라보며 생각을 붙잡지 말고 흘려보내세요.")
    html = """
    <div style="display:flex; justify-content:center; align-items:center; height:240px;">
      <div style="
        width:60px; height:60px;
        border-radius:999px;
        background:#4b86ff;
        animation:pulse 4s ease-in-out infinite;
      "></div>
    </div>
    <style>
      @keyframes pulse {
        0%   { transform: scale(1.0); opacity: 0.55; }
        50%  { transform: scale(3.2); opacity: 0.20; }
        100% { transform: scale(1.0); opacity: 0.55; }
      }
    </style>
    """
    st.components.v1.html(html, height=280)

def stimulus_audio_noise(rest_min: int):
    st.markdown("### 🌊 청각 유도: 화이트노이즈")
    st.caption("멍때림 시간 동안 계속 재생됩니다. (볼륨은 낮게 추천)")
    wav = make_white_noise_wav(seconds=rest_min * 60)
    st.audio(wav, format="audio/wav")

def stimulus_breath_guided_446():
    if st.session_state.breath_anchor is None:
        st.session_state.breath_anchor = time.time()

    t = int(time.time() - st.session_state.breath_anchor)
    phases = [("들이쉬세요", 4), ("멈추세요", 4), ("내쉬세요", 6)]
    cycle = sum(d for _, d in phases)  # 14

    x = t % cycle
    acc = 0
    cur_name, cur_rem = phases[0][0], phases[0][1]
    for name, dur in phases:
        if x < acc + dur:
            cur_name = name
            cur_rem = (acc + dur) - x
            break
        acc += dur

    st.markdown("### 🫁 호흡 유도: 4-4-6 (자동 가이드)")
    st.success(f"## {cur_name}")
    st.markdown(f"### ⏳ {cur_rem}초")
    st.caption("패턴: 4초 들이쉬기 → 4초 멈춤 → 6초 내쉬기 (반복)")

def stimulus_prompt_auto_10s():
    st.markdown("### 📝 문장 유도: 10초마다 자동 변경")

    if st.session_state.prompt_anchor is None:
        st.session_state.prompt_anchor = time.time()
        st.session_state.fixed_prompt = str(np.random.choice(PROMPTS))

    elapsed = int(time.time() - st.session_state.prompt_anchor)

    if elapsed >= 10:
        st.session_state.prompt_anchor = time.time()
        st.session_state.fixed_prompt = str(np.random.choice(PROMPTS))
        elapsed = 0

    remain = 10 - elapsed
    st.markdown(f"## “{st.session_state.fixed_prompt}”")
    st.caption(f"⏳ 다음 문장까지 {remain}초")
    st.info("천천히 한 번 읽고, 떠오르는 생각은 잡지 말고 흘려보내세요.")

def render_stimulus(stim_key: str, rest_min: int):
    if stim_key == "S1_VisualPulse":
        stimulus_visual_pulse()
    elif stim_key == "S2_AudioNoise":
        stimulus_audio_noise(rest_min)
    elif stim_key == "S3_BreathGuide":
        stimulus_breath_guided_446()
    elif stim_key == "S4_ThoughtPrompt":
        stimulus_prompt_auto_10s()
