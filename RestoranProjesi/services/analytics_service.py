import pandas as pd
from typing import Dict, List, Tuple

from analiz import veri_yukle, yapay_zeka_tahmini_yap
from services.stock_service import RECETELER

class AnalyticsService:
    @staticmethod
    def kpis_last30() -> Tuple[float, float, int, str]:
        df = veri_yukle()
        if df is None or df.empty:
            return 0.0, 0.0, 0, "-"
        last30 = df[df["Tarih"] > (df["Tarih"].max() - pd.Timedelta(days=30))]
        ciro = float(last30["Fiyat"].sum()) if not last30.empty else 0.0
        kar = float(last30["Kar"].sum()) if not last30.empty else 0.0
        sip = int(len(last30)) if not last30.empty else 0
        best = last30["Yemek Adi"].value_counts().idxmax() if sip > 0 else "-"
        return ciro, kar, sip, best

    @staticmethod
    def stock_plan(stok_map: Dict[str, Dict[str, int]], guvenlik_orani=0.10):
        df_ai = yapay_zeka_tahmini_yap()
        if df_ai is None or df_ai.empty:
            return pd.DataFrame(), pd.DataFrame(), [], df_ai

        tahmin_map = dict(zip(df_ai["Urun"], df_ai["Tahmin"]))
        ihtiyac: Dict[str, int] = {}
        yorumlar: List[str] = []

        for urun, tahmin_adet in tahmin_map.items():
            if urun not in RECETELER:
                continue

            try:
                buay = int(df_ai.loc[df_ai["Urun"] == urun, "BuAy"].values[0])
            except:
                buay = None

            if buay is not None:
                if tahmin_adet > buay * 1.10:
                    yorumlar.append(f"📈 {urun} artış (BuAy {buay} → Tahmin {tahmin_adet})")
                elif tahmin_adet < buay * 0.90:
                    yorumlar.append(f"📉 {urun} düşüş (BuAy {buay} → Tahmin {tahmin_adet})")
                else:
                    yorumlar.append(f"➖ {urun} stabil (BuAy {buay} → Tahmin {tahmin_adet})")

            for malzeme, miktar in RECETELER[urun].items():
                ihtiyac[malzeme] = ihtiyac.get(malzeme, 0) + int(miktar) * int(tahmin_adet)

        for malzeme in list(ihtiyac.keys()):
            ihtiyac[malzeme] = int(round(ihtiyac[malzeme] * (1 + guvenlik_orani)))

        rows, kritik = [], []
        for malzeme, need in sorted(ihtiyac.items(), key=lambda x: -x[1]):
            have = int(stok_map.get(malzeme, {}).get("miktar", 0))
            eksik = max(0, need - have)
            rows.append({
                "Malzeme": malzeme,
                "30g_Ihtiyac(+%10)": need,
                "Stok": have,
                "Eksik": eksik,
                "Aksiyon": "✅ Yeter" if eksik == 0 else "🛒 Satın Al"
            })
            if eksik > 0:
                kritik.append({"Malzeme": malzeme, "Ihtiyac": need, "Stok": have, "Eksik": eksik})

        return pd.DataFrame(rows), pd.DataFrame(kritik), yorumlar, df_ai
