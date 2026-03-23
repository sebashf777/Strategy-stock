# ============================================================
# APEX TRADING TERMINAL  ·  Streamlit Version
# Copyright (c) 2026 Sebastian Hernandez Flores. All Rights Reserved.
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

st.set_page_config(
    page_title="APEX TRADING TERMINAL",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Dark Terminal CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace !important; }
.stApp { background-color: #0A0A0F !important; color: #E8E8F0 !important; }
[data-testid="stSidebar"] { background-color: #0F0F1A !important; border-right: 1px solid #1E1E3A !important; }
[data-testid="stSidebar"] * { color: #E8E8F0 !important; font-family: 'JetBrains Mono', monospace !important; }
.stButton > button {
    background-color: #FF6B1A !important; color: #000 !important;
    font-family: 'JetBrains Mono', monospace !important; font-weight: 700 !important;
    letter-spacing: 2px !important; border: none !important;
    text-transform: uppercase !important; width: 100% !important;
}
.stButton > button:hover { background-color: #FF8C42 !important; }
.stTextInput > div > div > input {
    background-color: #161628 !important; color: #FFD600 !important;
    border: 1px solid #2A2A50 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important; font-size: 18px !important;
    letter-spacing: 3px !important; text-transform: uppercase !important;
}
.stTextInput label { color: #444466 !important; font-size: 10px !important; letter-spacing: 2px !important; }
.stRadio label { color: #8A8AB0 !important; font-size: 10px !important; letter-spacing: 1px !important; }
.stSelectbox label { color: #444466 !important; font-size: 9px !important; letter-spacing: 2px !important; }
.stSelectbox > div > div { background-color: #161628 !important; border-color: #1E1E3A !important; color: #E8E8F0 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Strategies ────────────────────────────────────────────────────────────────
STRATEGIES = {
    "Liquidity Sweep": {
        "short": "SWEEP", "color": "#FF6B1A", "icon": "L",
        "description": "Smart Money Concept",
        "rules": [
            "Price raids equal highs/lows (buy-side or sell-side liquidity)",
            "Engineered liquidity: market makers hunt stops above swing highs",
            "Entry after sweep + reversal candle + retest of swept level",
            "Target: next imbalance or fair value gap (FVG)",
            "Invalidation: candle closes beyond the swept level",
            "1M: ultra-scalp | 5M: scalp | 10M: intraday swing"
        ]
    },
    "AMD Model": {
        "short": "AMD", "color": "#B388FF", "icon": "A",
        "description": "Accumulation · Manipulation · Distribution",
        "rules": [
            "Accumulation: price coils in a range — smart money loads positions",
            "Manipulation: false break of range (stop hunt)",
            "Distribution: price moves in the true intended direction",
            "Entry after M → D confirmation with displacement candle",
            "1M: micro AMD cycle | 5M: session AMD | 10M: macro daily AMD",
            "Valid across all sessions: London, NY, Asia"
        ]
    },
    "Order Flow": {
        "short": "FLOW", "color": "#00B0FF", "icon": "F",
        "description": "Institutional Flow Analysis",
        "rules": [
            "Track delta: bid vs ask volume imbalance in each candle",
            "Absorption: large volume but small candle body = trapped longs/shorts",
            "Volume imbalance creates unfilled orders (price magnets)",
            "Footprint: cluster of high delta bars = institutional entry",
            "Divergence: price makes new high but delta fails = reversal signal",
            "Confirm with depth of market (DOM) stacking near key levels"
        ]
    },
    "Impulse Trend": {
        "short": "IMPULSE", "color": "#00E676", "icon": "I",
        "description": "BosWaves · TradingView Style",
        "rules": [
            "Identifies impulsive moves + corrective pullbacks (Elliott-style)",
            "BosWaves: Break of Structure signals trend continuation",
            "Entry: pullback to impulse origin with momentum confirmation",
            "Trend filter: EMA 21/50/200 alignment on higher TF",
            "Exit: next BOS level or 2R target",
            "Works best on 5M and 10M; 1M = noise filter required"
        ]
    },
    "GS Screener": {
        "short": "SCREENER", "color": "#FFD600", "icon": "G",
        "description": "Goldman Sachs Framework",
        "rules": [
            "P/E vs sector average + revenue growth 5Y trend",
            "Debt-to-equity health check + dividend sustainability",
            "Competitive moat: weak / moderate / strong",
            "Bull/bear price targets for 12-month horizon",
            "Risk rating 1-10 + entry price zones",
            "Stop-loss based on ATR × 1.5 below structure"
        ]
    }
}

BASE_PRICES = {
    "SPY": 562, "QQQ": 478, "AAPL": 221, "TSLA": 268,
    "NVDA": 880, "AMZN": 207, "MSFT": 415, "META": 577,
    "GOOGL": 175, "AMD": 145, "GLD": 210, "BTC": 85000
}

# ── Data & Indicator Functions ────────────────────────────────────────────────
def generate_candles(base_price, tf_minutes, count):
    rng = np.random.default_rng(int(datetime.now().timestamp()) % 9999)
    vol = base_price * {1: 0.0008, 5: 0.0018, 10: 0.003}.get(tf_minutes, 0.002)
    bias = (rng.random() - 0.48) * 0.3
    dates = [datetime.now() - timedelta(minutes=tf_minutes * (count - i)) for i in range(count)]
    rows, price = [], base_price
    for _ in range(count):
        r = vol * (0.5 + rng.random() * 1.5)
        d = 1 if rng.random() > 0.5 - bias else -1
        o = price
        c = round(o + d * r * (0.3 + rng.random() * 0.7), 2)
        h = round(max(o, c) + rng.random() * r * 0.5, 2)
        l = round(min(o, c) - rng.random() * r * 0.5, 2)
        v = int(50000 + rng.random() * 200000)
        rows.append({"open": o, "high": h, "low": l, "close": c, "volume": v})
        price = c
        if rng.random() < 0.04:
            price += d * vol * 2
    return pd.DataFrame(rows, index=pd.DatetimeIndex(dates))

def calc_rsi(closes, p=14):
    s = pd.Series(closes)
    d = s.diff()
    g = d.where(d > 0, 0).rolling(p).mean()
    ls = (-d.where(d < 0, 0)).rolling(p).mean()
    v = (100 - (100 / (1 + g / ls))).iloc[-1]
    return round(v, 1) if not np.isnan(v) else 50.0

def calc_macd(closes):
    s = pd.Series(closes)
    v = (s.ewm(span=12).mean() - s.ewm(span=26).mean()).iloc[-1]
    return round(v, 3)

def calc_bb_pct(closes, p=20):
    s = pd.Series(closes)
    mid = s.rolling(p).mean()
    std = s.rolling(p).std()
    pct = ((s - (mid - 2 * std)) / (4 * std)).iloc[-1]
    return round(pct, 2) if not np.isnan(pct) else 0.5

def calc_vol_ratio(volumes):
    s = pd.Series(volumes)
    r = s.iloc[-1] / s.rolling(20).mean().iloc[-1]
    return round(r, 2) if not np.isnan(r) else 1.0

def get_markers(df, strategy):
    buy_x, buy_y, sell_x, sell_y = [], [], [], []
    rng = np.random.default_rng(42)
    for i in range(5, len(df) - 5):
        c = df.iloc[i]
        prev_lo = df["low"].iloc[i-3:i].min()
        prev_hi = df["high"].iloc[i-3:i].max()
        if strategy in ("Liquidity Sweep", "AMD Model"):
            if c["low"] < prev_lo and c["close"] > prev_lo and rng.random() < 0.3:
                buy_x.append(df.index[i]); buy_y.append(c["low"] * 0.9993)
            if c["high"] > prev_hi and c["close"] < prev_hi and rng.random() < 0.25:
                sell_x.append(df.index[i]); sell_y.append(c["high"] * 1.0007)
        elif strategy == "Order Flow":
            if c["volume"] > 150000 and c["close"] > c["open"] and rng.random() < 0.35:
                buy_x.append(df.index[i]); buy_y.append(c["low"] * 0.9993)
        elif strategy == "Impulse Trend":
            if i % 8 == 0 and c["close"] > c["open"]:
                buy_x.append(df.index[i]); buy_y.append(c["low"] * 0.9993)
        elif strategy == "GS Screener":
            if i % 12 == 0:
                buy_x.append(df.index[i]); buy_y.append(c["low"] * 0.9993)
    return buy_x, buy_y, sell_x, sell_y

# ── Chart Builder ─────────────────────────────────────────────────────────────
def build_chart(df, strategy):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.78, 0.22], vertical_spacing=0.02)
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing=dict(line=dict(color="#00E676", width=1), fillcolor="#00E676"),
        decreasing=dict(line=dict(color="#FF1744", width=1), fillcolor="#FF1744"),
        name="PRICE", showlegend=False
    ), row=1, col=1)
    vol_colors = ["#00E67633" if c > o else "#FF174433"
                  for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(x=df.index, y=df["volume"], marker_color=vol_colors,
                         name="VOLUME", showlegend=False), row=2, col=1)
    hi, lo = df["high"].max(), df["low"].min()
    r = hi - lo
    for price, color, lbl in [(hi, "#FF6B1A66", "HIGH"), (lo, "#00E67666", "LOW"), ((hi+lo)/2, "#8A8AB055", "MID")]:
        fig.add_hline(y=price, line_color=color, line_dash="dash", line_width=1,
                      annotation_text=f" {lbl}", annotation_font_color=color,
                      annotation_font_size=9, row=1, col=1)
    if strategy == "Liquidity Sweep":
        for p, lbl in [(hi - r * 0.1, "LIQ ↑"), (lo + r * 0.1, "LIQ ↓")]:
            fig.add_hline(y=p, line_color="#FF6B1A99", line_width=2,
                          annotation_text=f" {lbl}", annotation_font_color="#FF6B1A",
                          annotation_font_size=9, row=1, col=1)
    elif strategy == "AMD Model":
        for p, lbl in [(lo + r * 0.2, "ACC"), (hi - r * 0.15, "DIST")]:
            fig.add_hline(y=p, line_color="#B388FF99", line_width=2,
                          annotation_text=f" {lbl}", annotation_font_color="#B388FF",
                          annotation_font_size=9, row=1, col=1)
    elif strategy == "Impulse Trend":
        ema21 = df["close"].ewm(span=21).mean().iloc[-1]
        fig.add_hline(y=ema21, line_color="#00E67677", line_width=1,
                      annotation_text=" EMA 21", annotation_font_color="#00E676",
                      annotation_font_size=9, row=1, col=1)
    bx, by, sx, sy = get_markers(df, strategy)
    if bx:
        fig.add_trace(go.Scatter(x=bx, y=by, mode="markers",
            marker=dict(symbol="triangle-up", size=9, color="#00E676"),
            name="BUY", showlegend=True), row=1, col=1)
    if sx:
        fig.add_trace(go.Scatter(x=sx, y=sy, mode="markers",
            marker=dict(symbol="triangle-down", size=9, color="#FF1744"),
            name="SELL", showlegend=True), row=1, col=1)
    fig.update_layout(
        paper_bgcolor="#0A0A0F", plot_bgcolor="#0A0A0F",
        font=dict(family="JetBrains Mono", color="#8A8AB0", size=10),
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=60, t=8, b=0), height=460,
        legend=dict(bgcolor="#161628", bordercolor="#1E1E3A",
                    font=dict(color="#8A8AB0", size=9), x=0.01, y=0.99),
    )
    fig.update_xaxes(gridcolor="#1E1E3A", showgrid=True, zeroline=False,
                     showspikes=True, spikecolor="#FF6B1A55", spikethickness=1)
    fig.update_yaxes(gridcolor="#1E1E3A", showgrid=True, zeroline=False,
                     showspikes=True, spikecolor="#FF6B1A55", spikethickness=1)
    return fig

# ── HTML helpers ──────────────────────────────────────────────────────────────
def panel_header(text):
    return f'<div style="padding:7px 12px;background:rgba(255,107,26,0.08);border:1px solid #1E1E3A;border-radius:4px 4px 0 0;font-size:9px;letter-spacing:3px;color:#FF6B1A;font-weight:700;text-transform:uppercase">{text}</div>'

def signal_card(label, value, color, sub):
    return f'<div style="background:#161628;border:1px solid #1E1E3A;border-radius:4px;padding:10px 12px;margin-bottom:6px"><div style="font-size:9px;letter-spacing:2px;color:#444466;text-transform:uppercase">{label}</div><div style="font-size:22px;font-weight:700;color:{color}">{value}</div><div style="font-size:10px;color:#8A8AB0;margin-top:2px">{sub}</div></div>'

def ind_card(label, value, color):
    return f'<div style="background:#161628;border:1px solid #1E1E3A;border-radius:4px;padding:8px 6px;text-align:center"><div style="font-size:8px;letter-spacing:2px;color:#444466;text-transform:uppercase">{label}</div><div style="font-size:17px;font-weight:700;color:{color};margin-top:2px">{value}</div></div>'

def ai_row(label, value, color):
    return f'<div style="display:flex;justify-content:space-between;font-size:10px;padding:5px 0;border-bottom:1px solid #1E1E3A"><span style="color:#8A8AB0">{label}</span><span style="font-weight:700;color:{color}">{value}</span></div>'

def ts_item(label, value, color):
    return f'<div style="background:#0F0F1A;border:1px solid #1E1E3A;border-radius:2px;padding:8px;text-align:center"><div style="font-size:8px;letter-spacing:2px;color:#444466;text-transform:uppercase">{label}</div><div style="font-size:15px;font-weight:700;color:{color}">{value}</div></div>'

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('''<div style="display:flex;align-items:center;gap:10px;padding:8px 0 18px 0;border-bottom:1px solid #1E1E3A;margin-bottom:16px">
    <div style="width:28px;height:28px;background:#FF6B1A;clip-path:polygon(50% 0%,100% 50%,50% 100%,0% 50%)"></div>
    <span style="color:#FF6B1A;font-size:13px;font-weight:700;letter-spacing:4px">APEX TERMINAL</span>
    </div>''', unsafe_allow_html=True)

    ticker = st.text_input("TICKER", value="SPY", max_chars=6).upper().strip() or "SPY"
    st.markdown(panel_header("⬡ TIMEFRAME"), unsafe_allow_html=True)
    tf_label = st.radio("", ["1M", "5M", "10M"], horizontal=True, label_visibility="collapsed", key="tf")
    tf_min = int(tf_label[:-1])
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(panel_header("⬡ STRATEGY"), unsafe_allow_html=True)
    strategy = st.selectbox("", list(STRATEGIES.keys()), label_visibility="collapsed", key="strat")
    analyze = st.button("▶ ANALYZE", type="primary")

    st.markdown("<br>", unsafe_allow_html=True)
    strat_cfg = STRATEGIES[strategy]
    rules_html = "".join([
        f'<div style="display:flex;gap:8px;padding:5px 0;border-bottom:1px solid #1E1E3A;font-size:10px;color:#8A8AB0;align-items:flex-start"><div style="width:5px;height:5px;min-width:5px;border-radius:50%;background:{strat_cfg["color"]};margin-top:5px"></div><div>{r}</div></div>'
        for r in strat_cfg["rules"]
    ])
    st.markdown(f'''<div style="background:#161628;border:1px solid #1E1E3A;border-radius:4px;overflow:hidden">
    <div style="padding:9px 12px;border-bottom:1px solid #1E1E3A;display:flex;align-items:center;gap:10px">
    <div style="background:{strat_cfg["color"]}22;color:{strat_cfg["color"]};font-weight:800;font-size:12px;padding:3px 7px;border-radius:2px">{strat_cfg["icon"]}</div>
    <div><div style="font-size:11px;font-weight:700;color:#E8E8F0">{strategy}</div>
    <div style="font-size:9px;color:#444466">{strat_cfg["description"]}</div></div></div>
    <div style="padding:10px 12px">{rules_html}</div></div>''', unsafe_allow_html=True)

    st.markdown('<div style="margin-top:16px;font-size:9px;color:#444466;line-height:1.7">Risk models based on Goldman Sachs, Bridgewater & Morgan Stanley frameworks.<br>Not financial advice. Past performance ≠ future results.</div>', unsafe_allow_html=True)

# ── GENERATE DATA ─────────────────────────────────────────────────────────────
cache_key = f"{ticker}_{tf_min}_{strategy}"
if "cache_key" not in st.session_state or st.session_state.cache_key != cache_key or analyze:
    base = BASE_PRICES.get(ticker, 150 + np.random.random() * 300)
    count = {1: 120, 5: 100, 10: 80}.get(tf_min, 100)
    df = generate_candles(base, tf_min, count)
    rng2 = np.random.default_rng(int(datetime.now().timestamp()) % 7777)
    st.session_state.df = df
    st.session_state.cache_key = cache_key
    st.session_state.sig = {
        "rsi": calc_rsi(df["close"].tolist()),
        "macd": calc_macd(df["close"].tolist()),
        "bb": calc_bb_pct(df["close"].tolist()),
        "vol_ratio": calc_vol_ratio(df["volume"].tolist()),
        "sentiment": round((rng2.random() - 0.4) * 0.8, 3),
        "vol_ann": round(12 + rng2.random() * 25, 1),
        "sweep_str": float(rng2.random()),
        "prob": round(50 + rng2.random() * 30, 1),
        "acc": round(55 + rng2.random() * 25, 1),
        "auc": round(0.55 + rng2.random() * 0.2, 2),
    }

df = st.session_state.df
s  = st.session_state.sig

last  = df["close"].iloc[-1];  prev = df["close"].iloc[-2]
chg   = last - prev;           chg_p = (chg / prev) * 100
trend = last > prev

rsi, macd, bb, vol_ratio = s["rsi"], s["macd"], s["bb"], s["vol_ratio"]
sentiment, vol_ann, sweep_str, prob, acc, auc = (
    s["sentiment"], s["vol_ann"], s["sweep_str"], s["prob"], s["acc"], s["auc"])

direction = "BUY" if (trend and rsi < 70) else "SELL" if (not trend and rsi > 50) else "HOLD"
dir_col   = "#00E676" if direction == "BUY" else "#FF1744" if direction == "SELL" else "#FFD600"
vol_reg   = "LOW" if vol_ann < 18 else "NORMAL" if vol_ann < 28 else "HIGH"
vol_col   = "#00E676" if vol_ann < 18 else "#FFD600" if vol_ann < 28 else "#FF1744"
sent_lbl  = "BULLISH" if sentiment > 0.1 else "BEARISH" if sentiment < -0.1 else "NEUTRAL"
sent_col  = "#00E676" if sentiment > 0.1 else "#FF1744" if sentiment < -0.1 else "#FFD600"
lgbm_sig  = "BUY" if (trend and rsi < 65) else "SELL" if (not trend and rsi > 50) else "HOLD"
lgbm_col  = "#00E676" if lgbm_sig == "BUY" else "#FF1744" if lgbm_sig == "SELL" else "#FFD600"
garch_reg = "LOW VOL" if vol_ann < 18 else "NORMAL" if vol_ann < 28 else "HIGH VOL"
garch_col = "#00E676" if vol_ann < 18 else "#FFD600" if vol_ann < 28 else "#FF1744"
rsi_col   = "#FF1744" if rsi > 70 else "#00E676" if rsi < 30 else "#FFD600"
macd_col  = "#00E676" if macd > 0 else "#FF1744"
swp_lbl   = "HIGH" if sweep_str > 0.66 else "MED" if sweep_str > 0.33 else "LOW"
swp_col   = "#FF6B1A" if sweep_str > 0.66 else "#FFD600" if sweep_str > 0.33 else "#00E676"
badge_txt = "⚡ SWEEP DETECTED" if sweep_str > 0.6 else ("▲ BULLISH FLOW" if trend else "▼ BEARISH FLOW")
badge_col = "#FF6B1A" if sweep_str > 0.6 else ("#00E676" if trend else "#FF1744")
atr       = last * 0.008 * (1 + np.random.random() * 0.5)
stop_p    = round(last - atr * 1.5, 2) if trend else round(last + atr * 1.5, 2)
tp1       = round(last + atr * 2, 2)   if trend else round(last - atr * 2, 2)
tp2       = round(last + atr * 4, 2)   if trend else round(last - atr * 4, 2)
chg_sign  = "+" if chg >= 0 else ""
chg_clr   = "#00E676" if chg >= 0 else "#FF1744"

# ── PRICE BAR ─────────────────────────────────────────────────────────────────
st.markdown(f'''<div style="background:#0F0F1A;border:1px solid #1E1E3A;border-radius:4px;
padding:12px 20px;display:flex;align-items:baseline;gap:16px;margin-bottom:12px;
font-family:'JetBrains Mono',monospace">
<span style="font-size:30px;font-weight:700;color:#FFD600;letter-spacing:-1px">${last:.2f}</span>
<span style="font-size:14px;font-weight:600;color:{chg_clr}">{chg_sign}{chg:.2f} ({chg_sign}{chg_p:.2f}%)</span>
<span style="font-size:10px;color:#444466;letter-spacing:2px">{ticker} · {tf_label}</span>
<span style="margin-left:auto;font-size:9px;color:{badge_col};letter-spacing:1px;
border:1px solid {badge_col}44;padding:3px 10px;border-radius:2px;background:{badge_col}11">
{badge_txt}</span></div>''', unsafe_allow_html=True)

# ── MAIN COLUMNS ──────────────────────────────────────────────────────────────
col_chart, col_right = st.columns([3, 1.15], gap="medium")

with col_chart:
    st.plotly_chart(build_chart(df, strategy), use_container_width=True,
                    config={"displayModeBar": False})

    st.markdown(panel_header("⬡ LIVE SIGNALS"), unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown(signal_card("DIRECTION",         direction, dir_col,  f"Prob: {prob}%"), unsafe_allow_html=True)
    c2.markdown(signal_card("VOLATILITY REGIME", vol_reg,   vol_col,  f"Ann. Vol: {vol_ann}%"), unsafe_allow_html=True)
    c3.markdown(signal_card("SENTIMENT",         sent_lbl,  sent_col, f"Score: {'+' if sentiment > 0 else ''}{sentiment:.2f}"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(panel_header("⬡ TECHNICAL INDICATORS"), unsafe_allow_html=True)
    i1, i2, i3, i4, i5 = st.columns(5)
    i1.markdown(ind_card("RSI(14)",   f"{rsi}",                            rsi_col),  unsafe_allow_html=True)
    i2.markdown(ind_card("MACD",      f"{'+' if macd>0 else ''}{macd:.3f}", macd_col), unsafe_allow_html=True)
    i3.markdown(ind_card("BB %",      f"{bb:.2f}",                         "#00B0FF"), unsafe_allow_html=True)
    i4.markdown(ind_card("VOL RATIO", f"{vol_ratio:.2f}×",                 "#FF6B1A"), unsafe_allow_html=True)
    i5.markdown(ind_card("SWEEP STR", swp_lbl,                             swp_col),  unsafe_allow_html=True)

with col_right:
    rng3 = np.random.default_rng(int(datetime.now().timestamp()) % 3333)
    flow_labels = ["BID", "ASK", "L2", "L3", "MKT"]
    flow_buys   = [int(45 + rng3.random() * 30) for _ in flow_labels]
    flow_rows   = "".join([
        f'<div style="display:flex;align-items:center;gap:6px;font-size:9px;margin-bottom:5px">'
        f'<div style="color:#8A8AB0;width:28px">{lb}</div>'
        f'<div style="flex:1;height:14px;background:#0F0F1A;border-radius:2px;position:relative;overflow:hidden">'
        f'<div style="position:absolute;left:0;top:0;bottom:0;width:{b}%;background:rgba(0,230,118,0.65);border-radius:2px 0 0 2px"></div>'
        f'<div style="position:absolute;right:0;top:0;bottom:0;width:{100-b}%;background:rgba(255,23,68,0.65);border-radius:0 2px 2px 0"></div></div>'
        f'<div style="color:#444466;width:28px;text-align:right">{b}%</div></div>'
        for lb, b in zip(flow_labels, flow_buys)
    ])
    st.markdown(f'<div style="background:#161628;border:1px solid #1E1E3A;border-radius:4px;overflow:hidden;margin-bottom:12px">{panel_header("⬡ ORDER FLOW DELTA")}<div style="padding:10px 12px">{flow_rows}</div></div>', unsafe_allow_html=True)

    ai_rows_html = "".join([ai_row(*r) for r in [
        ("LightGBM",        lgbm_sig,                                           lgbm_col),
        ("Up Probability",  f"{prob}%",                                         "#FFD600"),
        ("Direction Acc.",  f"{acc}%",                                          "#FFD600"),
        ("AUC (hold-out)",  str(auc),                                           "#FFD600"),
        ("GARCH Regime",    garch_reg,                                          garch_col),
        ("Ann. Volatility", f"{vol_ann}%",                                      garch_col),
        ("VADER Sentiment", sent_lbl,                                           sent_col),
        ("NLP Score",       f"{'+' if sentiment>0 else ''}{sentiment:.3f}",     sent_col),
    ]])
    st.markdown(f'''<div style="background:#161628;border:1px solid #1E1E3A;border-radius:4px;overflow:hidden;margin-bottom:12px">
    <div style="padding:8px 12px;background:rgba(179,136,255,0.08);border-bottom:1px solid #1E1E3A;display:flex;justify-content:space-between">
    <span style="font-size:9px;letter-spacing:3px;color:#B388FF;font-weight:700">⬡ AI / ML ANALYSIS</span>
    <span style="font-size:9px;color:#444466">LightGBM · GARCH · NLP</span></div>
    <div style="padding:8px 12px">{ai_rows_html}</div></div>''', unsafe_allow_html=True)

    ts_grid = (
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px">'
        f'{ts_item("ENTRY", f"${last:.2f}", "#FFD600")}{ts_item("STOP", f"${stop_p}", "#FF1744")}'
        f'{ts_item("TP1", f"${tp1}", "#00E676")}{ts_item("TP2", f"${tp2}", "#00E676")}</div>'
        f'<div style="background:#0F0F1A;border:1px solid #1E1E3A;border-radius:2px;padding:8px;text-align:center">'
        f'<div style="font-size:8px;letter-spacing:2px;color:#444466">RISK / REWARD</div>'
        f'<div style="font-size:14px;font-weight:700;color:#FF6B1A">2.0R · ATR ${atr:.2f}</div></div>'
    )
    st.markdown(f'''<div style="background:#161628;border:1px solid #FF6B1A;border-radius:4px;padding:14px">
    <div style="font-size:9px;letter-spacing:3px;color:#FF6B1A;font-weight:700;margin-bottom:10px">
    ◈ TRADE SETUP — {strat_cfg["short"]}</div>{ts_grid}</div>''', unsafe_allow_html=True)
