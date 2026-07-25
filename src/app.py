"""Streamlit UI: 2 pages -- Upload + Controller Result, Comparison Table with Advice."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import streamlit as st
import pandas as pd
from engine import run_analysis

st.set_page_config(page_title="Parameter Agent", layout="wide")


def page_upload():
    st.title("Parameter Agent - Bidding Analysis")
    st.caption("Upload a bidding document, identify the controlling vendor, compare parameters against iFLYTEK.")

    col1, col2 = st.columns(2)
    with col1:
        uploaded = st.file_uploader("Upload bidding document (JSON)", type=["json"], key="bid_upload")
    with col2:
        use_sample = st.button("Use Sample Bidding Document", type="secondary")

    if not uploaded and not use_sample:
        st.info("Upload a JSON bidding file or click 'Use Sample Bidding Document' to start.")
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

    st.subheader("Analysis Result")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Controlling Vendor", ctrl['vendor'])
    c2.metric("Confidence", f"{ctrl['confidence']:.0%}")
    c3.metric("Unique Feature Hits", f"{len(ctrl['hits'])}/{summary['total']}")
    c4.metric("Anomalies", len(ctrl['anomalies']))

    if ctrl['scores']:
        st.subheader("Vendor Unique Feature Distribution")
        score_df = pd.DataFrame({'Vendor': list(ctrl['scores'].keys()), 'Unique Features': list(ctrl['scores'].values())})
        st.bar_chart(score_df.set_index('Vendor'))

    st.subheader("Deviation Overview")
    d1, d2, d3 = st.columns(3)
    d1.metric("Green (Positive)", summary['positive'])
    d2.metric("Yellow (Fixable)", summary['negative_wording'])
    d3.metric("Red (Unsatisfied)", summary['negative_real'])

    if st.button("View Detailed Comparison ->", type="primary"):
        st.rerun()


def page_compare():
    st.title("Parameter Comparison")

    if 'result' not in st.session_state or st.session_state.result is None:
        st.warning("No analysis result. Please upload a bidding document first.")
        if st.button("<- Back to Upload"):
            st.session_state.page = "upload"
            st.rerun()
        return

    result = st.session_state.result

    if st.button("<- Back to Upload"):
        st.session_state.page = "upload"
        st.rerun()

    filter_option = st.selectbox("Filter:", ["All", "Green (Positive)", "Yellow (Fixable)", "Red (Unsatisfied)"])
    matching = result['matching']
    if filter_option.startswith("Green"):
        matching = [m for m in matching if m['deviation'] == 'positive']
    elif filter_option.startswith("Yellow"):
        matching = [m for m in matching if m['deviation'] == 'negative_wording']
    elif filter_option.startswith("Red"):
        matching = [m for m in matching if m['deviation'] == 'negative_real']

    rows = []
    for m in matching:
        dev_map = {'positive': ':green[Green]', 'negative_wording': ':orange[Yellow]', 'negative_real': ':red[Red]'}
        rows.append({
            '#': m['seq'],
            'Category': m.get('category', ''),
            'Bidding Requirement': m.get('bid_req', ''),
            'iFLYTEK Parameter': m.get('xunfei_spec', ''),
            'Deviation': dev_map.get(m['deviation'], '?'),
            'Method': m.get('match_method', ''),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.subheader("Advice Details")
    negative_items = [m for m in result['matching'] if m['deviation'] in ('negative_wording', 'negative_real')]
    if negative_items:
        for item in negative_items:
            label = item.get('deviation', '')
            if label == 'negative_wording':
                label = 'Yellow - Fixable Wording'
            else:
                label = 'Red - Genuinely Unsatisfied'
            with st.expander(f"#{item['seq']} {item.get('name', '')} - {label} | Method: {item.get('match_method', '')}"):
                st.markdown(f"**Bidding Requirement:** {item.get('bid_req', '')}")
                st.markdown(f"**iFLYTEK Parameter:** {item.get('xunfei_spec', '')}")
                st.markdown(f"**Analysis:** {item.get('detail', '')}")
                if item.get('suggestion'):
                    st.info(f"**Suggestion:** {item['suggestion']}")
    else:
        st.success("All parameters are positive deviations. No negative items found.")


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
