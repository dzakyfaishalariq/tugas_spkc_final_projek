import numpy as np
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
        self.PRESET = {
            "Seimbang":         [5, 5, 5, 5, 5, 5, 5],
            "Hemat (Budget)":   [9, 3, 3, 3, 5, 5, 5],
            "Performa Tinggi":  [3, 9, 7, 5, 5, 3, 5],
            "Coding":           [4, 8, 9, 6, 5, 5, 5],
            "Editing/Desain":   [4, 8, 9, 7, 4, 4, 5],
            "Gaming":           [3, 9, 7, 6, 3, 3, 5],
        }
    # Fungsi AHP dan MCDM
    def ahpWeights(self, M):
        n = M.shape[0]
        gm = np.prod(M, axis=1) ** (1.0 / n)
        w = gm / gm.sum()
        Aw = M @ w
        lam = float(np.mean(Aw / w))
        CI = (lam - n) / (n - 1) if n > 1 else 0.0
        CR = CI / self.RI.get(n, 1) if self.RI.get(n, 0) > 0 else 0.0
        return w, CR

    def topsis(self, X, w, types):
        """TOPSIS: vector normalization + jarak ke solusi ideal."""
        norm = np.sqrt((X ** 2).sum(axis=0))
        norm[norm == 0] = 1
        Y = (X / norm) * w
        best  = np.array([Y[:, j].max() if types[j] == "benefit"
                          else Y[:, j].min() for j in range(X.shape[1])])
        worst = np.array([Y[:, j].min() if types[j] == "benefit"
                          else Y[:, j].max() for j in range(X.shape[1])])
        Dp = np.sqrt(((Y - best) ** 2).sum(axis=1))
        Dm = np.sqrt(((Y - worst) ** 2).sum(axis=1))
        return Dm / (Dp + Dm + 1e-12)

    def saw(self, X, w, types):
        """SAW: normalisasi linier lalu jumlah terbobot."""
        m, n = X.shape
        R = np.zeros_like(X)
        for j in range(n):
            if types[j] == "benefit":
                mx = X[:, j].max()
                R[:, j] = X[:, j] / mx if mx > 0 else 0
            else:
                mn = X[:, j].min()
                R[:, j] = mn / X[:, j] if mn > 0 else 0
        return R @ w

    def fmtRp(self, x):
        return "Rp " + f"{int(x):,}".replace(",",".")
    