# app.py

import streamlit as st

from pathlib import Path

import json

import io

import base64

import pandas as pd

import matplotlib.pyplot as plt


from core.utils import read_file, write_file, save_json

from core.code_analysis import analyze_file

from core.formatter import get_formatted_copy, run_black


# --- Settings ---

st.set_page_config(
    page_title="AI Code Reviewer", layout="wide", initial_sidebar_state="expanded"
)


# Folders

ROOT = Path(__file__).parent

INPUTS = ROOT / "inputs"

OUTPUTS = ROOT / "outputs"

REPORTS = ROOT / "reports"

for d in (INPUTS, OUTPUTS, REPORTS):

    d.mkdir(exist_ok=True)


# Apple-style centered header (fixed alignment)
st.markdown("""
<div style="
    display: flex; 
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin-top: 25px;
    margin-bottom: 20px;
">
    <h1 style="
        color: #FFFFFFF; 
        font-size: 42px; 
        font-weight: 600;
        margin: 0;
    ">
        🔍 AI Code Reviewer
    </h1>
    <p style="
        color: #6e6e73; 
        font-size: 18px; 
        margin: 4px 0 0 0;
    ">
        Minimal & Clean Apple-Style Interface
    </p>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<style>
div[data-testid="stMetricValue"] { 
    color: #ffffff !important; 
}
div[data-testid="stMetricLabel"] { 
    color: #d0d0d0 !important; 
}
</style>
""", unsafe_allow_html=True)

# Sidebar controls

st.sidebar.header("Upload / Options")

uploaded = st.sidebar.file_uploader("Upload a Python file (.py)", type=["py"])

use_example = st.sidebar.checkbox("Use example file (example_code.py)", value=True)

run_button = st.sidebar.button("Run Analysis")


# Show example code

if use_example and not uploaded:

    sample_path = INPUTS / "example_code.py"

    if not sample_path.exists():

        sample_path.write_text("# sample file missing")

    uploaded_content = sample_path.read_text(encoding="utf-8")

else:

    uploaded_content = None


if uploaded:

    uploaded_bytes = uploaded.read()

    uploaded_content = uploaded_bytes.decode("utf-8")

    # save to inputs

    in_file = INPUTS / f"uploaded_{uploaded.name}"

    in_file.write_text(uploaded_content, encoding="utf-8")

    working_file_path = str(in_file)

elif uploaded_content is not None:

    # use example

    working_file_path = str(INPUTS / "example_code.py")

    # ensure example exists on disk

    (INPUTS / "example_code.py").write_text(uploaded_content, encoding="utf-8")

else:

    st.info("Upload a .py file or tick 'Use example file' to try the tool.")

    st.stop()


# Editor area (wide)

st.subheader("Source Code")

code_col, preview_col = st.columns([2, 1])

with code_col:

    code_text = st.text_area(
        "Edit source (optional)", value=uploaded_content or "", height=400
    )

    if st.button("Save edits to file"):

        Path(working_file_path).write_text(code_text, encoding="utf-8")

        st.success("Saved edits.")


with preview_col:

    st.markdown("**File preview**")

    st.code(code_text or read_file(working_file_path), language="python")

    st.markdown("---")

    st.markdown("**Quick actions**")

    if st.button("Download raw file"):

        b = code_text.encode("utf-8")

        b64 = base64.b64encode(b).decode()

        href = f'<a href="data:file/plain;base64,{b64}" download="code.py">Download</a>'

        st.markdown(href, unsafe_allow_html=True)


# Run analysis

if run_button:

    st.info("Running analysis — results will appear below.")

    with st.spinner("Analyzing with flake8 & radon..."):

        report = analyze_file(working_file_path)

    # Format code using black

    formatted_path = OUTPUTS / "formatted_code.py"

    success, msg = get_formatted_copy(working_file_path, str(formatted_path))

    st.success("Analysis complete")

    # Layout: Tabs for results

    tabs = st.tabs(
        [
            "Summary",
            "Flake8 Issues",
            "Complexity (Radon)",
            "Formatted Code",
            "Export / Reports",
        ]
    )

    # --- Summary Tab

    with tabs[0]:

        st.markdown("""
<h2 style='color:#FFFFFF; font-weight:600; margin-top:10px;'>
    Summary
</h2>
""", unsafe_allow_html=True)


        # short summary

        flake8_issues = report.get("flake8_issues", [])

        radon_cc = report.get("radon_cc", {})

        radon_mi = report.get("radon_mi", {})

        issue_count = 0

        if isinstance(flake8_issues, list):

            issue_count = len(flake8_issues)

        st.metric("Style issues (flake8)", value=issue_count)

        if isinstance(radon_mi, dict) and radon_mi:

            try:

                # radon_mi is usually { "filename": { "mi": value, "rank": "A" } }

                k = list(radon_mi.keys())[0]

                mi_val = (
                    radon_mi[k].get("mi") if isinstance(radon_mi[k], dict) else None
                )

                if mi_val is not None:

                    st.metric("Maintainability Index", value=f"{mi_val:.1f}")

            except Exception:

                pass

        # quick suggestions (AI-like summarization)

        suggestions = []

        if issue_count > 0:

            suggestions.append(
                f"Found {issue_count} style issues — consider fixing PEP8 warnings."
            )

        # examine radon complexity to produce advice

        try:

            functions = []

            for fname, blocks in radon_cc.items():

                for b in blocks:

                    functions.append((b.get("name"), b.get("complexity")))

            high = [f for f in functions if f[1] and f[1] >= 8]

            if high:

                suggestions.append(
                    f"{len(high)} block(s) with high cyclomatic complexity — consider refactoring."
                )

        except Exception:

            pass

        if not suggestions:

            suggestions = ["No immediate suggestions — code looks clean."]

        for s in suggestions:

            st.write("- " + s)

    # --- Flake8 Tab

    with tabs[1]:

        st.header("Flake8 Issues")

        if isinstance(flake8_issues, list) and flake8_issues:

            df = pd.DataFrame(flake8_issues)

            st.dataframe(df)

        else:

            st.info(
                "No flake8 issues found or flake8 not available. See raw output below."
            )

            st.json(flake8_issues)

    # --- Complexity Tab

    with tabs[2]:

        st.header("Cyclomatic Complexity (radon)")

        st.markdown("Below: functions / methods and their complexity.")

        if isinstance(radon_cc, dict) and radon_cc:

            rows = []

            for fname, blocks in radon_cc.items():

                for b in blocks:

                    rows.append(
                        {
                            "file": fname,
                            "name": b.get("name"),
                            "type": b.get("type"),
                            "complexity": b.get("complexity"),
                            "lineno": b.get("lineno"),
                            "rank": b.get("rank"),
                        }
                    )

            df = pd.DataFrame(rows)

            if not df.empty:

                st.dataframe(df)

                # Chart

                fig, ax = plt.subplots()

                ax.bar(df["name"], df["complexity"])

                ax.set_xlabel("Function")

                ax.set_ylabel("Cyclomatic Complexity")

                ax.set_title("Complexity per function")

                plt.xticks(rotation=45, ha="right")

                st.pyplot(fig)

            else:

                st.info("No complexity data available.")

        else:

            st.info("Radon complexity not available. Raw radon output:")

            st.json(radon_cc)

        st.markdown("**Maintainability Index**")

        st.json(radon_mi)

    # --- Formatted Code Tab

    with tabs[3]:

        st.header("Formatted Code (black)")

        if success:

            formatted_text = Path(formatted_path).read_text(encoding="utf-8")

            st.code(formatted_text, language="python")

            if st.download_button(
                "Download formatted code",
                data=formatted_text,
                file_name="formatted_code.py",
            ):

                st.success("Downloaded formatted code.")

        else:

            st.warning("Formatting not performed: " + msg)

            st.text(msg)

    # --- Export / Reports

    with tabs[4]:

        st.header("Export & Report")

        final_report = {
            "file": Path(working_file_path).name,
            "flake8_issues": report.get("flake8_issues"),
            "radon_cc": report.get("radon_cc"),
            "radon_mi": report.get("radon_mi"),
            "formatting": {
                "success": success,
                "message": msg,
                "formatted_file": str(formatted_path) if success else None,
            },
        }

        save_path = REPORTS / f"report_{Path(working_file_path).stem}.json"

        save_json = json.dumps(final_report, indent=2)

        Path(save_path).write_text(save_json, encoding="utf-8")

        st.write("Saved report to:", str(save_path))

        st.download_button(
            "Download report (JSON)",
            data=save_json,
            file_name=f"report_{Path(working_file_path).stem}.json",
        )

        st.markdown("**Sample report**")

        st.json(final_report)

        st.markdown("You can use this report for further analysis or record-keeping.")

# ---- Custom Apple-style CSS ----
apple_css = """
<style>

/* Remove Streamlit default padding */
.block-container {
    padding-top: 1.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Make cards (tabs, editor, preview) look like Apple widgets */
.stTabs [role="tablist"] {
    border-bottom: 1px solid #dcdcdc;
}

.stTabs [role="tab"] {
    padding: 12px 20px;
    margin-right: 4px;
    border-radius: 10px 10px 0 0;
    font-size: 16px;
    color: #555;
}

.stTabs [aria-selected="true"] {
    background: #ffffff;
    border: 1px solid #e4e4e4;
    border-bottom: 1px solid #ffffff;
    font-weight: 600;
}

/* Apple-style card for all boxes */
div.stTextArea, div.stCodeBlock, div.stDataFrame {
    background: #ffffff !important;
    border-radius: 14px !important;
    border: 1px solid #eaeaea !important;
    padding: 12px !important;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.06);
}

/* Buttons — Apple rounded style */
.stButton>button {
    background: #007AFF !important;
    color: white !important;
    padding: 10px 20px !important;
    border-radius: 12px !important;
    border: none;
    font-size: 15px;
    transition: 0.2s ease;
}

.stButton>button:hover {
    background: #005FCC !important;
}

/* Sidebar minimal */
.css-1d391kg {
    background-color: #F5F5F7 !important;
}

/* Editor + preview layout tweaks */
textarea {
    border-radius: 12px !important;
}

/* Header */
h1, h2, h3 {
    font-family: -apple-system, BlinkMacSystemFont, "San Francisco", "Helvetica Neue", Arial;
}

/* Metrics */
div[data-testid="stMetricValue"] {
    font-size: 32px !important;
    font-weight: 700;
    color: #000;
}
</style>
"""

st.markdown("""
<h2 style='color:#FFFFFF; font-weight:600;'>
</h2>
""", unsafe_allow_html=True)
st.markdown(apple_css, unsafe_allow_html=True)
st.markdown("""<style>
/* Remove Streamlit default padding */
.block-container {
    padding-top: 1.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
}
</style>""", unsafe_allow_html=True)   



# ----------------------------------------
# 🚀 PYTHON CODE REVIEWER (APPLE-STYLE CARD)
# ----------------------------------------

st.markdown("""
<hr><br>
<div style="
    font-size: 32px;
    font-weight: 700;
    text-align: center;
    color: white;
">
    ☕ PYTHON Code Reviewer
</div>
<p style="
    text-align: center;
    font-size: 18px;
    color: #6e6e73;
    margin-top: -5px;
">
</p>
""", unsafe_allow_html=True)

