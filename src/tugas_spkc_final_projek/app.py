import streamlit as st
import pandas as pd
import numpy as np
import json
import altair as alt

st.set_page_config(
    page_title="SPK Rekomendasi Leptop Mahasiswa",
    page_icon="💻",
    layout="wide"
)
# load data
@st.cache_data
def loadData(path="laptop_dummy.json"):
    with open(path, 'r', encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))

df = loadData()


