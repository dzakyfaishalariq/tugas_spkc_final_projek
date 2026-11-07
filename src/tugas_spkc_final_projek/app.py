import json

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from tugas_spkc_final_projek.fungsi import AHP

my_fungsi = AHP()

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

with st.sidebar:
    st.header("🔍 Filter data")

    min_h = int(df.harga_rp.min() // 100_000 * 100_000)
    max_h = int((df.harga_rp.max() // 100_000 + 1) * 100_000)

    budget = st.slider(
        "Budget (Rp)", min_value=min_h, max_value=max_h, value=(min_h, max_h), step=100_000, format="Rp %d"
    )

    all_jur = sorted({j for lst in df.jurusan_rekomendasi for j in lst})
    jurusan = st.selectbox("Jurusan", ["Semua"] + all_jur)

    all_keb = ["tugas_ringan", "coding", "editing_desain", "gaming"]
    keb = st.multiselect("Kebutuhan", all_keb, default=[])

    all_merek = sorted(df.merek.unique())
    merek = st.multiselect("Merek (kosong = semua)", all_merek)

    all_kat = sorted(df.kategori.unique())
    kategori = st.multiselect("Kategori (kosong = semua)", all_kat) 

    st.divider()
    st.header("⚖️ Bobot Kriteria")
    mode = st.radio("Mode bobot", ["Preset + Slider", "AHP Pairwise"])

    weights, CR = None, 0.0

    if mode == "Preset + Slider":
        preset_name = st.selectbox("Preset Profil", list(my_fungsi.PRESET.keys()))
        raws = []
        for i, c in enumerate(my_fungsi.CRITERIA):
            v = st.slider(
                c['label'], 0.0, 10.0,
                float(my_fungsi.PRESET[preset_name][i]), 0.5,
                key=f"w_{preset_name}_{c['key']}"
            )
            raws.append(v)
        if sum(raws) == 0:
            raws = [1] * len(raws)

        weights = np.array(raws) / sum(raws)
        st.caption("Bobot dinormalisasi. Ekuivalen AHP konsisten (CR = 0).")

    else: # AHP Pairwise
        st.write("Matriks saat y (nilai > 1 = baris lebih penting dari kolom).")
        n = len(my_fungsi.CRITERIA)
        labels = [c['label'] for c in my_fungsi.CRITERIA]
        M = np.ones((n,n))
        cols = st.columns(3)
        idx = 0
        for i in range(n):
            for j in range(i + 1, n):
                with cols[idx % 3]:
                    v = st.number_input(
                        f"{labels[i]} / {labels[j]}",
                        min_value=0.111, max_value=9.0,
                        value=1.0, step=0.1,
                        key=f'ahp_{i}_{j}',
                    )
                M[i,j] = v
                M[j,i] = 1.0/v
                idx += 1
        weights, CR = my_fungsi.ahpWeights(M)
        if CR <= 0.1:
            st.success(f"CR = {CR:.4f} ✅ Konsisten (<= 0.1)")
        else:
            st.warning(f"CR = {CR:.4f} ⚠️ Tidak konsisten (> 0.1), revisi matriks.")
    st.divider()
    st.header("🎯 Perangkingan")
    metode = st.radio("Metode", ["TOPSIS", "SAW"], horizontal=True)
    top_n = st.slider("Tampilkan Top N", 3, 30, 10)

# Menampilkan bobot aktif
with st.expander("📊 Bobot Kriteria Aktif", expanded=False):
    wdf = pd.DataFrame({
        "Kriteria" : [c['label'] for c in my_fungsi.CRITERIA],
        "Tipe" : [c['type'] for c in my_fungsi.CRITERIA],
        "Bobot" : [round(float(w), 4) for w in weights],
        "Bobot %" : [f"{w*100:.2f}%" for w in weights ]
    })
    st.dataframe(wdf, use_container_width=True, hide_index=True)
    st.bar_chart(wdf.set_index("Kriteria")["Bobot"])

# Filter data
fdf = df.copy()
fdf = fdf[(fdf.harga_rp >= budget[0]) & (fdf.harga_rp <= budget[1])]
if jurusan != "Semua":
    fdf = fdf[fdf.jurusan_rekomendasi.apply(lambda x: jurusan in x)]
if keb:
    fdf = fdf[fdf.cocok_untuk.apply(lambda x: any(k in x for k in keb))]
if merek:
    fdf = fdf[fdf.merek.isin(merek)]
if kategori:
    fdf = fdf[fdf.kategori.isin(kategori)]
fdf = fdf.reset_index(drop=True)

st.subheader(f"📋 Kandidat Laptop ({len(fdf)} cocok filter)")

if len(fdf) < 2:
    st.error("Perlu minimal **2 laptop** untuk perangkingan. Longgarkan filter di sidebar.")
    st.stop()

# perangkingan MCDM
X = fdf[[c["key"] for c in my_fungsi.CRITERIA]].values.astype(float)
types = [c["type"] for c in my_fungsi.CRITERIA]
skor = my_fungsi.topsis(X, weights, types) if metode == "TOPSIS" else my_fungsi.saw(X, weights, types)

fdf["skor_spk"] = skor
fdf = fdf.sort_values("skor_spk", ascending=False).head(top_n).reset_index(drop=True)
fdf["Rank"] = fdf.index + 1

# tabel hasil
disp = fdf[["Rank", "nama_lengkap", "merek", "kategori", "harga_rp",
            "prosesor", "ram_gb", "penyimpanan_gb", "skor_performa",
            "baterai_jam", "berat_kg", "skor_spk"]].copy()
disp["harga_rp"] = disp["harga_rp"].map(my_fungsi.fmtRp)
disp.columns = ["#", "Laptop", "Merek", "Kategori", "Harga", "Prosesor",
                "RAM (GB)", "Storage (GB)", "Performa", "Baterai (jam)",
                "Berat (kg)", "Skor SPK"]

st.dataframe(
    disp,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Skor SPK": st.column_config.ProgressColumn(
            "Skor SPK", format="%.4f", min_value=0.0, max_value=1.0,
        ),
    },
)

# validasi rangking

chart = (
    alt.Chart(fdf)
    .mark_bar()
    .encode(
        x=alt.X("skor_spk:Q", title=f"Skor {metode}"),
        y=alt.Y("nama_lengkap:N", sort="-x", title=None),
        color=alt.Color("skor_spk:Q", scale=alt.Scale(scheme="blues"), legend=None),
        tooltip=["nama_lengkap", "merek", "harga_rp", "skor_spk"],
    )
    .properties(height=max(300, 28 * len(fdf)))
)
st.altair_chart(chart, use_container_width=True)

# detail top pick
st.subheader("🏆 Rekomendasi Utama")
top = fdf.iloc[0]
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown(f"### {top['nama_lengkap']}")
    st.markdown(f"**Skor SPK:** `{top['skor_spk']:.4f}`")
    st.markdown(f"**Harga:** {my_fungsi.fmtRp(top['harga_rp'])}")
    st.markdown(f"**Prosesor:** {top['prosesor']}")
    st.markdown(f"**GPU:** {top['gpu']}" + (" (dedicated)" if top["gpu_dedicated"] else ""))
    st.markdown(f"**RAM:** {top['ram_gb']} GB • **Storage:** {top['penyimpanan_gb']} GB {top['tipe_penyimpanan']}")
    st.markdown(f"**Layar:** {top['ukuran_layar_inch']}\" • **Berat:** {top['berat_kg']} kg")
    st.markdown(f"**Baterai:** {top['baterai_jam']} jam • **OS:** {top['sistem_operasi']}")
    st.markdown(f"**Cocok untuk:** {', '.join(top['cocok_untuk'])}")
    st.markdown(f"**Jurusan:** {', '.join(top['jurusan_rekomendasi'])}")
with c2:
    st.metric("Performa", f"{top['skor_performa']}/10")
    st.metric("Rating",   f"{top['rating_pengguna']}/5")
    st.metric("Garansi",  f"{top['garansi_tahun']} tahun")
    st.metric("Tahun rilis", int(top["tahun_rilis"]))

st.caption("⚠️ Dataset **dummy** — harga, rating, baterai, dan skor hanya untuk demo, bukan data pasar sebenarnya.")
