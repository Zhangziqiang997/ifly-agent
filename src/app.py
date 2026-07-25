"""Streamlit UI — Dark Industrial Warmth. 2 pages: Upload + Controller, Comparison + Advice."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import streamlit as st
import pandas as pd
from engine import run_analysis

st.set_page_config(page_title="Parameter Agent", layout="wide")

# ═══════════════════════════════════════════════════════════════
# CSS — Dark Industrial Warmth
# Palette: bg #1a1a1a | card #242424 | amber #f59e0b | teal #0891b2
# Fonts: system Chinese sans-serif, NO Inter/Roboto/Arial
# ═══════════════════════════════════════════════════════════════
CSS = """
<style>
/* ── Base ── */
.stApp, .main { background: #1a1a1a; }
section[data-testid="stSidebar"] { background: #141414; border-right: 1px solid #333; }

/* ── Typography ── */
h1, h2, h3, h4, .stMarkdown, .stCaption, .stMetric label, .stDataFrame, .stSelectbox label {
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", "Source Han Sans CN", sans-serif !important;
    color: #e5e5e5;
}
h1 { font-size: 1.6rem !important; font-weight: 800 !important; letter-spacing: 0.02em; color: #f59e0b !important; text-transform: uppercase; }
h2 { font-size: 1.1rem !important; font-weight: 700 !important; color: #d4d4d4 !important; border-bottom: 1px solid #333; padding-bottom: 8px; margin-top: 28px; }
h3 { font-size: 0.95rem !important; font-weight: 600 !important; color: #a3a3a3 !important; }
.stCaption { color: #737373 !important; }

/* ── Cards / Containers ── */
div[data-testid="stMetric"] {
    background: #242424; border: 1px solid #333; border-radius: 0; padding: 16px 20px;
}
div[data-testid="stMetric"] label { color: #a3a3a3 !important; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #f59e0b !important; font-size: 1.6rem !important; font-weight: 700; }

/* ── Buttons ── */
.stButton > button {
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif !important;
    border-radius: 0 !important; border: 1px solid #f59e0b !important;
    background: transparent !important; color: #f59e0b !important;
    font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; font-size: 0.8rem;
    padding: 8px 24px; transition: all 0.15s;
}
.stButton > button:hover { background: #f59e0b !important; color: #1a1a1a !important; border-color: #f59e0b !important; }

/* Primary button */
.stButton > button[kind="primary"] {
    background: #f59e0b !important; color: #1a1a1a !important; border-color: #f59e0b !important;
}
.stButton > button[kind="primary"]:hover { background: #fbbf24 !important; }

/* ── Metrics in columns - unequal emphasis ── */
div[data-testid="column"]:nth-child(1) div[data-testid="stMetric"] { border-left: 3px solid #f59e0b; }
div[data-testid="column"]:nth-child(2) div[data-testid="stMetric"] { border-left: 3px solid #0891b2; }
div[data-testid="column"]:nth-child(3) div[data-testid="stMetric"] { border-left: 3px solid #d97706; }
div[data-testid="column"]:nth-child(4) div[data-testid="stMetric"] { border-left: 3px solid #737373; }

/* ── Dataframe / Table ── */
.stDataFrame { background: #242424; border: 1px solid #333; border-radius: 0; }
.stDataFrame th { background: #1a1a1a !important; color: #f59e0b !important; font-weight: 600; border-bottom: 2px solid #f59e0b !important; }
.stDataFrame td { color: #d4d4d4 !important; border-bottom: 1px solid #2a2a2a !important; }
.stDataFrame tr:nth-child(even) td { background: #1e1e1e; }
.stDataFrame tr:hover td { background: #2a2a2a !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #242424 !important; border: 1px solid #333 !important; border-radius: 0 !important;
    font-family: "PingFang SC", "Microsoft YaHei", sans-serif !important; color: #d4d4d4 !important;
}
.streamlit-expanderHeader:hover { border-color: #f59e0b !important; }
.streamlit-expanderContent { background: #1e1e1e; border: 1px solid #333; border-top: none; }

/* ── Selectbox ── */
div[data-testid="stSelectbox"] div { color: #d4d4d4 !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #f59e0b !important; }

/* ── Alert boxes ── */
.stAlert { border-radius: 0 !important; border-left: 3px solid; }
div[data-testid="stInfo"] { background: #1e293b; border-color: #0891b2; color: #cbd5e1; }
div[data-testid="stSuccess"] { background: #1a2e1a; border-color: #22c55e; }
div[data-testid="stWarning"] { background: #2e231a; border-color: #f59e0b; }
div[data-testid="stError"] { background: #2e1a1a; border-color: #ef4444; }

/* ── File uploader ── */
div[data-testid="stFileUploader"] section { background: #242424 !important; border: 1px dashed #444 !important; border-radius: 0 !important; }

/* ── Chart ── */
div[data-testid="stVegaLiteChart"] { background: #242424; border: 1px solid #333; }

/* ── Block container spacing ── */
div[data-testid="stVerticalBlock"] { gap: 0.6rem; }
</style>
"""


def _inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# Custom card component — Streamlit can't do true custom cards,
# but we can wrap metrics with styled containers
# ═══════════════════════════════════════════════════════════════
def _big_number(col, value, label, accent="#f59e0b"):
    """Render a bold KPI inside a dark card with left accent border."""
    col.markdown(f"""
    <div style="background:#242424; border-left:3px solid {accent}; padding:12px 16px; margin:4px 0;">
        <div style="font-size:1.5rem;font-weight:800;color:{accent};">{value}</div>
        <div style="font-size:0.65rem;color:#a3a3a3;text-transform:uppercase;letter-spacing:0.06em;">{label}</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# Page 1 — Upload & Controller Result
# ═══════════════════════════════════════════════════════════════
def page_upload():
    _inject_css()

    # Asymmetric header — large title hanging left, subtitle indented
    st.markdown("""
    <div style="margin:12px 0 28px 0;">
        <div style="font-size:2rem;font-weight:900;color:#f59e0b;letter-spacing:0.03em;text-transform:uppercase;">Parameter Agent</div>
        <div style="font-size:0.8rem;color:#525252;padding-left:4px;">AI-drive bidding analysis for smart blackboard · iFLYTEK</div>
    </div>
    """, unsafe_allow_html=True)

    # Two-column asymmetric upload area — left wider
    left, right = st.columns([1.6, 1])
    with left:
        uploaded = st.file_uploader("Upload bidding document", type=["json"], key="bid_upload",
                                     label_visibility="collapsed")
    with right:
        use_sample = st.button("Use Sample Bid", type="primary", use_container_width=True)

    if not uploaded and not use_sample:
        # Empty state — geometric placeholder
        st.markdown("""
        <div style="background:#242424;border:1px dashed #333;padding:48px 32px;text-align:center;margin-top:16px;">
            <div style="font-size:2.5rem;margin-bottom:12px;">&#9634;&#9634;&#9634;</div>
            <div style="font-size:0.85rem;color:#737373;">Upload a JSON bidding file or click <span style="color:#f59e0b;">Use Sample Bid</span> to start</div>
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
    st.session_state.page = "compare"

    ctrl = result['controller']
    summary = result['summary']

    # ── Controller identity — bold asymmetric layout ──
    st.markdown('<div style="margin-top:24px;"></div>', unsafe_allow_html=True)

    # Dominant controller card
    st.markdown(f"""
    <div style="background:#242424;border:1px solid #333;padding:20px 24px;margin-bottom:16px;">
        <div style="display:flex;align-items:baseline;gap:16px;">
            <div style="font-size:0.65rem;color:#737373;text-transform:uppercase;letter-spacing:0.1em;">Controlling Vendor</div>
            <div style="font-size:1.8rem;font-weight:900;color:#f59e0b;">{ctrl['vendor']}</div>
            <div style="font-size:0.8rem;color:#0891b2;font-weight:600;">{ctrl['confidence']:.0%} confidence</div>
        </div>
        <div style="font-size:0.7rem;color:#525252;margin-top:8px;">
            {len(ctrl['hits'])} unique feature hits / {summary['total']} items · {len(ctrl['anomalies'])} anomalies
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Deviation overview — 3 asymmetric columns with distinct weights
    d1, d2, d3 = st.columns([1, 0.8, 0.8])
    _big_number(d1, summary['positive'], "Green · Satisfied", "#22c55e")
    _big_number(d2, summary['negative_wording'], "Yellow · Fixable", "#f59e0b")
    _big_number(d3, summary['negative_real'], "Red · Unsatisfied", "#ef4444")

    # Vendor score bar chart
    if ctrl['scores']:
        st.markdown("### Vendor Feature Hits")
        score_df = pd.DataFrame({
            'Vendor': list(ctrl['scores'].keys()),
            'Unique Features': list(ctrl['scores'].values())
        })
        st.bar_chart(score_df.set_index('Vendor'), use_container_width=True)

    st.markdown('<div style="margin-top:16px;"></div>', unsafe_allow_html=True)
    if st.button("View Detailed Comparison", type="primary"):
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# Page 2 — Comparison Table & Advice
# ═══════════════════════════════════════════════════════════════
def page_compare():
    _inject_css()

    st.markdown("""
    <div style="margin:12px 0 28px 0;">
        <div style="font-size:1.4rem;font-weight:900;color:#f59e0b;letter-spacing:0.03em;text-transform:uppercase;">Parameter Comparison</div>
    </div>
    """, unsafe_allow_html=True)

    if 'result' not in st.session_state or st.session_state.result is None:
        st.warning("No analysis result. Please upload a bidding document first.")
        if st.button("Back to Upload"):
            st.session_state.page = "upload"
            st.rerun()
        return

    result = st.session_state.result

    # Navigation + filter in one row, asymmetric
    nav_left, nav_right = st.columns([0.5, 2])
    with nav_left:
        if st.button("Back", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()
    with nav_right:
        filter_option = st.selectbox("Filter by status:", [
            "All Parameters",
            "Positive (Green)",
            "Fixable Wording (Yellow)",
            "Unsatisfied (Red)"
        ], label_visibility="collapsed")

    matching = result['matching']
    if "Positive" in filter_option:
        matching = [m for m in matching if m['deviation'] == 'positive']
    elif "Fixable" in filter_option:
        matching = [m for m in matching if m['deviation'] == 'negative_wording']
    elif "Unsatisfied" in filter_option:
        matching = [m for m in matching if m['deviation'] == 'negative_real']

    # ── Data table with custom rendering ──
    rows = []
    for m in matching:
        dev = m['deviation']
        if dev == 'positive':
            badge = '<span style="background:#1a2e1a;color:#22c55e;padding:2px 8px;font-size:0.7rem;font-weight:600;text-transform:uppercase;">GREEN</span>'
        elif dev == 'negative_wording':
            badge = '<span style="background:#2e231a;color:#f59e0b;padding:2px 8px;font-size:0.7rem;font-weight:600;text-transform:uppercase;">YELLOW</span>'
        else:
            badge = '<span style="background:#2e1a1a;color:#ef4444;padding:2px 8px;font-size:0.7rem;font-weight:600;text-transform:uppercase;">RED</span>'

        method = m.get('match_method', '')
        method_badge = '<span style="color:#0891b2;font-size:0.7rem;">PROGRAM</span>' if method == 'program' else '<span style="color:#a78bfa;font-size:0.7rem;">AI</span>'

        rows.append({
            '#': m['seq'],
            'Category': m.get('category', ''),
            'Bidding Requirement': m.get('bid_req', ''),
            'iFLYTEK Parameter': m.get('xunfei_spec', ''),
            'Deviation': badge,
            'Method': method_badge,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={
                     'Bidding Requirement': st.column_config.TextColumn(width='large'),
                     'iFLYTEK Parameter': st.column_config.TextColumn(width='large'),
                     'Deviation': st.column_config.TextColumn(width='small'),
                     'Method': st.column_config.TextColumn(width='small'),
                 })

    # ── Advice cards — dark expanders with custom badges ──
    st.markdown("### Advice for Negative Deviations")

    negative_items = [m for m in result['matching'] if m['deviation'] in ('negative_wording', 'negative_real')]
    if negative_items:
        for item in negative_items:
            dev = item.get('deviation', '')
            if dev == 'negative_wording':
                accent = "#f59e0b"
                tag = "FIXABLE"
            else:
                accent = "#ef4444"
                tag = "UNSATISFIED"

            method = item.get('match_method', '?')
            title = f"#{item['seq']} {item.get('name', '')} [{tag}] · {method}"

            with st.expander(title):
                c_left, c_right = st.columns([1, 1])
                with c_left:
                    st.markdown(f"""
                    <div style="margin-bottom:8px;">
                        <div style="font-size:0.65rem;color:#737373;text-transform:uppercase;">Bidding Requirement</div>
                        <div style="color:#d4d4d4;font-size:0.85rem;">{item.get('bid_req', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c_right:
                    st.markdown(f"""
                    <div style="margin-bottom:8px;">
                        <div style="font-size:0.65rem;color:#737373;text-transform:uppercase;">iFLYTEK Parameter</div>
                        <div style="color:#d4d4d4;font-size:0.85rem;">{item.get('xunfei_spec', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="font-size:0.65rem;color:#737373;text-transform:uppercase;margin-top:8px;">Analysis</div>
                <div style="color:#a3a3a3;font-size:0.8rem;">{item.get('detail', '')}</div>
                """, unsafe_allow_html=True)

                if item.get('suggestion'):
                    st.markdown(f"""
                    <div style="background:#1e1a1a;border-left:3px solid {accent};padding:10px 14px;margin-top:10px;">
                        <div style="font-size:0.65rem;color:#737373;text-transform:uppercase;">Suggestion</div>
                        <div style="color:#e5e5e5;font-size:0.85rem;">{item['suggestion']}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.success("All parameters are positive deviations — nothing to worry about.")


# ═══════════════════════════════════════════════════════════════
# Main
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
