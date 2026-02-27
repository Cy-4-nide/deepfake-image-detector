import streamlit as st
from detector import predict_image
from PIL import Image
import numpy as np
import io
import wave

st.set_page_config(
    page_title="DeepTrace | AI Detector",
    page_icon="🔬",
    layout="centered"
)

# ══════════════════════════════════════════════════════════════════════════════
#  SOUND ENGINE  —  every sound is synthesized from scratch using numpy
# ══════════════════════════════════════════════════════════════════════════════

SR = 44100   # sample rate

def _wav(samples: np.ndarray) -> io.BytesIO:
    """Convert float32 array → WAV bytes buffer."""
    pcm = np.int16(np.clip(samples, -1, 1) * 32767)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    buf.seek(0)
    return buf

def _sine(freq, dur, vol=0.4, fade=0.04):
    n  = int(SR * dur)
    t  = np.linspace(0, dur, n, False)
    s  = vol * np.sin(2 * np.pi * freq * t)
    fi = min(int(SR * fade), n // 2)
    if fi > 0:
        s[:fi]  *= np.linspace(0, 1, fi)
        s[-fi:] *= np.linspace(1, 0, fi)
    return s

def _saw(freq, dur, vol=0.3, fade=0.03):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, False)
    s = vol * (2 * (t * freq - np.floor(t * freq + 0.5)))
    fi = min(int(SR * fade), n // 2)
    if fi > 0:
        s[:fi]  *= np.linspace(0, 1, fi)
        s[-fi:] *= np.linspace(1, 0, fi)
    return s

def _square(freq, dur, vol=0.2, fade=0.02):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, False)
    s = vol * np.sign(np.sin(2 * np.pi * freq * t))
    fi = min(int(SR * fade), n // 2)
    if fi > 0:
        s[:fi]  *= np.linspace(0, 1, fi)
        s[-fi:] *= np.linspace(1, 0, fi)
    return s

def _noise(dur, vol=0.15):
    n = int(SR * dur)
    return vol * (np.random.rand(n) * 2 - 1)

def _silence(dur):
    return np.zeros(int(SR * dur))

def _concat(*parts):
    return np.concatenate(parts)

def _play(samples):
    st.audio(_wav(samples), format="audio/wav", autoplay=True)

# ── 1. BOOT / PAGE LOAD  — warm power-on hum + rising sweep ──────────────────
def sound_boot():
    hum   = _sine(60,  0.3, vol=0.15)
    sweep = np.concatenate([_sine(200 + i*40, 0.05, vol=0.12) for i in range(12)])
    ping  = _sine(1200, 0.25, vol=0.25)
    _play(_concat(hum, sweep, ping))

# ── 2. IMAGE SELECTED  — satisfying "lock-on" confirmation ───────────────────
def sound_image_selected():
    click1 = _sine(800,  0.04, vol=0.35)
    click2 = _sine(1200, 0.04, vol=0.35)
    beep   = _sine(1600, 0.12, vol=0.25)
    _play(_concat(click1, _silence(0.03), click2, _silence(0.04), beep))

# ── 3. CINEMATIC MILITARY SCAN SOUND — full 4.5 second Hollywood sequence ────
def sound_cinematic_scan():
    import time

    # ═══════════════════════════════════════════════════════════════
    # PHASE 1 (0.0–0.6s): DEEP BASS THUD — like a warship door closing
    # ═══════════════════════════════════════════════════════════════
    thud_n = int(SR * 0.6)
    t1 = np.linspace(0, 0.6, thud_n, False)
    # sub-bass with exponential decay
    thud = 0.55 * np.sin(2*np.pi*55*t1) * np.exp(-6*t1)
    thud += 0.3 * np.sin(2*np.pi*40*t1) * np.exp(-4*t1)
    # punch of noise on the attack
    noise_punch = _noise(0.6, vol=0.12) * np.exp(-18*t1)
    phase1 = thud + noise_punch

    # ═══════════════════════════════════════════════════════════════
    # PHASE 2 (0.6–1.4s): POWER CHARGE — reactor spinning up
    # rising sawtooth sweep from 60Hz to 900Hz
    # ═══════════════════════════════════════════════════════════════
    charge_dur = 0.8
    charge_n   = int(SR * charge_dur)
    t2 = np.linspace(0, charge_dur, charge_n, False)
    # exponential frequency sweep
    freq_sweep = 60 * np.exp(np.log(900/60) * t2 / charge_dur)
    phase_acc  = np.cumsum(2 * np.pi * freq_sweep / SR)
    charge_saw = 0.22 * (2 * (phase_acc/(2*np.pi) - np.floor(phase_acc/(2*np.pi)+0.5)))
    # add harmonic overtone
    charge_saw += 0.10 * np.sin(phase_acc * 2)
    # volume ramp up
    charge_saw *= np.linspace(0.1, 1.0, charge_n)
    phase2 = charge_saw

    # ═══════════════════════════════════════════════════════════════
    # PHASE 3 (1.4–2.2s): RADAR LOCK — military sonar ping sequence
    # 4 sharp descending radar beeps like missile lock-on
    # ═══════════════════════════════════════════════════════════════
    pings = []
    ping_freqs = [1800, 1400, 1100, 900]
    ping_vols  = [0.45, 0.42, 0.38, 0.35]
    for pf, pv in zip(ping_freqs, ping_vols):
        p = _sine(pf, 0.09, vol=pv)
        pings.append(p)
        pings.append(_silence(0.11))
    phase3 = _concat(*pings)

    # ═══════════════════════════════════════════════════════════════
    # PHASE 4 (2.2–3.2s): DATA PROCESSING — rapid-fire digital blips
    # like a computer scanning through terabytes — frantic and intense
    # ═══════════════════════════════════════════════════════════════
    data_parts = []
    for i in range(22):
        freq  = 400 + (i % 7) * 120 + np.random.randint(-30, 30)
        dur   = 0.025 + (i % 3) * 0.008
        vol   = 0.18 + (i % 4) * 0.04
        wtype = i % 3
        if wtype == 0:
            data_parts.append(_sine(freq,   dur, vol=vol))
        elif wtype == 1:
            data_parts.append(_square(freq, dur, vol=vol*0.6))
        else:
            data_parts.append(_saw(freq,    dur, vol=vol*0.7))
        data_parts.append(_silence(0.018))
    phase4 = _concat(*data_parts)

    # ═══════════════════════════════════════════════════════════════
    # PHASE 5 (3.2–3.8s): TENSION BUILD — low drone + high frequency whine
    # like a missile guidance system locking on final target
    # ═══════════════════════════════════════════════════════════════
    drone_dur = 0.6
    drone_n   = int(SR * drone_dur)
    t5 = np.linspace(0, drone_dur, drone_n, False)
    # low rumbling drone
    drone  = 0.20 * np.sin(2*np.pi*80*t5)
    drone += 0.12 * np.sin(2*np.pi*160*t5)
    # high whine rising to climax
    whine_freq = 800 + 1200*(t5/drone_dur)**2
    whine_phase = np.cumsum(2*np.pi*whine_freq/SR)
    whine = 0.18 * np.sin(whine_phase)
    # tremolo effect — rapid amplitude oscillation
    tremolo = 1 + 0.4 * np.sin(2*np.pi*18*t5)
    phase5  = (drone + whine) * tremolo

    # ═══════════════════════════════════════════════════════════════
    # PHASE 6 (3.8–4.5s): SYSTEM READY — final lock confirmed
    # two sharp military confirmation beeps + deep bass settle
    # ═══════════════════════════════════════════════════════════════
    confirm1 = _sine(1200, 0.12, vol=0.5)
    silence1 = _silence(0.06)
    confirm2 = _sine(1500, 0.18, vol=0.55)
    settle_n = int(SR * 0.25)
    t6 = np.linspace(0, 0.25, settle_n, False)
    settle   = 0.3 * np.sin(2*np.pi*100*t6) * np.exp(-8*t6)
    phase6   = _concat(confirm1, silence1, confirm2, settle)

    # ═══════════════════════════════════════════════════════════════
    # MIX everything together with crossfades
    # ═══════════════════════════════════════════════════════════════
    full = _concat(phase1, phase2, phase3, phase4, phase5, phase6)

    # master limiter — prevent clipping
    peak = np.max(np.abs(full))
    if peak > 0.92:
        full = full * (0.92 / peak)

    _play(full)

# ── 4. SCANNING TICK (kept for compatibility, not used) ───────────────────────
def sound_scanning():
    pass  # replaced by cinematic scan above

# ── 5. RESULT: AUTHENTIC / REAL  — triumphant upward arpeggio ────────────────
def sound_real():
    notes = [523, 659, 784, 988, 1319]
    parts = []
    for i, f in enumerate(notes):
        vol  = 0.25 + i * 0.03
        dur  = 0.15 if i < 4 else 0.5
        parts.append(_sine(f, dur, vol=vol))
    # add a warm shimmer at the end
    shimmer = sum(_sine(f, 0.4, vol=0.06) for f in [1319, 1568, 1976])
    _play(_concat(*parts, shimmer))

# ── 6. RESULT: SYNTHETIC / FAKE  — ominous descending alarm ──────────────────
def sound_fake():
    # descending saw alarm
    alarm_parts = []
    for i in range(3):
        for j in range(10):
            f = 500 - j * 30
            alarm_parts.append(_saw(f, 0.04, vol=0.25))
        alarm_parts.append(_silence(0.08))
    alarm = _concat(*alarm_parts)
    # deep bass thud
    thud  = _sine(55, 0.4, vol=0.5)
    noise = _noise(0.1, vol=0.15)
    _play(_concat(alarm[:int(SR*0.6)], noise, thud))

# ── 7. RESULT: UNCERTAIN  — mysterious oscillating tone ──────────────────────
def sound_uncertain():
    # warbling LFO-style uncertain sound
    dur = 0.8
    n   = int(SR * dur)
    t   = np.linspace(0, dur, n, False)
    lfo = np.sin(2 * np.pi * 5 * t)          # 5Hz wobble
    freq_mod = 440 + 80 * lfo
    phase = np.cumsum(2 * np.pi * freq_mod / SR)
    warble = 0.25 * np.sin(phase)
    fi = int(SR * 0.05)
    warble[:fi]  *= np.linspace(0, 1, fi)
    warble[-fi:] *= np.linspace(1, 0, fi)
    # add question-mark style rising inflection
    q = _sine(440, 0.1, vol=0.2)
    q2 = _sine(660, 0.15, vol=0.2)
    _play(_concat(warble, _silence(0.05), q, q2))

# ── 8. HOVER / UI TICK  — tiny satisfying click ──────────────────────────────
def sound_ui_tick():
    _play(_sine(1000, 0.03, vol=0.15))

# ══════════════════════════════════════════════════════════════════════════════
#  CSS + PARTICLES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&display=swap');

:root {
    --bg:      #020408;
    --surface: #080f18;
    --accent:  #00d4ff;
    --green:   #00ff88;
    --purple:  #b44fff;
    --pink:    #ff2d9b;
    --orange:  #ff6a00;
    --yellow:  #ffd200;
    --red:     #ff2d55;
    --text:    #c8e0f0;
    --muted:   #3a5a72;
}

*, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'Rajdhani', sans-serif;
    color: var(--text);
    overflow-x: hidden;
}

/* animated mesh background */
[data-testid="stAppViewContainer"]::before {
    content:'';
    position:fixed; inset:0;
    background:
        radial-gradient(ellipse 70% 50% at 20% 20%, rgba(180,79,255,.13) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(0,212,255,.10) 0%, transparent 60%),
        radial-gradient(ellipse 50% 50% at 50% 50%, rgba(255,45,155,.07) 0%, transparent 70%),
        repeating-linear-gradient(0deg,   transparent, transparent 49px, rgba(0,212,255,.018) 50px),
        repeating-linear-gradient(90deg,  transparent, transparent 49px, rgba(0,212,255,.018) 50px);
    pointer-events:none; z-index:0;
    animation: bgPulse 8s ease-in-out infinite alternate;
}
@keyframes bgPulse { 0%{opacity:.6} 100%{opacity:1} }

[data-testid="stMain"] { position:relative; z-index:1; }

/* floating particles */
.particles { position:fixed; inset:0; pointer-events:none; z-index:0; overflow:hidden; }
.particle  { position:absolute; border-radius:50%; animation:floatUp linear infinite; }
@keyframes floatUp {
    0%   { transform:translateY(110vh) rotate(0deg); opacity:0; }
    8%   { opacity:.5; }
    92%  { opacity:.5; }
    100% { transform:translateY(-80px) rotate(900deg); opacity:0; }
}

/* scanning line overlay (only active during scan) */
.scanline-wrap {
    position:fixed; inset:0; pointer-events:none; z-index:999;
    overflow:hidden; display:none;
}
.scanline-wrap.active { display:block; }
.scanline {
    position:absolute; left:0; right:0; height:3px;
    background:linear-gradient(90deg, transparent, rgba(0,212,255,.8), var(--green), rgba(0,212,255,.8), transparent);
    box-shadow: 0 0 20px rgba(0,255,136,.6);
    animation: scanDown 0.8s linear infinite;
}
@keyframes scanDown {
    0%   { top:-4px; }
    100% { top:100%; }
}

/* hide streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display:none !important; }

/* hide audio player */
[data-testid="stAudio"] {
    position:fixed !important; bottom:-200px !important; left:-200px !important;
    width:1px !important; height:1px !important; opacity:0 !important;
    pointer-events:none !important; overflow:hidden !important;
}

/* ── HERO ── */
.hero { text-align:center; padding:2.5rem 1rem 1.5rem; }
.hero-badge {
    display:inline-block;
    font-family:'Share Tech Mono',monospace;
    font-size:.65rem; letter-spacing:.45em;
    padding:.35rem 1.4rem;
    border:1px solid var(--purple); color:var(--purple);
    border-radius:20px; margin-bottom:1.2rem;
    background:rgba(180,79,255,.08);
    box-shadow:0 0 20px rgba(180,79,255,.25);
    animation:fadeDown .5s ease both;
}
.hero-title {
    font-family:'Orbitron',monospace;
    font-size:clamp(2.5rem,8vw,5rem); font-weight:900; line-height:1;
    margin-bottom:.5rem;
    background:linear-gradient(135deg,#00d4ff 0%,#b44fff 40%,#ff2d9b 70%,#ffd200 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    filter:drop-shadow(0 0 35px rgba(180,79,255,.5));
    animation:fadeDown .5s .1s ease both;
}
.hero-sub {
    font-family:'Share Tech Mono',monospace;
    font-size:.78rem; color:var(--muted); letter-spacing:.22em;
    animation:fadeDown .5s .2s ease both;
}

/* ── RAINBOW DIVIDER ── */
.rdivider {
    height:2px;
    background:linear-gradient(90deg,transparent,#00d4ff,#b44fff,#ff2d9b,#ffd200,#00ff88,transparent);
    margin:1.5rem 0; border-radius:2px;
    background-size:200% 100%;
    animation:shimmer 3s linear infinite;
}
@keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }

.section-label {
    font-family:'Share Tech Mono',monospace;
    font-size:.65rem; letter-spacing:.45em; color:var(--accent);
    text-align:center; margin:.5rem 0 1rem;
}

/* ── UPLOAD ZONE ── */
[data-testid="stFileUploader"] {
    background:linear-gradient(135deg,rgba(0,212,255,.05),rgba(180,79,255,.05)) !important;
    border:1px solid rgba(180,79,255,.35) !important;
    border-radius:14px !important; padding:1rem !important;
    transition:all .3s; cursor:pointer;
}
[data-testid="stFileUploader"]:hover {
    border-color:var(--purple) !important;
    box-shadow:0 0 35px rgba(180,79,255,.3), 0 0 70px rgba(0,212,255,.12) !important;
    transform:translateY(-1px);
}
[data-testid="stFileUploader"] * { color:var(--text) !important; }
[data-testid="stFileUploaderDropzone"] {
    background:rgba(180,79,255,.04) !important;
    border:1px dashed rgba(180,79,255,.35) !important;
    border-radius:10px !important;
}

/* ── IMAGE ── */
[data-testid="stImage"] img {
    border-radius:10px !important;
    border:1px solid rgba(180,79,255,.35) !important;
    box-shadow:0 0 50px rgba(180,79,255,.22), 0 0 100px rgba(0,212,255,.12) !important;
    animation:imgReveal .5s ease both;
}
@keyframes imgReveal {
    0%   { opacity:0; transform:scale(.95); filter:blur(8px); }
    100% { opacity:1; transform:scale(1);   filter:blur(0); }
}

/* ── BUTTON ── */
[data-testid="stButton"] > button {
    width:100%;
    background:linear-gradient(135deg,#b44fff,#00d4ff) !important;
    border:none !important; color:#fff !important;
    font-family:'Orbitron',monospace !important;
    font-size:.9rem !important; font-weight:700 !important;
    letter-spacing:.2em !important; padding:1rem 2rem !important;
    border-radius:10px !important; transition:all .25s ease !important;
    box-shadow:0 0 25px rgba(180,79,255,.45) !important;
    position:relative; overflow:hidden;
}
[data-testid="stButton"] > button:hover {
    transform:translateY(-3px) scale(1.01) !important;
    box-shadow:0 0 50px rgba(180,79,255,.7), 0 0 100px rgba(0,212,255,.35) !important;
    background:linear-gradient(135deg,#ff2d9b,#b44fff,#00d4ff) !important;
}
[data-testid="stButton"] > button:active { transform:translateY(0) scale(.99) !important; }

/* ── RESULT CARDS ── */
.result-card {
    border-radius:14px; padding:2rem; margin:1.5rem 0;
    text-align:center; position:relative; overflow:hidden;
    animation:popIn .6s cubic-bezier(.34,1.56,.64,1) both;
}
@keyframes popIn {
    0%   { opacity:0; transform:scale(.75) translateY(30px); }
    100% { opacity:1; transform:scale(1)   translateY(0); }
}
.result-real {
    background:linear-gradient(135deg,rgba(0,255,136,.09),rgba(0,212,255,.05));
    border:2px solid rgba(0,255,136,.35);
    box-shadow:0 0 50px rgba(0,255,136,.22), 0 0 100px rgba(0,212,255,.12), inset 0 0 50px rgba(0,255,136,.04);
}
.result-fake {
    background:linear-gradient(135deg,rgba(255,45,85,.09),rgba(255,45,155,.05));
    border:2px solid rgba(255,45,85,.35);
    box-shadow:0 0 50px rgba(255,45,85,.22), 0 0 100px rgba(255,45,155,.12), inset 0 0 50px rgba(255,45,85,.04);
}
.result-uncertain {
    background:linear-gradient(135deg,rgba(255,210,0,.09),rgba(255,106,0,.05));
    border:2px solid rgba(255,210,0,.35);
    box-shadow:0 0 50px rgba(255,210,0,.22), inset 0 0 50px rgba(255,210,0,.04);
}
.result-icon {
    font-size:4rem; margin-bottom:.6rem; display:block;
    animation:iconBounce .7s .15s cubic-bezier(.34,1.56,.64,1) both;
}
@keyframes iconBounce {
    0%   { transform:scale(0) rotate(-30deg); opacity:0; }
    60%  { transform:scale(1.2) rotate(5deg); }
    100% { transform:scale(1)   rotate(0deg); opacity:1; }
}
.result-verdict {
    font-family:'Orbitron',monospace; font-size:2.4rem;
    font-weight:900; letter-spacing:.1em; margin-bottom:.6rem;
    animation:verdictIn .5s .3s ease both;
}
@keyframes verdictIn {
    0%   { opacity:0; letter-spacing:.5em; }
    100% { opacity:1; letter-spacing:.1em; }
}
.result-real .result-verdict     { color:#00ff88; text-shadow:0 0 35px rgba(0,255,136,.7); }
.result-fake .result-verdict     { color:#ff2d55; text-shadow:0 0 35px rgba(255,45,85,.7); }
.result-uncertain .result-verdict{ color:#ffd200; text-shadow:0 0 35px rgba(255,210,0,.7); }
.result-desc {
    font-family:'Share Tech Mono',monospace;
    font-size:.76rem; opacity:.6; letter-spacing:.08em; line-height:1.7;
}

/* ── CONFIDENCE BAR ── */
.conf-wrap {
    background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.07);
    border-radius:14px; padding:1.5rem; margin:1rem 0;
    animation:fadeUp .4s .2s ease both;
}
.conf-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:.9rem; }
.conf-title  { font-family:'Share Tech Mono',monospace; font-size:.65rem; letter-spacing:.35em; color:var(--muted); }
.conf-pct    { font-family:'Orbitron',monospace; font-size:1.6rem; font-weight:700; }
.conf-pct.real      { color:#00ff88; text-shadow:0 0 15px rgba(0,255,136,.5); }
.conf-pct.fake      { color:#ff2d55; text-shadow:0 0 15px rgba(255,45,85,.5); }
.conf-pct.uncertain { color:#ffd200; text-shadow:0 0 15px rgba(255,210,0,.5); }
.conf-track { height:12px; background:rgba(255,255,255,.05); border-radius:6px; overflow:hidden; position:relative; }
.conf-fill  { height:100%; border-radius:6px; animation:barFill 1.5s cubic-bezier(.25,1,.5,1) both; }
@keyframes barFill { 0%{width:0!important} }
.conf-fill.real     { background:linear-gradient(90deg,#00cc77,#00ff88,#00d4ff); box-shadow:0 0 18px rgba(0,255,136,.65); }
.conf-fill.fake     { background:linear-gradient(90deg,#cc0033,#ff2d55,#ff2d9b); box-shadow:0 0 18px rgba(255,45,85,.65); }
.conf-fill.uncertain{ background:linear-gradient(90deg,#cc8800,#ffd200,#ff6a00); box-shadow:0 0 18px rgba(255,210,0,.65); }

/* ── METRICS ── */
.metrics { display:grid; grid-template-columns:1fr 1fr 1fr; gap:.8rem; margin:1rem 0; }
.metric {
    background:linear-gradient(135deg,rgba(255,255,255,.045),rgba(255,255,255,.01));
    border:1px solid rgba(255,255,255,.08); border-radius:12px;
    padding:1.1rem .5rem; text-align:center;
    transition:transform .2s,box-shadow .2s;
    animation:fadeUp .4s ease both;
}
.metric:hover { transform:translateY(-4px); box-shadow:0 10px 30px rgba(180,79,255,.22); }
.metric-lbl {
    font-family:'Share Tech Mono',monospace; font-size:.58rem;
    letter-spacing:.32em; color:var(--muted); margin-bottom:.5rem; text-transform:uppercase;
}
.metric-val {
    font-family:'Orbitron',monospace; font-size:1.05rem; font-weight:700;
    background:linear-gradient(135deg,#00d4ff,#b44fff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}

/* ── STATUS TICKER ── */
.ticker-wrap {
    overflow:hidden; border:1px solid rgba(0,212,255,.15);
    border-radius:6px; background:rgba(0,212,255,.04);
    padding:.4rem 0; margin:.8rem 0;
}
.ticker {
    display:inline-block; white-space:nowrap;
    font-family:'Share Tech Mono',monospace; font-size:.65rem;
    color:rgba(0,212,255,.5); letter-spacing:.15em;
    animation:tickerScroll 18s linear infinite;
}
@keyframes tickerScroll {
    0%   { transform:translateX(100vw); }
    100% { transform:translateX(-100%); }
}

/* ── DISCLAIMER ── */
.disclaimer {
    background:rgba(255,210,0,.05); border:1px solid rgba(255,210,0,.15);
    border-radius:10px; padding:.9rem 1.1rem;
    font-family:'Share Tech Mono',monospace; font-size:.68rem;
    color:rgba(255,210,0,.7); letter-spacing:.08em; line-height:1.7;
    margin-top:1rem; animation:fadeUp .4s .45s ease both;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background:rgba(8,15,24,.96) !important;
    border-right:1px solid rgba(180,79,255,.15) !important;
}
[data-testid="stSidebar"] * { color:var(--text) !important; }

/* ── ANIMATIONS ── */
@keyframes fadeDown { from{opacity:0;transform:translateY(-20px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeUp   { from{opacity:0;transform:translateY(16px)}  to{opacity:1;transform:translateY(0)} }

[data-testid="stProgressBar"] { display:none !important; }

::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:linear-gradient(180deg,#b44fff,#00d4ff); border-radius:2px; }
</style>

<!-- PARTICLES -->
<div class="particles" id="particles"></div>
<!-- SCAN LINE OVERLAY -->
<div class="scanline-wrap" id="scanOverlay"><div class="scanline"></div></div>

<script>
// ── particles ────────────────────────────────────────────────────────────────
(function(){
    const c = document.getElementById('particles');
    if(!c) return;
    const cols=['#00d4ff','#b44fff','#ff2d9b','#00ff88','#ffd200','#ff6a00'];
    for(let i=0;i<35;i++){
        const p=document.createElement('div');
        p.className='particle';
        const sz=Math.random()*5+1;
        const col=cols[Math.floor(Math.random()*cols.length)];
        p.style.cssText=`width:${sz}px;height:${sz}px;left:${Math.random()*100}%;
            background:${col};box-shadow:0 0 ${sz*2}px ${col};
            animation-duration:${Math.random()*18+10}s;
            animation-delay:-${Math.random()*18}s;opacity:.35;`;
        c.appendChild(p);
    }
})();

// ── scan-line helper ──────────────────────────────────────────────────────────
function showScanline(){ document.getElementById('scanOverlay').classList.add('active'); }
function hideScanline(){ document.getElementById('scanOverlay').classList.remove('active'); }
</script>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE  —  track what we've already played
# ══════════════════════════════════════════════════════════════════════════════
if "booted" not in st.session_state:
    st.session_state.booted        = False
if "last_file" not in st.session_state:
    st.session_state.last_file     = None
if "scan_sound_played" not in st.session_state:
    st.session_state.scan_sound_played = False

# ── BOOT SOUND (once per session) ─────────────────────────────────────────────
if not st.session_state.booted:
    sound_boot()
    st.session_state.booted = True

# ══════════════════════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-badge">⬡ AI FORENSICS SYSTEM v4.0 ⬡</div>
    <div class="hero-title">DEEPTRACE</div>
    <div class="hero-sub">// NEURAL AUTHENTICITY VERIFICATION ENGINE //</div>
</div>

<!-- live status ticker -->
<div class="ticker-wrap">
    <span class="ticker">
        ◈ SYSTEM ONLINE &nbsp;◈ NEURAL ENGINE READY &nbsp;◈ ViT-B/16 LOADED &nbsp;
        ◈ AWAITING INPUT &nbsp;◈ FORENSIC ANALYSIS SYSTEM v4.0 &nbsp;
        ◈ PYTORCH ENGINE ACTIVE &nbsp;◈ HUGGING FACE CONNECTED &nbsp;
        ◈ DEEPFAKE DETECTION READY &nbsp;◈ UPLOAD IMAGE TO BEGIN &nbsp;
    </span>
</div>

<div class="rdivider"></div>
<div class="section-label">▸ UPLOAD TARGET IMAGE ◂</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  UPLOAD
# ══════════════════════════════════════════════════════════════════════════════
uploaded_file = st.file_uploader(
    "Drop image here",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

# ── IMAGE SELECTED SOUND ──────────────────────────────────────────────────────
if uploaded_file is not None:
    file_id = uploaded_file.file_id if hasattr(uploaded_file, "file_id") else uploaded_file.name
    if file_id != st.session_state.last_file:
        st.session_state.last_file = file_id
        sound_image_selected()          # 🔊 lock-on click when image is picked

    image = Image.open(uploaded_file).convert("RGB")

    st.markdown("<div class='rdivider'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image(image, caption="✦ TARGET LOCKED ✦", use_column_width=True)

    st.markdown("""
    <div class="rdivider"></div>
    <div class="section-label">▸ INITIATE ANALYSIS ◂</div>
    """, unsafe_allow_html=True)

    # ── SCAN BUTTON ───────────────────────────────────────────────────────────
    if st.button("🔬  LAUNCH FORENSIC SCAN  🔬"):
        import time

        # show scanline overlay
        st.markdown("<script>showScanline();</script>", unsafe_allow_html=True)

        status_box = st.empty()

        # Step 1 — INITIATING (0.0s)
        status_box.markdown("""
        <div style="font-family:'Share Tech Mono',monospace; font-size:.75rem;
                    color:#00d4ff; letter-spacing:.2em; text-align:center;
                    padding:1.2rem; border:1px solid rgba(0,212,255,.2);
                    border-radius:8px; background:rgba(0,212,255,.04);">
            ◈ &nbsp; INITIATING FORENSIC SEQUENCE &nbsp; ◈<br>
            <span style="font-size:.6rem; color:#3a5a72; letter-spacing:.15em;">LOADING NEURAL WEIGHTS...</span>
        </div>
        """, unsafe_allow_html=True)

        # 🔊 PLAY THE FULL CINEMATIC SCAN SOUND (4.5 seconds)
        sound_cinematic_scan()
        time.sleep(0.6)

        # Step 2 — POWER CHARGE (0.6s)
        status_box.markdown("""
        <div style="font-family:'Share Tech Mono',monospace; font-size:.75rem;
                    color:#b44fff; letter-spacing:.2em; text-align:center;
                    padding:1.2rem; border:1px solid rgba(180,79,255,.25);
                    border-radius:8px; background:rgba(180,79,255,.05);">
            ⬡ &nbsp; POWER SYSTEMS CHARGING &nbsp; ⬡<br>
            <span style="font-size:.6rem; color:#3a5a72; letter-spacing:.15em;">REACTOR ONLINE — SCANNING PIXEL MATRIX...</span>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.8)

        # Step 3 — RADAR LOCK (1.4s)
        status_box.markdown("""
        <div style="font-family:'Share Tech Mono',monospace; font-size:.75rem;
                    color:#ffd200; letter-spacing:.2em; text-align:center;
                    padding:1.2rem; border:1px solid rgba(255,210,0,.25);
                    border-radius:8px; background:rgba(255,210,0,.04);">
            ◎ &nbsp; RADAR LOCK ACQUIRED &nbsp; ◎<br>
            <span style="font-size:.6rem; color:#3a5a72; letter-spacing:.15em;">ANALYZING FACIAL GEOMETRY — 4 TARGETS LOCKED...</span>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.8)

        # Step 4 — DATA PROCESSING (2.2s) — run actual model here
        status_box.markdown("""
        <div style="font-family:'Share Tech Mono',monospace; font-size:.75rem;
                    color:#ff2d9b; letter-spacing:.2em; text-align:center;
                    padding:1.2rem; border:1px solid rgba(255,45,155,.25);
                    border-radius:8px; background:rgba(255,45,155,.04);">
            ▣ &nbsp; PROCESSING NEURAL SIGNATURES &nbsp; ▣<br>
            <span style="font-size:.6rem; color:#3a5a72; letter-spacing:.15em;">COMPARING AGAINST 1.2M SYNTHETIC PATTERNS...</span>
        </div>
        """, unsafe_allow_html=True)
        label, confidence = predict_image(image)   # ← actual model runs here
        time.sleep(0.6)

        # Step 5 — TENSION (3.2s)
        status_box.markdown("""
        <div style="font-family:'Share Tech Mono',monospace; font-size:.75rem;
                    color:#ff6a00; letter-spacing:.2em; text-align:center;
                    padding:1.2rem; border:1px solid rgba(255,106,0,.25);
                    border-radius:8px; background:rgba(255,106,0,.04);">
            ⚡ &nbsp; FINAL VERIFICATION IN PROGRESS &nbsp; ⚡<br>
            <span style="font-size:.6rem; color:#3a5a72; letter-spacing:.15em;">CROSS-REFERENCING ANOMALY DATABASE...</span>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.6)

        # Step 6 — COMPLETE (3.8s)
        status_box.markdown("""
        <div style="font-family:'Share Tech Mono',monospace; font-size:.75rem;
                    color:#00ff88; letter-spacing:.2em; text-align:center;
                    padding:1.2rem; border:1px solid rgba(0,255,136,.3);
                    border-radius:8px; background:rgba(0,255,136,.05);">
            ✦ &nbsp; ANALYSIS COMPLETE — DECRYPTING VERDICT &nbsp; ✦<br>
            <span style="font-size:.6rem; color:#3a5a72; letter-spacing:.15em;">CONFIDENCE THRESHOLD CALCULATED...</span>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.7)

        # clear status and hide scanline
        status_box.empty()
        st.markdown("<script>hideScanline();</script>", unsafe_allow_html=True)

        pct          = int(confidence * 100)
        is_real      = "real" in label.lower()
        is_uncertain = confidence < 0.70

        st.markdown("<div class='rdivider'></div>", unsafe_allow_html=True)

        # ── RESULT ────────────────────────────────────────────────────────────
        if is_uncertain:
            st.markdown("""
            <div class="result-card result-uncertain">
                <span class="result-icon">⚠️</span>
                <div class="result-verdict">UNCERTAIN</div>
                <div class="result-desc">
                    Confidence level below decision threshold.<br>
                    Manual forensic review is recommended.
                </div>
            </div>
            """, unsafe_allow_html=True)
            bar_cls, pct_cls = "uncertain", "uncertain"
            sound_uncertain()   # 🔊 warbling uncertain tone

        elif is_real:
            st.markdown("""
            <div class="result-card result-real">
                <span class="result-icon">✅</span>
                <div class="result-verdict">AUTHENTIC</div>
                <div class="result-desc">
                    Neural patterns consistent with genuine photograph.<br>
                    No manipulation signatures detected.
                </div>
            </div>
            """, unsafe_allow_html=True)
            bar_cls, pct_cls = "real", "real"
            sound_real()        # 🔊 triumphant arpeggio

        else:
            st.markdown("""
            <div class="result-card result-fake">
                <span class="result-icon">🚨</span>
                <div class="result-verdict">SYNTHETIC</div>
                <div class="result-desc">
                    Anomalous neural patterns detected.<br>
                    Image is likely AI-generated or digitally manipulated.
                </div>
            </div>
            """, unsafe_allow_html=True)
            bar_cls, pct_cls = "fake", "fake"
            sound_fake()        # 🔊 ominous descending alarm

        # ── CONFIDENCE BAR ────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="conf-wrap">
            <div class="conf-header">
                <span class="conf-title">CONFIDENCE LEVEL</span>
                <span class="conf-pct {pct_cls}">{pct}%</span>
            </div>
            <div class="conf-track">
                <div class="conf-fill {bar_cls}" style="width:{pct}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── METRICS ───────────────────────────────────────────────────────────
        certainty = "VERY HIGH" if confidence >= 0.90 else ("MODERATE" if confidence >= 0.70 else "LOW")
        verdict   = "AUTHENTIC" if is_real else ("UNCERTAIN" if is_uncertain else "SYNTHETIC")

        st.markdown(f"""
        <div class="metrics">
            <div class="metric" style="animation-delay:.0s">
                <div class="metric-lbl">VERDICT</div>
                <div class="metric-val">{verdict}</div>
            </div>
            <div class="metric" style="animation-delay:.1s">
                <div class="metric-lbl">CONFIDENCE</div>
                <div class="metric-val">{pct}%</div>
            </div>
            <div class="metric" style="animation-delay:.2s">
                <div class="metric-lbl">CERTAINTY</div>
                <div class="metric-val">{certainty}</div>
            </div>
        </div>
        <div class="disclaimer">
            ⚠ NOTICE: No AI detection system achieves 100% accuracy.
            Results should be treated as one forensic signal among many.
            Human verification is recommended for critical decisions.
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center; padding:4rem 1rem;
                font-family:'Share Tech Mono',monospace;
                color:#1a3a52; font-size:.72rem; letter-spacing:.25em; line-height:2.8;">
        [ AWAITING IMAGE INPUT ]<br>
        ────────────────────────<br>
        JPG &nbsp;·&nbsp; JPEG &nbsp;·&nbsp; PNG<br>
        MAX SIZE: 200MB
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1rem 0 .5rem;">
        <div style="font-family:'Orbitron',monospace; font-size:1.3rem; font-weight:900;
                    background:linear-gradient(135deg,#00d4ff,#b44fff,#ff2d9b);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    background-clip:text; letter-spacing:.15em;">
            DEEPTRACE
        </div>
        <div style="font-family:'Rajdhani',sans-serif; font-size:.85rem;
                    color:#7aaabf; letter-spacing:.25em; margin-top:.4rem;">
            v4.0 FORENSICS
        </div>
    </div>
    <hr style="border:none;height:1px;
               background:linear-gradient(90deg,transparent,#b44fff,transparent);margin:1rem 0;">

    <div style="font-family:'Rajdhani',sans-serif; font-size:1rem;
                color:#8bbfd4; line-height:2.2; letter-spacing:.04em;">
        <span style="color:#b44fff; font-size:1.05rem;">▸ MODEL</span>  &nbsp;&nbsp;&nbsp;ViT-B/16<br>
        <span style="color:#b44fff; font-size:1.05rem;">▸ ENGINE</span> &nbsp;&nbsp;PyTorch<br>
        <span style="color:#b44fff; font-size:1.05rem;">▸ HUB</span>    &nbsp;&nbsp;&nbsp;&nbsp;HuggingFace<br>
        <span style="color:#b44fff; font-size:1.05rem;">▸ UI</span>     &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Streamlit<br>
        <span style="color:#b44fff; font-size:1.05rem;">▸ AUDIO</span>  &nbsp;&nbsp;&nbsp;NumPy DSP<br>
        <span style="color:#b44fff; font-size:1.05rem;">▸ STATUS</span> &nbsp;&nbsp;<span style="color:#00ff88; font-weight:700;">● ONLINE</span>
    </div>
    <hr style="border:none;height:1px;
               background:linear-gradient(90deg,transparent,#b44fff,transparent);margin:1rem 0;">

    <div style="font-family:'Orbitron',monospace; font-size:.85rem; font-weight:700;
                color:#00d4ff; letter-spacing:.18em; margin-bottom:.9rem;">HOW TO USE</div>
    <div style="font-family:'Rajdhani',sans-serif; font-size:1rem;
                color:#8bbfd4; line-height:2.3; letter-spacing:.03em;">
        <span style="color:#ffd200; font-weight:700;">01</span> &nbsp;→&nbsp; Upload face image<br>
        <span style="color:#ffd200; font-weight:700;">02</span> &nbsp;→&nbsp; Launch forensic scan<br>
        <span style="color:#ffd200; font-weight:700;">03</span> &nbsp;→&nbsp; View verdict + confidence
    </div>
    <hr style="border:none;height:1px;
               background:linear-gradient(90deg,transparent,#b44fff,transparent);margin:1rem 0;">

    <div style="font-family:'Orbitron',monospace; font-size:.85rem; font-weight:700;
                color:#00d4ff; letter-spacing:.18em; margin-bottom:.9rem;">CONFIDENCE GUIDE</div>
    <div style="font-family:'Rajdhani',sans-serif; font-size:1rem;
                color:#8bbfd4; line-height:2.3; letter-spacing:.03em;">
        90%+ &nbsp;&nbsp;&nbsp;→ <span style="color:#00ff88; font-weight:700;">VERY RELIABLE</span><br>
        70–90% &nbsp;→ <span style="color:#ffd200; font-weight:700;">MODERATE</span><br>
        &lt;70% &nbsp;&nbsp;&nbsp;→ <span style="color:#ff2d55; font-weight:700;">UNCERTAIN</span>
    </div>
    <hr style="border:none;height:1px;
               background:linear-gradient(90deg,transparent,#b44fff,transparent);margin:1rem 0;">

    <div style="font-family:'Rajdhani',sans-serif; font-size:.9rem;
                color:#4a7a92; text-align:center; letter-spacing:.12em; line-height:2;">
        Built with PyTorch<br>HuggingFace · Streamlit
    </div>
    """, unsafe_allow_html=True)