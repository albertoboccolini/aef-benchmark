import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="AEF (AI Event Finder) Benchmark", layout="wide")
st.title("AEF (AI Event Finder) Benchmark")

EVAL_FOLDER = Path("evaluations")
EVAL_FOLDER.mkdir(exist_ok=True)

csv_files = list(EVAL_FOLDER.glob("*.csv"))

if not csv_files:
    st.warning("No report found in 'evaluations' folder.")
    st.stop()

selected_file = st.selectbox("Select a report", csv_files)

df = pd.read_csv(selected_file)


def get_model_color(row):
    model = str(row.get("Model", "")).lower()
    if "gpt" in model:
        return "color:#9370DB; font-weight: bold;"
    if "sonar" in model:
        return "color:#21808d; font-weight: bold;"
    return ""


def style_table(df):
    styled_df = df.style.map(
        lambda _: "", subset=pd.IndexSlice[:, :]
    )
    styled_df = styled_df.apply(
        lambda row: [get_model_color(row) if col == "Model" else "" for col in df.columns],
        axis=1
    ).format({
        "AVG Matching Score (distance > 2km)": "{:.3f}",
        "AVG Non-Matching Score": "{:.3f}",
    })
    return styled_df


st.dataframe(style_table(df), use_container_width=True, hide_index=True)
