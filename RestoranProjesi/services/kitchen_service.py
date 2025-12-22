import time
from dataclasses import dataclass, field
from typing import List

from models import Yemek, Siparis
from database import siparis_kaydet

@dataclass
class ActiveOrderItem:
    masa_no: int
    yemek: Yemek
    garson_adi: str
    created_at: float = field(default_factory=time.time)
    duration_s: int = 0
    written_to_csv: bool = False

    @property
    def eta_seconds(self) -> int:
        elapsed = time.time() - self.created_at
        return int(max(0, self.duration_s - elapsed))

    @property
    def status(self) -> str:
        return "HAZIR!" if self.eta_seconds <= 0 else "Hazırlanıyor..."

class KitchenService:
    @staticmethod
    def add_orders(aktif_siparisler: List[ActiveOrderItem], masa_no: int, garson_adi: str, items: List[Yemek]) -> None:
        current_load = len([o for o in aktif_siparisler if o.status != "HAZIR!"])
        load_factor = 1.0 + min(1.0, current_load / 20)

        for y in items:
            duration = int(round(y.hazirlanma_suresi * load_factor))
            aktif_siparisler.append(
                ActiveOrderItem(masa_no=masa_no, yemek=y, garson_adi=garson_adi, duration_s=duration)
            )

    @staticmethod
    def flush_ready_to_csv(aktif_siparisler: List[ActiveOrderItem]) -> None:
        for o in aktif_siparisler:
            if o.status == "HAZIR!" and not o.written_to_csv:
                sip = Siparis(o.masa_no, o.yemek, garson_adi=o.garson_adi)
                sip.durum = "HAZIR!"
                siparis_kaydet(sip)
                o.written_to_csv = True
