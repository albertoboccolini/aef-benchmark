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

csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)


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


for csv_file in csv_files:
    st.text(csv_file.name)

    try:
        df = pd.read_csv(csv_file)
        if "Matching events" in df.columns:
            df = df.sort_values("Matching events", ascending=False)
        st.dataframe(style_table(df), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Errore nel caricare il file {csv_file.name}: {str(e)}")
