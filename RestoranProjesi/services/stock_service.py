import os
import pandas as pd
from collections import Counter
from typing import Dict, List, Tuple

from models import Yemek

STOK_DOSYA = "stok.csv"

# Ürün -> reçete (1 porsiyon)
RECETELER: Dict[str, Dict[str, int]] = {
    "İskender": {
        "Dana Eti (gr)": 200,
        "Ekmek (gr)": 100,
        "Yoğurt (gr)": 50,
        "Domates (adet)": 1,
        "Biber (adet)": 1,
        "Tereyağı (gr)": 15,
        "Salça Sos (gr)": 60
    },
    "Adana": {
        "Kıyma (gr)": 180,
        "Lavaş (adet)": 1,
        "Domates (adet)": 1,
        "Biber (adet)": 1,
        "Soğan (gr)": 50
    },
    "Beyti": {
        "Kıyma (gr)": 180,
        "Lavaş (adet)": 1,
        "Yoğurt (gr)": 60,
        "Salça Sos (gr)": 60
    },
    "Künefe": {
        "Kadayıf (gr)": 120,
        "Peynir (gr)": 90,
        "Şerbet (ml)": 120,
        "Tereyağı (gr)": 20
    },
    "Mercimek": {
        "Mercimek (gr)": 70,
        "Soğan (gr)": 30,
        "Yağ (ml)": 10
    },
    "Ezogelin": {
        "Kırmızı Mercimek (gr)": 60,
        "Bulgur (gr)": 25,
        "Soğan (gr)": 30,
        "Salça (gr)": 15
    },
    "Gavurdağı": {
        "Domates (adet)": 1,
        "Salatalık (adet)": 1,
        "Ceviz (gr)": 25,
        "Zeytinyağı (ml)": 15
    },
    "Su": {"Su (ml)": 500},
    "Kola": {"Kola (ml)": 330},
    "Ayran": {"Ayran (ml)": 250},
}

DEFAULT_ESIK_ADET = 10
DEFAULT_ESIK_GRML = 1000


def _unit_of(material_name: str) -> str:
    if "(" in material_name and ")" in material_name:
        return material_name.split("(")[-1].split(")")[0].strip().lower()
    return "adet"


def _default_esik_for(material_name: str) -> int:
    u = _unit_of(material_name)
    if u in ("gr", "ml"):
        return DEFAULT_ESIK_GRML
    return DEFAULT_ESIK_ADET


class StockService:
    @staticmethod
    def _migrate_if_needed(df: pd.DataFrame) -> pd.DataFrame:
        """
        Kullanıcının paylaştığı gibi eski format stok.csv:
        Malzeme,Miktar
        -> bunu Malzeme,Miktar,Esik formatına otomatik çevirir.
        """
        if "Esik" not in df.columns:
            df["Esik"] = df["Malzeme"].apply(_default_esik_for)

        # Güvenlik: boş/negatif düzelt
        df["Malzeme"] = df["Malzeme"].astype(str).str.strip()
        df = df[df["Malzeme"] != ""]
        df["Miktar"] = pd.to_numeric(df["Miktar"], errors="coerce").fillna(0).astype(int).clip(lower=0)
        df["Esik"] = pd.to_numeric(df["Esik"], errors="coerce").fillna(0).astype(int).clip(lower=0)

        return df

    @staticmethod
    def load_df() -> pd.DataFrame:
        if not os.path.exists(STOK_DOSYA):
            # stok.csv yoksa minimum bir stok oluştur
            df = pd.DataFrame([{"Malzeme": m, "Miktar": 0, "Esik": _default_esik_for(m)} for m in sorted(set().union(*RECETELER.values()))])
            df.to_csv(STOK_DOSYA, index=False, encoding="utf-8")
            return df

        df = pd.read_csv(STOK_DOSYA)
        df = StockService._migrate_if_needed(df)

        # migrate olduysa dosyaya yaz (kalıcı)
        df.to_csv(STOK_DOSYA, index=False, encoding="utf-8")
        return df

    @staticmethod
    def save_df(df: pd.DataFrame) -> None:
        df = StockService._migrate_if_needed(df)
        df.to_csv(STOK_DOSYA, index=False, encoding="utf-8")

    @staticmethod
    def load_map() -> Dict[str, Dict[str, int]]:
        df = StockService.load_df()
        out: Dict[str, Dict[str, int]] = {}
        for _, r in df.iterrows():
            out[str(r["Malzeme"])] = {"miktar": int(r["Miktar"]), "esik": int(r["Esik"])}
        return out

    @staticmethod
    def compute_total_decrease(items: List[Yemek]) -> Tuple[Dict[str, int], List[str]]:
        warnings: List[str] = []
        adet_map = Counter([y.isim for y in items])
        total: Dict[str, int] = {}

        for urun, adet in adet_map.items():
            if urun not in RECETELER:
                warnings.append(f"⚠️ Reçete yok: {urun} (stok kontrol dışı)")
                continue
            for malzeme, miktar in RECETELER[urun].items():
                total[malzeme] = total.get(malzeme, 0) + int(miktar) * int(adet)

        return total, warnings

    @staticmethod
    def validate_order(items: List[Yemek]) -> Tuple[bool, List[str], List[str]]:
        """
        - stok yetersiz => sipariş ENGEL
        - sipariş sonrası miktar <= Esik => uyarı
        """
        stok = StockService.load_map()
        total_decrease, base_warn = StockService.compute_total_decrease(items)

        errors: List[str] = []
        low_warnings: List[str] = list(base_warn)

        for malzeme, dusus in total_decrease.items():
            if malzeme not in stok:
                errors.append(f"⛔ {malzeme}: stokta yok (stok ekranına ekle)")
                continue

            mevcut = int(stok[malzeme]["miktar"])
            esik = int(stok[malzeme]["esik"])
            kalan = mevcut - int(dusus)

            if kalan < 0:
                errors.append(f"⛔ {malzeme}: yetersiz (stok {mevcut}, gereken {dusus})")
            else:
                if kalan <= esik:
                    low_warnings.append(f"⚠️ Stok takviyesi: {malzeme} kaldı {kalan} (eşik {esik})")

        return len(errors) == 0, errors, low_warnings

    @staticmethod
    def commit_order(items: List[Yemek]) -> None:
        """
        validate_order TRUE olduktan sonra çağrılır.
        """
        df = StockService.load_df()
        total_decrease, _ = StockService.compute_total_decrease(items)

        df_index = {str(r["Malzeme"]): i for i, r in df.iterrows()}

        for malzeme, dusus in total_decrease.items():
            if malzeme not in df_index:
                continue
            i = df_index[malzeme]
            df.at[i, "Miktar"] = max(0, int(df.at[i, "Miktar"]) - int(dusus))

        StockService.save_df(df)

    @staticmethod
    def admin_add_stock(malzeme: str, miktar_ekle: int) -> None:
        df = StockService.load_df()
        malzeme = (malzeme or "").strip()
        if not malzeme:
            return

        # varsa artır, yoksa ekle
        if (df["Malzeme"] == malzeme).any():
            idx = df.index[df["Malzeme"] == malzeme][0]
            df.at[idx, "Miktar"] = int(df.at[idx, "Miktar"]) + int(miktar_ekle)
        else:
            df = pd.concat([df, pd.DataFrame([{
                "Malzeme": malzeme,
                "Miktar": int(miktar_ekle),
                "Esik": _default_esik_for(malzeme)
            }])], ignore_index=True)

        StockService.save_df(df)

    @staticmethod
    def low_stock_list() -> pd.DataFrame:
        df = StockService.load_df()
        df["Durum"] = df.apply(lambda r: "❗ Kritik" if int(r["Miktar"]) <= int(r["Esik"]) else "✅ Normal", axis=1)
        return df.sort_values(by=["Durum", "Miktar"], ascending=[True, True])
