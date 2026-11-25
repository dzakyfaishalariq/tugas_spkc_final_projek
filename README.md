# Dokumentasi Aplikasi: SPK Rekomendasi Laptop Mahasiswa

Aplikasi web interaktif berbasis **Streamlit** yang mengimplementasikan Sistem Pendukung Keputusan (SPK) menggunakan metode pembobotan **AHP (Analytic Hierarchy Process)** dan metode perangkingan **MCDM (Multi-Criteria Decision Making)** yaitu **TOPSIS** dan **SAW** untuk membantu mahasiswa memilih laptop sesuai spesifikasi dan anggaran.

---

## 1. Dependensi & Modul Eksternal

| Library / Modul | Kegunaan |
| --- | --- |
| `streamlit` | Membangun antarmuka pengguna (UI), sidebar filter, tabel interaktif, dan layout halaman. |
| `pandas` & `numpy` | Manipulasi dataset tabular (`DataFrame`) dan operasi matriks numerik untuk pembobotan serta perhitungan skor. |
| `altair` | Membuat visualisasi grafik batang horizontal interaktif untuk perbandingan skor hasil perangkingan. |
| `json` | Membaca sumber data laptop dari file berformat JSON. |
| `tugas_spkc_final_projek.fungsi.AHP` | Modul lokal yang menyediakan atribut kriteria (`CRITERIA`, `PRESET`), perhitungan bobot AHP (`ahpWeights`), algoritma perangkingan (`topsis`, `saw`), dan format mata uang (`fmtRp`). |

---

## 2. Alur Kerja Sistem (Workflow)

1. **Inisialisasi & Pemuatan Data:** Mengatur konfigurasi halaman (`wide` layout) dan memuat `laptop_dummy.json` ke dalam `DataFrame` dengan mekanisme *caching* (`@st.cache_data`).
2. **Konfigurasi Sidebar:** Pengguna mengatur filter kandidat, memilih mode pembobotan kriteria, dan menentukan metode perangkingan.
3. **Penyaringan Data (Filtering):** Dataset utama disaring berdasarkan kriteria fisik/non-kriteria (harga, jurusan, kebutuhan, merek, kategori).
4. **Validasi Kandidat:** Sistem memvalidasi jumlah kandidat hasil filter (minimal 2 laptop agar perbandingan MCDM dapat berjalan).
5. **Perhitungan Skor & Perangkingan:** Matriks keputusan dihitung menggunakan metode **TOPSIS** atau **SAW** berdasarkan vektor bobot aktif, lalu diurutkan dari skor tertinggi.
6. **Visualisasi & Output:** Menampilkan tabel peringkat, grafik batang perbandingan skor, dan kartu detail spesifikasi rekomendasi peringkat pertama.

---

## 3. Penjelasan Komponen & Blok Kode

### A. Konfigurasi Halaman & Pemuatan Data

* **`st.set_page_config(...)`**: Mengatur judul tab browser (`SPK Rekomendasi Leptop Mahasiswa`), ikon, dan tata letak lebar (`wide`).
* **`loadData(path="laptop_dummy.json")`**: Menggunakan dekorator `@st.cache_data` agar pembacaan file JSON hanya dilakukan sekali selama tidak ada perubahan file, sehingga mempercepat *rerun* aplikasi saat pengguna mengubah filter.

### B. Sidebar: Filter Data Kandidat

Menyediakan kontrol input di panel kiri untuk mempersempit ruang pencarian:

* **`budget` (`st.slider`)**: Rentang harga minimum dan maksimum yang dibulatkan ke kelipatan Rp 100.000.
* **`jurusan` (`st.selectbox`)**: Mengambil nilai unik dari kolom list `jurusan_rekomendasi` untuk menyaring kecocokan program studi.
* **`keb` (`st.multiselect`)**: Filter kebutuhan penggunaan (`tugas_ringan`, `coding`, `editing_desain`, `gaming`) yang dicocokkan dengan kolom `cocok_untuk`.
* **`merek` & `kategori` (`st.multiselect`)**: Filter opsional berdasarkan merek dan tipe/kategori laptop (jika dikosongkan, semua data disertakan).

### C. Sidebar: Pembobotan Kriteria (`weights`)

Terdapat dua mode penentuan bobot kriteria yang saling eksklusif:

| Mode | Mekanisme Perhitungan | Validasi Konsistensi |
| --- | --- | --- |
| **Preset + Slider** | Memuat profil bobot bawaan dari `my_fungsi.PRESET`, lalu pengguna menyesuaikan nilai tiap kriteria (`0.0` – `10.0`). Vektor bobot dinormalisasi dengan membagi tiap nilai terhadap total jumlahnya (`raws / sum(raws)`). Jika semua bernilai `0`, otomatis diatur merata (`1`). | Dianggap konsisten secara otomatis (`CR = 0.0`). |
| **AHP Pairwise** | Pengguna mengisi matriks perbandingan berpasangan ukuran $n \times n$ (segitiga atas, skala `0.111` – `9.0`). Elemen segitiga bawah otomatis diisi kebalikannya ($1/v$). Bobot dihitung melalui `my_fungsi.ahpWeights(M)`. | Menghitung *Consistency Ratio* (`CR`). Jika `CR <= 0.1`, matriks dinyatakan konsisten; jika `> 0.1`, muncul peringatan untuk merevisi perbandingan. |

### D. Sidebar: Pengaturan Perangkingan

* **`metode` (`st.radio`)**: Memilih algoritma MCDM antara **TOPSIS** atau **SAW**.
* **`top_n` (`st.slider`)**: Membatasi jumlah kandidat teratas yang ditampilkan (`3` hingga `30`, default `10`).

### E. Panel Utama: Inspeksi Bobot & Penyaringan

* **Expander `📊 Bobot Kriteria Aktif**`: Menampilkan tabel berisi nama kriteria, tipe (`benefit`/`cost`), nilai bobot desimal, persentase bobot, serta grafik batang (`st.bar_chart`).
* **Proses Filtering (`fdf`)**: Menerapkan seluruh filter sidebar ke salinan `DataFrame` utama (`df.copy()`).
* **Guard Clause (`len(fdf) < 2`)**: Menghentikan eksekusi aplikasi (`st.stop()`) dengan pesan error jika kandidat kurang dari 2, karena metode perangkingan membutuhkan perbandingan antar-alternatif.

### F. Perhitungan MCDM & Penyajian Hasil

1. **Ekstraksi Matriks & Skor:**
* `X`: Matriks numerik nilai kriteria dari kandidat tersaring (`fdf`).
* `types`: Daftar tipe kriteria (`benefit` atau `cost`) dari `my_fungsi.CRITERIA`.
* `skor`: Dihitung via `my_fungsi.topsis(X, weights, types)` atau `my_fungsi.saw(X, weights, types)`.


2. **Tabel Peringkat (`st.dataframe`):**
* Mengurutkan `fdf` berdasarkan `skor_spk` secara menurun (*descending*), mengambil sejumlah `top_n`, dan menambahkan kolom `Rank`.
* Kolom `Skor SPK` diformat menggunakan `st.column_config.ProgressColumn` (rentang `0.0` – `1.0`) untuk memudahkan pembacaan visual.


3. **Grafik Perbandingan (`alt.Chart`):**
* Merender diagram batang horizontal dengan Altair yang diurutkan berdasarkan nilai skor tertinggi (`sort="-x"`), dilengkapi *tooltip* interaktif (nama laptop, merek, harga, dan skor).


4. **Kartu Rekomendasi Utama (`🏆 Rekomendasi Utama`):**
* Mengambil baris pertama (`fdf.iloc[0]`) dan membaginya ke dalam dua kolom:
* **Kolom Kiri (`c1`)**: Menampilkan spesifikasi teknis lengkap (nama, skor, harga terformat `fmtRp`, prosesor, GPU beserta status *dedicated*, RAM, penyimpanan, layar, berat, baterai, OS, kecocokan tugas, dan jurusan).
* **Kolom Kanan (`c2`)**: Menampilkan 4 metrik ringkas (`st.metric`) untuk skor performa, rating pengguna, masa garansi, dan tahun rilis.





---

## 4. Struktur Data yang Dibutuhkan (`laptop_dummy.json`)

Agar kode berjalan tanpa error (`KeyError`), file JSON masukan wajib memiliki kolom-kolom berikut pada setiap objek laptop:

* **Identitas & Kategori:** `nama_lengkap` (str), `merek` (str), `kategori` (str), `tahun_rilis` (int/float).
* **Spesifikasi & Harga:** `harga_rp` (int/float), `prosesor` (str), `gpu` (str), `gpu_dedicated` (bool), `ram_gb` (int/float), `penyimpanan_gb` (int/float), `tipe_penyimpanan` (str), `ukuran_layar_inch` (float), `berat_kg` (float), `baterai_jam` (float), `sistem_operasi` (str).
* **Atribut Penilaian & Filter:** `skor_performa` (float), `rating_pengguna` (float), `garansi_tahun` (int/float), `jurusan_rekomendasi` (list of str), `cocok_untuk` (list of str), serta seluruh key kriteria yang didefinisikan di `my_fungsi.CRITERIA`.

---

## 5. Cara Menjalankan Aplikasi

Pastikan struktur direktori menempatkan paket `tugas_spkc_final_projek` dan file `laptop_dummy.json` pada *root* proyek yang sama, lalu jalankan perintah berikut di terminal:

```bash
streamlit run nama_file_utama.py

```
