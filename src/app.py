"""Streamlit UI — matches prototype_design.html dark navy aesthetic."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import streamlit as st
import pandas as pd
from engine import run_analysis

st.set_page_config(page_title="Parameter Agent", layout="wide")

# ═══════════════════════════════════════════════════════════════
# CSS — Match prototype: navy bg, cyan accent, JetBrains Mono + Noto Sans SC
# ═══════════════════════════════════════════════════════════════
CSS = """
<style>
/* ── Root variables ── */
:root {
    --bg: #0A1628; --surface: #0F1E35; --card: #162035; --border: #1E3050;
    --cyan: #00D4FF; --cyan-dim: rgba(0,212,255,.12); --amber: #FFB547;
    --red: #FF5C5C; --green: #22C55E; --text: #E8EDF5; --muted: #6B82A0;
}

/* ── Base ── */
.stApp, .stMain { background: var(--bg); }
div[data-testid="stAppViewContainer"] { background: var(--bg); }
section[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Typography ── */
h1, h2, h3, h4, p, span, div, label, .stMarkdown, .stCaption, .stDataFrame, .stSelectbox, .stMetric {
    font-family: "Inter", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif !important;
}
h1 { font-size: 1.4rem !important; font-weight: 700 !important; color: var(--text) !important; }
h2 { font-size: 1.1rem !important; font-weight: 600 !important; color: var(--text) !important; margin-top: 28px; }
h3 { font-size: 0.9rem !important; font-weight: 600 !important; }
.stCaption { color: var(--muted) !important; font-size: 0.8rem; }
p, li, span, div { color: var(--text); }

/* ── Sidebar ── */
section[data-testid="stSidebar"] > div:first-child { background: var(--surface); }
.st-emotion-cache-1gwvyta { background: var(--surface); }
div[data-testid="stSidebarNav"] a { color: var(--muted) !important; }
div[data-testid="stSidebarNav"] a:hover { color: var(--cyan) !important; background: var(--cyan-dim) !important; }
div[data-testid="stSidebarNav"] a[aria-current="page"] { color: var(--cyan) !important; background: var(--cyan-dim) !important; }

/* ── Buttons ── */
.stButton > button {
    font-family: "Inter", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif !important;
    border-radius: 8px !important; border: none !important;
    font-weight: 600 !important; font-size: 0.82rem !important;
    padding: 10px 22px !important; transition: all 0.15s !important;
}
/* primary = cyan filled */
.stButton > button[kind="primary"] {
    background: var(--cyan) !important; color: #0A1628 !important;
}
.stButton > button[kind="primary"]:hover { background: #33dcff !important; }
/* secondary = transparent + border */
.stButton > button[kind="secondary"] {
    background: transparent !important; border: 1px solid var(--border) !important; color: var(--text) !important;
}
.stButton > button[kind="secondary"]:hover { border-color: var(--cyan) !important; color: var(--cyan) !important; }
/* tertiary (back nav) */
.stButton > button:not([kind]):not([kind="primary"]):not([kind="secondary"]) {
    background: transparent !important; border: 1px solid var(--border) !important; color: var(--muted) !important;
}
.stButton > button:not([kind]):hover { border-color: var(--cyan) !important; color: var(--cyan) !important; }

/* ── Cards / Containers ── */
div[data-testid="stMetric"] {
    background: var(--card) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; padding: 16px 18px !important;
}
div[data-testid="stMetric"] label { color: var(--muted) !important; font-size: 0.68rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-size: 1.6rem !important; font-weight: 700 !important;
    font-family: "JetBrains Mono", "Cascadia Code", "Fira Code", monospace !important;
}

/* ── Dataframe / Table ── */
div[data-testid="stTable"], .stDataFrame {
    background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 12px !important;
}
.stDataFrame th, div[data-testid="stTable"] th {
    background: var(--surface) !important; color: var(--muted) !important;
    font-size: 0.68rem !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.06em !important;
    border-bottom: 1px solid var(--border) !important; padding: 10px 16px !important;
}
.stDataFrame td, div[data-testid="stTable"] td {
    padding: 12px 16px !important; border-bottom: 1px solid rgba(30,48,80,.6) !important;
    font-size: 0.82rem !important; color: var(--text) !important;
}
.stDataFrame tr:last-child td { border-bottom: none !important; }
.stDataFrame tr:hover td { background: rgba(255,255,255,.02) !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; font-family: "Inter", "Noto Sans SC", sans-serif !important;
    color: var(--text) !important; font-size: 0.82rem !important; font-weight: 600 !important;
}
.streamlit-expanderHeader:hover { border-color: var(--cyan) !important; }
.streamlit-expanderContent { background: var(--surface) !important; border: 1px solid var(--border) !important; border-top: none !important; border-radius: 0 0 10px 10px !important; }

/* ── Selectbox ── */
div[data-testid="stSelectbox"] select, .stSelectbox div {
    color: var(--text) !important; background: var(--card) !important;
    border: 1px solid var(--border) !important; border-radius: 8px !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--cyan) !important; border-right-color: var(--cyan) !important; }

/* ── Alert boxes ── */
div[data-testid="stAlert"] {
    border-radius: 10px !important; border: 1px solid var(--border) !important;
}
div[data-testid="stInfo"] { background: rgba(0,212,255,.08); }
div[data-testid="stSuccess"] { background: rgba(34,197,94,.08); }
div[data-testid="stWarning"] { background: rgba(255,181,71,.08); }
div[data-testid="stError"] { background: rgba(255,92,92,.08); }

/* ── File uploader ── */
div[data-testid="stFileUploader"] section {
    background: var(--surface) !important; border: 2px dashed var(--border) !important;
    border-radius: 14px !important;
}
div[data-testid="stFileUploader"]:hover section { border-color: var(--cyan) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }
</style>
"""


def _inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# Page 1 — Upload & Dashboard
# ═══════════════════════════════════════════════════════════════
def page_upload():
    _inject_css()

    st.title("Upload Bidding Document")
    st.caption("Upload a JSON bidding file or use the sample to run 3-layer analysis.")

    col1, col2 = st.columns([1.6, 1])
    with col1:
        uploaded = st.file_uploader(
            "Drop file here or click to browse",
            type=["json"],
            key="bid_upload",
            label_visibility="collapsed"
        )
    with col2:
        use_sample = st.button("Use Sample Bid", type="primary", use_container_width=True)

    if not uploaded and not use_sample:
        # Empty state matching prototype's upload-zone geometry
        st.markdown("""
        <div style="
            background:var(--surface); border:2px dashed #1E3050; border-radius:14px;
            padding:56px 40px; text-align:center; transition:.2s;
        ">
            <div style="font-size:48px;margin-bottom:16px;">&#128196;</div>
            <div style="font-size:1.1rem;font-weight:600;color:#E8EDF5;margin-bottom:6px;">
                Drag &amp; drop file here, or click to select
            </div>
            <div style="font-size:0.8rem;color:#6B82A0;">
                Supported formats: .json (bidding document)
            </div>
            <div style="display:flex;gap:10px;justify-content:center;margin-top:14px;">
                <span style="background:rgba(255,255,255,.05);border:1px solid #1E3050;border-radius:6px;
                    padding:4px 12px;font-size:0.65rem;font-family:'JetBrains Mono',monospace;color:#6B82A0;">.json</span>
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

    # ── Page subtitle bar ──
    st.markdown(f"""
    <div style="margin:12px 0 20px 0;">
        <div style="font-size:1.3rem;font-weight:700;color:#E8EDF5;">Analysis Report</div>
        <div style="font-size:0.75rem;color:#6B82A0;">
            {result.get('project', 'Bidding Project')} · {summary['total']} parameters analyzed
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats row (4-col) ──
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("Total Parameters", summary['total'])
    with s2:
        st.metric("Positive (Green)", summary['positive'])
    with s3:
        st.metric("Fixable (Yellow)", summary['negative_wording'])
    with s4:
        st.metric("Unsatisfied (Red)", summary['negative_real'])

    # ── Verdict + Chart row ──
    v_left, v_right = st.columns([1.2, 2])

    with v_left:
        # Verdict card — matching prototype's verdict-card
        confidence_pct = int(ctrl['confidence'] * 100)
        verdict_label = "Highly Suspicious" if confidence_pct > 60 else ("Partial Bias" if confidence_pct > 30 else "Low Bias")
        verdict_color = "var(--red)" if confidence_pct > 60 else ("var(--amber)" if confidence_pct > 30 else "var(--muted)")

        st.markdown(f"""
        <div style="background:var(--card);border:1px solid var(--border);border-radius:12px;padding:22px;">
            <div style="font-size:0.68rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px;">
                Controlling Vendor
            </div>
            <div style="font-size:1.4rem;font-weight:700;color:#fff;">{ctrl['vendor']}</div>
            <div style="font-size:0.8rem;color:var(--muted);margin-bottom:14px;">Bidding controller target</div>

            <div style="display:flex;align-items:center;gap:16px;margin:8px 0;">
                <div style="
                    width:80px;height:80px;border-radius:50%;
                    border:5px solid var(--border);
                    border-top-color:{verdict_color};border-right-color:{verdict_color};
                    transform:rotate(-45deg);
                    display:flex;align-items:center;justify-content:center;
                ">
                    <span style="
                        transform:rotate(45deg);font-family:'JetBrains Mono',monospace;
                        font-size:1rem;font-weight:700;color:{verdict_color};
                    ">{confidence_pct}%</span>
                </div>
                <div>
                    <div style="font-size:1.6rem;font-weight:700;font-family:'JetBrains Mono',monospace;color:{verdict_color};">{confidence_pct}%</div>
                    <div style="font-size:0.7rem;color:var(--muted);">Unique feature hit rate</div>
                    <div style="margin-top:8px;">
                        <span style="
                            display:inline-flex;align-items:center;gap:6px;
                            background:rgba(255,92,92,.12);border:1px solid rgba(255,92,92,.3);
                            color:{verdict_color};border-radius:20px;padding:4px 12px;
                            font-size:0.72rem;font-weight:600;
                        ">&#9888; {verdict_label}</span>
                    </div>
                </div>
            </div>

            <div style="font-size:0.68rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin:16px 0 8px 0;">
                Unique Feature Hits
            </div>
            <div style="display:flex;flex-direction:column;gap:6px;max-height:200px;overflow-y:auto;">
        """, unsafe_allow_html=True)

        for hit in ctrl.get('hits', []):
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:8px;font-size:0.75rem;
                padding:7px 10px;background:var(--surface);border-radius:6px;border:1px solid var(--border);">
                <div style="width:6px;height:6px;background:var(--red);border-radius:50%;margin-top:4px;flex-shrink:0;"></div>
                <div style="line-height:1.5;">
                    <span style="color:var(--muted);font-family:'JetBrains Mono',monospace;">#{hit['seq']}</span>
                    {hit['param_name']}
                    <span style="color:var(--muted);font-size:0.7rem;"> &middot; {hit['hit_vendor']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

    with v_right:
        # Bar chart
        if ctrl['scores']:
            st.markdown("""
            <div style="background:var(--card);border:1px solid var(--border);border-radius:12px;padding:22px;">
                <div style="font-size:0.68rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:14px;">
                    Vendor Unique Feature Distribution
                </div>
            """, unsafe_allow_html=True)
            score_df = pd.DataFrame({
                'Vendor': list(ctrl['scores'].keys()),
                'Unique Features': list(ctrl['scores'].values())
            })
            st.bar_chart(score_df.set_index('Vendor'), use_container_width=True)

            st.markdown("""
            <div style="display:flex;gap:18px;margin-top:10px;font-size:0.75rem;">
                <span style="display:flex;align-items:center;gap:6px;">
                    <span style="width:10px;height:10px;background:var(--red);border-radius:2px;display:inline-block;"></span>
                    Unique Feature Hits per Vendor
                </span>
            </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Deviations summary ──
    st.markdown("### Deviation Overview")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.metric("Green (Positive)", summary['positive'])
    with d2:
        st.metric("Yellow (Fixable Wording)", summary['negative_wording'])
    with d3:
        st.metric("Red (Genuinely Unsatisfied)", summary['negative_real'])

    # ── Navigation ──
    st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)
    if st.button("View Detailed Comparison", type="primary"):
        st.session_state.page = "compare"
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# Page 2 — Comparison Table & Advice
# ═══════════════════════════════════════════════════════════════
def page_compare():
    _inject_css()

    st.title("Parameter Comparison")

    if 'result' not in st.session_state or st.session_state.result is None:
        st.warning("No analysis result. Please upload a bidding document first.")
        if st.button("Back to Upload"):
            st.session_state.page = "upload"
            st.rerun()
        return

    result = st.session_state.result
    summary = result['summary']

    # Subtitle
    st.markdown(f"""
    <div style="font-size:0.75rem;color:var(--muted);margin-bottom:20px;">
        {result.get('project', 'Bidding Project')} · {summary['total']} parameters ·
        Controller: <span style="color:var(--cyan);">{result['controller']['vendor']}</span>
        ({result['controller']['confidence']:.0%} confidence)
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
            "Filter",
            ["All Parameters", "Green (Positive)", "Yellow (Fixable Wording)", "Red (Unsatisfied)"],
            label_visibility="collapsed"
        )

    matching = result['matching']
    if "Green" in filter_option:
        matching = [m for m in matching if m['deviation'] == 'positive']
    elif "Yellow" in filter_option:
        matching = [m for m in matching if m['deviation'] == 'negative_wording']
    elif "Red" in filter_option:
        matching = [m for m in matching if m['deviation'] == 'negative_real']

    # ── Table ──
    rows = []
    for m in matching:
        dev = m['deviation']
        if dev == 'positive':
            badge = f'<span style="display:inline-flex;align-items:center;gap:4px;font-size:0.68rem;font-weight:600;padding:3px 9px;border-radius:5px;background:rgba(34,197,94,.12);color:{CSS_COLORS["green"]};border:1px solid rgba(34,197,94,.25);">Green</span>'
        elif dev == 'negative_wording':
            badge = f'<span style="display:inline-flex;align-items:center;gap:4px;font-size:0.68rem;font-weight:600;padding:3px 9px;border-radius:5px;background:rgba(255,181,71,.12);color:{CSS_COLORS["amber"]};border:1px solid rgba(255,181,71,.25);">Yellow</span>'
        else:
            badge = f'<span style="display:inline-flex;align-items:center;gap:4px;font-size:0.68rem;font-weight:600;padding:3px 9px;border-radius:5px;background:rgba(255,92,92,.12);color:{CSS_COLORS["red"]};border:1px solid rgba(255,92,92,.25);">Red</span>'

        method_label = "AI" if m.get('match_method') == 'ai_semantic' else "PROGRAM"
        method_color = "#A78BFA" if m.get('match_method') == 'ai_semantic' else "var(--cyan)"
        method_badge = f'<span style="font-size:0.62rem;font-family:JetBrains Mono,monospace;background:var(--surface);border:1px solid var(--border);padding:2px 6px;border-radius:4px;color:{method_color};">{method_label}</span>'

        rows.append({
            '#': f'<span style="font-family:JetBrains Mono,monospace;font-size:0.75rem;color:var(--muted);">{m["seq"]:02d}</span>',
            'Category': f'<span style="font-size:0.72rem;color:var(--muted);">{m.get("category", "")}</span>',
            'Bidding Requirement': m.get('bid_req', ''),
            'iFLYTEK Spec': m.get('xunfei_spec', ''),
            'Deviation': badge,
            'Method': method_badge,
        })

    # Render table as markdown to handle inline HTML
    st.markdown("""
    <div style="background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 0 0 0;">
        <div style="display:flex;align-items:center;gap:10px;padding:0 18px 10px 18px;border-bottom:1px solid var(--border);">
            <div style="font-size:0.9rem;font-weight:600;color:var(--text);margin-right:auto;">Parameter Comparison Table</div>
    """, unsafe_allow_html=True)

    # Filter pill buttons
    st.markdown("</div></div><br>", unsafe_allow_html=True)

    df = pd.DataFrame([
        {
            '#': f"{m['seq']:02d}",
            'Category': m.get('category', ''),
            'Bidding Requirement': m.get('bid_req', ''),
            'iFLYTEK Spec': m.get('xunfei_spec', ''),
            'Deviation': m['deviation'],
            'Method': m.get('match_method', ''),
        }
        for m in matching
    ])
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={
                     '#': st.column_config.TextColumn(width='small'),
                     'Category': st.column_config.TextColumn(width='small'),
                     'Bidding Requirement': st.column_config.TextColumn(width='large'),
                     'iFLYTEK Spec': st.column_config.TextColumn(width='large'),
                     'Deviation': st.column_config.TextColumn(width='small'),
                     'Method': st.column_config.TextColumn(width='small'),
                 })

    # ── Advice for negative deviations ──
    negative_items = [m for m in result['matching'] if m['deviation'] in ('negative_wording', 'negative_real')]
    if negative_items:
        st.markdown("### Response Suggestions")

        for item in negative_items:
            dev = item.get('deviation', '')
            is_wording = dev == 'negative_wording'
            accent = "var(--amber)" if is_wording else "var(--red)"
            p_tag = "P0" if is_wording else "P1"
            p_class = "background:rgba(34,197,94,.15);color:var(--green);" if p_tag == "P0" else "background:rgba(255,181,71,.15);color:var(--amber);"
            title = "Fixable Wording" if is_wording else "Genuinely Unsatisfied"

            with st.expander(f"#{item['seq']} {item.get('name', '')} — {title} · {item.get('match_method', '')}"):
                c_left, c_right = st.columns([1, 1])
                with c_left:
                    st.markdown(f"""
                    <div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;margin-bottom:4px;">
                        Bidding Requirement
                    </div>
                    <div style="color:var(--text);font-size:0.82rem;margin-bottom:12px;">
                        {item.get('bid_req', '')}
                    </div>
                    """, unsafe_allow_html=True)
                with c_right:
                    st.markdown(f"""
                    <div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;margin-bottom:4px;">
                        iFLYTEK Parameter
                    </div>
                    <div style="color:var(--text);font-size:0.82rem;margin-bottom:12px;">
                        {item.get('xunfei_spec', '')}
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;margin-bottom:4px;">
                    Analysis
                </div>
                <div style="color:#BCC8DC;font-size:0.78rem;line-height:1.6;margin-bottom:10px;">
                    {item.get('detail', '')}
                </div>
                """, unsafe_allow_html=True)

                if item.get('suggestion'):
                    st.markdown(f"""
                    <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 14px;">
                        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                            <span style="{p_class}padding:2px 8px;border-radius:4px;font-size:0.62rem;font-weight:700;font-family:JetBrains Mono,monospace;">{p_tag}</span>
                            <span style="font-weight:600;font-size:0.75rem;color:var(--text);">{"Rewording" if p_tag == "P0" else "Challenge Argument"}</span>
                        </div>
                        <div style="color:#BCC8DC;font-size:0.78rem;line-height:1.7;">
                            {item['suggestion']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.success("All parameters are positive deviations.")


# Colors for inline CSS (avoid f-string escaping headaches)
CSS_COLORS = {
    "green": "#22C55E",
    "amber": "#FFB547",
    "red": "#FF5C5C",
    "cyan": "#00D4FF",
    "muted": "#6B82A0",
    "text": "#E8EDF5",
    "border": "#1E3050",
    "card": "#162035",
    "surface": "#0F1E35",
}


# ═══════════════════════════════════════════════════════════════
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
