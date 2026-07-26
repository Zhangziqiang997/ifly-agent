"""Streamlit UI — exact visual match with prototype_design.html dark navy design system."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import streamlit as st
import pandas as pd
from engine import run_analysis

st.set_page_config(page_title="Parameter Agent", layout="wide")

# ═══════════════════════════════════════════════════════════════
# AGGRESSIVE CSS — kill every white background Streamlit creates
# ═══════════════════════════════════════════════════════════════
CSS = r"""
<style>
:root {
    --bg: #0A1628; --surface: #0F1E35; --card: #162035; --border: #1E3050;
    --cyan: #00D4FF; --cyan-dim: rgba(0,212,255,.12); --amber: #FFB547;
    --red: #FF5C5C; --green: #22C55E; --text: #E8EDF5; --muted: #6B82A0;
}

/* KILL ALL WHITE */
.stApp, .stMain, .main, #root, body, html,
div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewBlockContainer"],
div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"],
div[data-testid="column"],
div[data-testid="stBlock"],
div.st-emotion-cache-0,
div.stMainBlockContainer,
section.main,
div.block-container {
    background: var(--bg) !important;
}

/* Every possible container that defaults to white */
div[data-testid="stVerticalBlockBorderWrapper"],
div.element-container,
div[class*="st-emotion-cache"] {
    background: transparent !important;
}

/* Typography — Inter + Noto Sans SC + JetBrains Mono */
* { font-family: "Inter", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif; }
h1, h2, h3, h4 { color: var(--text) !important; }
h1 { font-size: 1.35rem !important; font-weight: 700 !important; }
h2 { font-size: 1.05rem !important; font-weight: 600 !important; margin-top: 24px; }
h3 { font-size: 0.9rem !important; font-weight: 600 !important; }
.stCaption, .st-caption { color: var(--muted) !important; font-size: 0.8rem !important; }
p, li, label { color: var(--text) !important; }

/* Sidebar */
section[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border) !important; }
section[data-testid="stSidebar"] * { color: var(--text) !important; }
section[data-testid="stSidebar"] .st-emotion-cache-0 { background: var(--surface) !important; }

/* Buttons */
.stButton > button {
    font-weight: 600 !important; font-size: 0.82rem !important; padding: 10px 22px !important;
    border-radius: 8px !important; transition: all 0.15s !important;
}
.stButton > button[kind="primary"] {
    background: var(--cyan) !important; color: #0A1628 !important; border: none !important;
}
.stButton > button[kind="primary"]:hover { background: #33dcff !important; }
.stButton > button[kind="secondary"] {
    background: transparent !important; border: 1px solid var(--border) !important; color: var(--text) !important;
}
.stButton > button[kind="secondary"]:hover { border-color: var(--cyan) !important; color: var(--cyan) !important; }
.stButton > button:not([kind]) {
    background: transparent !important; border: 1px solid var(--border) !important; color: var(--muted) !important;
}
.stButton > button:not([kind]):hover { border-color: var(--cyan) !important; color: var(--cyan) !important; }

/* Selectbox */
div[data-testid="stSelectbox"] * {
    color: var(--text) !important; background: var(--card) !important;
    border-color: var(--border) !important; border-radius: 8px !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text) !important; font-weight: 600 !important;
}
.streamlit-expanderHeader:hover { border-color: var(--cyan) !important; }
.streamlit-expanderContent { background: var(--surface) !important; border: 1px solid var(--border) !important; border-top: none !important; border-radius: 0 0 10px 10px !important; }

/* Spinner */
.stSpinner > div { border-color: var(--cyan) var(--cyan) transparent transparent !important; }

/* Alert boxes */
div[data-testid="stAlert"] { border-radius: 10px !important; border: 1px solid var(--border) !important; }
div[data-testid="stInfo"] { background: rgba(0,212,255,.08) !important; }
div[data-testid="stSuccess"] { background: rgba(34,197,94,.08) !important; }
div[data-testid="stWarning"] { background: rgba(255,181,71,.08) !important; }
div[data-testid="stError"] { background: rgba(255,92,92,.08) !important; }

/* File uploader */
div[data-testid="stFileUploader"] section {
    background: var(--surface) !important; border: 2px dashed var(--border) !important; border-radius: 14px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }

/* Kill chart white backgrounds */
div[data-testid="stVegaLiteChart"] { background: transparent !important; }
div[data-testid="stVegaLiteChart"] > * { background: transparent !important; }
canvas, .vega-embed, .vega-embed svg, .marks { background: transparent !important; }
div[data-testid="stArrowVegaLiteChart"] { background: transparent !important; }
div[data-testid="stArrowVegaLiteChart"] > * { background: transparent !important; }

/* Kill dataframe / table white */
div[data-testid="stTable"], .stDataFrame, div[data-testid="stDataFrame"] { background: transparent !important; }
div[data-testid="stTable"] * { background: transparent !important; color: var(--text) !important; }
div.dvn-scroller { background: transparent !important; }
div[data-testid="stDataFrame"] table { background: transparent !important; }
div[data-testid="stDataFrame"] th {
    background: var(--surface) !important; color: var(--muted) !important; border-bottom: 1px solid var(--border) !important;
}
div[data-testid="stDataFrame"] td { background: transparent !important; color: var(--text) !important; border-bottom: 1px solid rgba(30,48,80,.5) !important; }
div[data-testid="stDataFrame"] tr:hover td { background: rgba(255,255,255,.02) !important; }

/* Kill metric white */
div[data-testid="stMetric"] { background: transparent !important; }
div[data-testid="stMetric"] > div { background: transparent !important; }
div[data-testid="stMetric"] label { color: var(--muted) !important; font-size: 0.68rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: var(--cyan) !important; font-size: 1.6rem !important; font-weight: 700 !important;
    font-family: "JetBrains Mono", "Cascadia Code", monospace !important;
}

/* Title area */
div[data-testid="stHeading"] * { color: var(--text) !important; }
div[data-testid="stHeadingContainer"] { background: transparent !important; }
</style>
"""

_CS = {
    "bg": "#0A1628", "surface": "#0F1E35", "card": "#162035", "border": "#1E3050",
    "cyan": "#00D4FF", "amber": "#FFB547", "red": "#FF5C5C", "green": "#22C55E",
    "text": "#E8EDF5", "muted": "#6B82A0", "purple": "#A78BFA",
}

def _css():
    st.markdown(CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# Reusable HTML component helpers
# ═══════════════════════════════════════════════════════════════

def _stat_card(num, label, color):
    """A single stat card matching prototype's stat-card."""
    return f"""
    <div style="background:{_CS['card']};border:1px solid {_CS['border']};border-radius:10px;padding:16px 18px;">
        <div style="font-size:1.6rem;font-weight:700;font-family:'JetBrains Mono',monospace;color:{color};">{num}</div>
        <div style="font-size:0.68rem;color:{_CS['muted']};text-transform:uppercase;letter-spacing:.08em;">{label}</div>
    </div>"""


def _verdict_card(ctrl, summary):
    """Verdict card matching prototype exactly — vendor name, donut ring, hit list."""
    pct = int(ctrl['confidence'] * 100)
    if pct > 60:
        vc, vl = _CS["red"], "Highly Suspicious"
    elif pct > 30:
        vc, vl = _CS["amber"], "Partial Bias"
    else:
        vc, vl = _CS["muted"], "Low Bias"

    # SVG donut
    circumference = 2 * 3.14159 * 38  # r=38
    dash = circumference * pct / 100
    gap = circumference - dash

    html = f"""
    <div style="background:{_CS['card']};border:1px solid {_CS['border']};border-radius:12px;padding:24px;">
        <div style="font-size:0.68rem;font-weight:600;color:{_CS['muted']};text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;">
            Controlling Vendor
        </div>
        <div style="font-size:1.4rem;font-weight:700;color:#fff;">{ctrl['vendor']}</div>
        <div style="font-size:0.8rem;color:{_CS['muted']};margin-bottom:16px;">Bidding controller target</div>

        <div style="display:flex;align-items:center;gap:20px;margin:8px 0;">
            <div style="width:90px;height:90px;position:relative;flex-shrink:0;">
                <svg width="90" height="90" viewBox="0 0 90 90" style="transform:rotate(-90deg);">
                    <circle cx="45" cy="45" r="28" fill="none" stroke="rgba(255,92,92,.3)" stroke-width="1" style="animation:ring-pulse 2s ease-out infinite;"/>
                    <circle cx="45" cy="45" r="28" fill="none" stroke="rgba(255,92,92,.3)" stroke-width="1" style="animation:ring-pulse 2s ease-out .7s infinite;"/>
                    <circle cx="45" cy="45" r="38" fill="none" stroke="{_CS['border']}" stroke-width="5"/>
                    <circle cx="45" cy="45" r="38" fill="none" stroke="{vc}" stroke-width="5"
                            stroke-dasharray="{dash:.0f} {gap:.0f}" stroke-dashoffset="60" stroke-linecap="round"/>
                </svg>
                <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;">
                    <span style="font-family:'JetBrains Mono',monospace;font-size:1rem;font-weight:700;color:{vc};">{pct}%</span>
                </div>
            </div>
            <div>
                <div style="font-size:1.8rem;font-weight:700;font-family:'JetBrains Mono',monospace;color:{vc};">{pct}%</div>
                <div style="font-size:0.7rem;color:{_CS['muted']};">Unique feature hit rate</div>
                <div style="margin-top:10px;">
                    <span style="display:inline-flex;align-items:center;gap:6px;background:rgba(255,92,92,.12);border:1px solid rgba(255,92,92,.3);color:{vc};border-radius:20px;padding:5px 12px;font-size:0.72rem;font-weight:600;">
                        &#9888; {vl}
                    </span>
                </div>
            </div>
        </div>

        <div style="font-size:0.68rem;font-weight:600;color:{_CS['muted']};text-transform:uppercase;letter-spacing:.08em;margin:18px 0 8px 0;">
            Unique Feature Hits
        </div>
        <div style="display:flex;flex-direction:column;gap:6px;max-height:200px;overflow-y:auto;">
    """
    for hit in ctrl.get('hits', []):
        html += f"""
            <div style="display:flex;align-items:flex-start;gap:8px;font-size:0.75rem;padding:7px 10px;background:{_CS['surface']};border-radius:6px;border:1px solid {_CS['border']};">
                <div style="width:6px;height:6px;background:{_CS['red']};border-radius:50%;margin-top:5px;flex-shrink:0;"></div>
                <div style="line-height:1.5;color:{_CS['text']};">
                    <span style="color:{_CS['muted']};font-family:'JetBrains Mono',monospace;font-size:0.7rem;">#{hit['seq']}</span>
                    {hit['param_name']}
                    <span style="color:{_CS['muted']};font-size:0.65rem;"> &middot; {hit['hit_vendor']}</span>
                </div>
            </div>"""
    html += "</div></div>"
    return html


def _bar_chart_html(scores):
    """Custom HTML bar chart matching prototype's stacked bar style."""
    if not scores:
        return ""
    vendors = list(scores.keys())
    vals = list(scores.values())
    max_val = max(vals) if max(vals) > 0 else 1
    bar_height = 120
    bar_width = 48
    gap = 24

    html = f"""
    <div style="background:{_CS['card']};border:1px solid {_CS['border']};border-radius:12px;padding:22px;">
        <div style="font-size:0.68rem;font-weight:600;color:{_CS['muted']};text-transform:uppercase;letter-spacing:.08em;margin-bottom:14px;">
            Vendor Unique Feature Distribution
        </div>
        <div style="display:flex;align-items:flex-end;gap:{gap}px;height:{bar_height}px;">
    """
    for i, v in enumerate(vendors):
        h = int(vals[i] / max_val * bar_height)
        html += f"""
            <div style="display:flex;flex-direction:column;align-items:center;gap:6px;flex:1;">
                <div style="font-size:0.8rem;font-weight:600;font-family:'JetBrains Mono',monospace;color:{_CS['text']};margin-bottom:2px;">{vals[i]}</div>
                <div style="width:100%;height:{h}px;background:{_CS['red']};border-radius:4px 4px 0 0;opacity:0.85;"></div>
                <div style="font-size:0.7rem;color:{_CS['muted']};text-align:center;line-height:1.3;white-space:nowrap;">{v}</div>
            </div>"""
    html += """
        </div>
        <div style="display:flex;gap:18px;margin-top:14px;font-size:0.75rem;">
            <span style="display:flex;align-items:center;gap:6px;color:%s;">
                <span style="width:10px;height:10px;background:%s;border-radius:2px;display:inline-block;"></span>
                Unique Feature Hits per Vendor
            </span>
        </div>
    </div>""" % (_CS["muted"], _CS["red"])
    return html


def _deviation_badge(dev):
    if dev == 'positive':
        return f'<span style="display:inline-flex;align-items:center;gap:4px;font-size:0.68rem;font-weight:600;padding:3px 10px;border-radius:5px;background:rgba(34,197,94,.12);color:{_CS["green"]};border:1px solid rgba(34,197,94,.25);">Green</span>'
    elif dev == 'negative_wording':
        return f'<span style="display:inline-flex;align-items:center;gap:4px;font-size:0.68rem;font-weight:600;padding:3px 10px;border-radius:5px;background:rgba(255,181,71,.12);color:{_CS["amber"]};border:1px solid rgba(255,181,71,.25);">Yellow</span>'
    return f'<span style="display:inline-flex;align-items:center;gap:4px;font-size:0.68rem;font-weight:600;padding:3px 10px;border-radius:5px;background:rgba(255,92,92,.12);color:{_CS["red"]};border:1px solid rgba(255,92,92,.25);">Red</span>'


def _method_badge(method):
    if method == 'ai_semantic':
        return f'<span style="font-size:0.62rem;font-family:JetBrains Mono,monospace;background:{_CS["surface"]};border:1px solid {_CS["border"]};padding:2px 7px;border-radius:4px;color:{_CS["purple"]};">AI</span>'
    return f'<span style="font-size:0.62rem;font-family:JetBrains Mono,monospace;background:{_CS["surface"]};border:1px solid {_CS["border"]};padding:2px 7px;border-radius:4px;color:{_CS["cyan"]};">PROGRAM</span>'


# ═══════════════════════════════════════════════════════════════
# Page 1 — Upload & Analysis Result
# ═══════════════════════════════════════════════════════════════
def page_upload():
    _css()

    st.title("Upload Bidding Document")
    st.caption("Upload a JSON bidding file or use the sample to run 3-layer analysis.")

    col1, col2 = st.columns([1.6, 1])
    with col1:
        uploaded = st.file_uploader("Drop file here", type=["json"], key="bid_upload", label_visibility="collapsed")
    with col2:
        use_sample = st.button("Use Sample Bid", type="primary", use_container_width=True)

    if not uploaded and not use_sample:
        st.markdown(f"""
        <div style="background:{_CS['surface']};border:2px dashed {_CS['border']};border-radius:14px;padding:56px 40px;text-align:center;">
            <div style="font-size:48px;margin-bottom:16px;">&#128196;</div>
            <div style="font-size:1.1rem;font-weight:600;color:{_CS['text']};margin-bottom:6px;">Drag &amp; drop file here, or click to select</div>
            <div style="font-size:0.8rem;color:{_CS['muted']};">Supported formats: .json (bidding document)</div>
            <div style="display:flex;gap:10px;justify-content:center;margin-top:14px;">
                <span style="background:rgba(255,255,255,.05);border:1px solid {_CS['border']};border-radius:6px;padding:4px 12px;font-size:0.65rem;font-family:'JetBrains Mono',monospace;color:{_CS['muted']};">.json</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    with st.spinner("Running 3-layer analysis..."):
        if use_sample:
            result = run_analysis("sample-bid.json")
        else:
            content = uploaded.getvalue().decode("utf-8")
            tmp_path = os.path.join(os.path.dirname(__file__), "..", "data", "samples", "_uploaded.json")
            os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
            result = run_analysis("_uploaded.json")

    st.session_state.result = result

    ctrl = result['controller']
    summary = result['summary']

    # ── Page header ──
    st.markdown(f"""
    <div style="margin:12px 0 20px 0;">
        <div style="font-size:1.3rem;font-weight:700;color:{_CS['text']};">Analysis Report</div>
        <div style="font-size:0.75rem;color:{_CS['muted']};">
            {result.get('project', 'Bidding Project')} &middot; {summary['total']} parameters analyzed
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats row (4 cards) — single markdown block ──
    st.markdown(
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px;">'
        f'{_stat_card(summary["total"], "Total Parameters", _CS["cyan"])}'
        f'{_stat_card(summary["positive"], "Positive (Green)", _CS["green"])}'
        f'{_stat_card(summary["negative_wording"], "Fixable Wording", _CS["amber"])}'
        f'{_stat_card(summary["negative_real"], "Unsatisfied (Red)", _CS["red"])}'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Verdict + Bar chart row — single markdown block ──
    chart = _bar_chart_html(ctrl.get('scores', {}))
    st.markdown(
        f'<div style="display:grid;grid-template-columns:340px 1fr;gap:20px;margin-bottom:20px;">'
        f'{_verdict_card(ctrl, summary)}'
        f'{chart}'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Deviation overview ──
    st.markdown("""
    <div style="font-size:0.68rem;font-weight:600;color:%s;text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px;">
        Deviation Overview
    </div>""" % _CS["muted"], unsafe_allow_html=True)

    d1, d2, d3 = st.columns(3)
    with d1:
        st.metric("Green (Positive)", summary['positive'])
    with d2:
        st.metric("Yellow (Fixable Wording)", summary['negative_wording'])
    with d3:
        st.metric("Red (Unsatisfied)", summary['negative_real'])

    st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)
    if st.button("View Detailed Comparison", type="primary"):
        st.session_state.page = "compare"
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# Page 2 — Comparison Table & Advice
# ═══════════════════════════════════════════════════════════════
def page_compare():
    _css()

    if 'result' not in st.session_state or st.session_state.result is None:
        st.warning("No analysis result. Please upload first.")
        if st.button("Back to Upload"):
            st.session_state.page = "upload"
            st.rerun()
        return

    result = st.session_state.result
    summary = result['summary']

    st.title("Parameter Comparison")

    st.markdown(f"""
    <div style="font-size:0.75rem;color:{_CS['muted']};margin-bottom:20px;">
        {result.get('project', 'Bidding Project')} &middot; {summary['total']} parameters &middot;
        Controller: <span style="color:{_CS['cyan']};">{result['controller']['vendor']}</span>
        ({result['controller']['confidence']:.0%})
    </div>
    """, unsafe_allow_html=True)

    # Toolbar
    tb_left, tb_right = st.columns([0.5, 3])
    with tb_left:
        if st.button("Back to Report", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()
    with tb_right:
        filter_option = st.selectbox(
            "", ["All Parameters", "Green (Positive)", "Yellow (Fixable Wording)", "Red (Unsatisfied)"],
            label_visibility="collapsed"
        )

    matching = result['matching']
    if "Green" in filter_option:
        matching = [m for m in matching if m['deviation'] == 'positive']
    elif "Yellow" in filter_option:
        matching = [m for m in matching if m['deviation'] == 'negative_wording']
    elif "Red" in filter_option:
        matching = [m for m in matching if m['deviation'] == 'negative_real']

    # ── Raw HTML Table (NOT st.dataframe — avoids white bg) ──
    table_html = f"""
    <div style="background:{_CS['card']};border:1px solid {_CS['border']};border-radius:12px;overflow:hidden;margin-bottom:20px;">
        <div style="display:flex;align-items:center;gap:10px;padding:14px 18px;border-bottom:1px solid {_CS['border']};">
            <div style="font-size:0.9rem;font-weight:600;color:{_CS['text']};margin-right:auto;">Parameter Comparison Table</div>
            <span style="font-size:0.65rem;color:{_CS['muted']};">filtered: {len(matching)} / {summary['total']}</span>
        </div>
        <table style="width:100%;border-collapse:collapse;">
            <thead>
                <tr>
                    <th style="background:{_CS['surface']};font-size:0.68rem;font-weight:600;color:{_CS['muted']};text-transform:uppercase;letter-spacing:.06em;padding:10px 16px;text-align:left;border-bottom:1px solid {_CS['border']};width:32px;">#</th>
                    <th style="background:{_CS['surface']};font-size:0.68rem;font-weight:600;color:{_CS['muted']};text-transform:uppercase;letter-spacing:.06em;padding:10px 16px;text-align:left;border-bottom:1px solid {_CS['border']};width:64px;">Category</th>
                    <th style="background:{_CS['surface']};font-size:0.68rem;font-weight:600;color:{_CS['muted']};text-transform:uppercase;letter-spacing:.06em;padding:10px 16px;text-align:left;border-bottom:1px solid {_CS['border']};">Bidding Requirement</th>
                    <th style="background:{_CS['surface']};font-size:0.68rem;font-weight:600;color:{_CS['muted']};text-transform:uppercase;letter-spacing:.06em;padding:10px 16px;text-align:left;border-bottom:1px solid {_CS['border']};">iFLYTEK Spec</th>
                    <th style="background:{_CS['surface']};font-size:0.68rem;font-weight:600;color:{_CS['muted']};text-transform:uppercase;letter-spacing:.06em;padding:10px 16px;text-align:left;border-bottom:1px solid {_CS['border']};width:96px;">Deviation</th>
                    <th style="background:{_CS['surface']};font-size:0.68rem;font-weight:600;color:{_CS['muted']};text-transform:uppercase;letter-spacing:.06em;padding:10px 16px;text-align:left;border-bottom:1px solid {_CS['border']};width:80px;">Method</th>
                </tr>
            </thead>
            <tbody>
    """
    for m in matching:
        star = '<span style="color:%s;font-size:0.62rem;font-weight:700;vertical-align:super;">&#9733;</span>' % _CS["red"] if m.get('star_mark') else ''
        table_html += f"""
                <tr style="border-bottom:1px solid rgba(30,48,80,.5);">
                    <td style="padding:10px 16px;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:{_CS['muted']};vertical-align:top;">{m['seq']:02d}</td>
                    <td style="padding:10px 16px;font-size:0.72rem;color:{_CS['muted']};vertical-align:top;">{m.get('category', '')}</td>
                    <td style="padding:10px 16px;font-size:0.82rem;color:{_CS['text']};vertical-align:top;">{m.get('bid_req', '')}{star}</td>
                    <td style="padding:10px 16px;font-size:0.82rem;color:{_CS['text']};vertical-align:top;">{m.get('xunfei_spec', '')}</td>
                    <td style="padding:10px 16px;vertical-align:top;">{_deviation_badge(m['deviation'])}</td>
                    <td style="padding:10px 16px;vertical-align:top;">{_method_badge(m.get('match_method', ''))}</td>
                </tr>"""

    table_html += """
            </tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

    # ── Suggestions ──
    negative_items = [m for m in result['matching'] if m['deviation'] in ('negative_wording', 'negative_real')]
    if negative_items:
        st.markdown("### Response Suggestions")

        for item in negative_items:
            dev = item.get('deviation', '')
            is_wording = dev == 'negative_wording'
            p_tag = "P0" if is_wording else "P1"
            p_label = "Rewording" if is_wording else "Challenge"
            p_color = _CS["green"] if is_wording else _CS["amber"]
            p_bg = "rgba(34,197,94,.15)" if is_wording else "rgba(255,181,71,.15)"
            title = "Fixable Wording" if is_wording else "Genuinely Unsatisfied"

            with st.expander(f"#{item['seq']} {item.get('name', '')} — {title} · {item.get('match_method', '')}"):
                c_left, c_right = st.columns([1, 1])
                with c_left:
                    st.markdown(f"""
                    <div style="font-size:0.65rem;color:{_CS['muted']};text-transform:uppercase;margin-bottom:4px;">Bidding Requirement</div>
                    <div style="color:{_CS['text']};font-size:0.82rem;margin-bottom:12px;line-height:1.5;">{item.get('bid_req', '')}</div>
                    """, unsafe_allow_html=True)
                with c_right:
                    st.markdown(f"""
                    <div style="font-size:0.65rem;color:{_CS['muted']};text-transform:uppercase;margin-bottom:4px;">iFLYTEK Parameter</div>
                    <div style="color:{_CS['text']};font-size:0.82rem;margin-bottom:12px;line-height:1.5;">{item.get('xunfei_spec', '')}</div>
                    """, unsafe_allow_html=True)

                if item.get('detail'):
                    st.markdown(f"""
                    <div style="font-size:0.65rem;color:{_CS['muted']};text-transform:uppercase;margin-bottom:4px;">Analysis</div>
                    <div style="color:#BCC8DC;font-size:0.78rem;line-height:1.6;margin-bottom:12px;">{item.get('detail', '')}</div>
                    """, unsafe_allow_html=True)

                if item.get('suggestion'):
                    st.markdown(f"""
                    <div style="background:{_CS['surface']};border:1px solid {_CS['border']};border-radius:10px;padding:12px 14px;margin-top:8px;">
                        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                            <span style="background:{p_bg};color:{p_color};padding:2px 8px;border-radius:4px;font-size:0.62rem;font-weight:700;font-family:'JetBrains Mono',monospace;">{p_tag}</span>
                            <span style="font-weight:600;font-size:0.75rem;color:{_CS['text']};">{p_label}</span>
                        </div>
                        <div style="color:#BCC8DC;font-size:0.78rem;line-height:1.7;">{item['suggestion']}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.success("All parameters are positive deviations.")


def main():
    if 'page' not in st.session_state:
        st.session_state.page = "upload"
    if 'result' not in st.session_state:
        st.session_state.result = None
    if st.session_state.page == "upload":
        page_upload()
    else:
        page_compare()


if __name__ == "__main__":
    main()
