class AHP:
    def __init__(self):
        self.CRITERIA = [
             {"key": "harga_rp",       "label": "Harga",         "type": "cost"},
             {"key": "skor_performa",  "label": "Performa",      "type": "benefit"},
             {"key": "ram_gb",         "label": "RAM",           "type": "benefit"},
             {"key": "penyimpanan_gb", "label": "Penyimpanan",   "type": "benefit"},
             {"key": "baterai_jam",    "label": "Baterai",       "type": "benefit"},
             {"key": "berat_kg",       "label": "Bobot Ringan",  "type": "cost"},
             {"key": "rating_pengguna","label": "Rating",        "type": "benefit"},
        ]
        self.RI = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}