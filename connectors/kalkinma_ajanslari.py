"""
connectors/kalkinma_ajanslari.py
Kalkınma Ajansı sisteminden API aracılığıyla (JSON) veri çeken bot.
"""
import asyncio
import httpx
from typing import List

from connectors.base import BaseConnector, RawProgram

class KalkinmaAjansiConnector(BaseConnector):
    def __init__(self):
        # NOT: Buraya gerçek ajansın API linkini veya web adresini yazmalısın.
        # Şimdilik örnek bir endpoint (uç nokta) adresi koyuyoruz.
        self.api_url = "https://jsonplaceholder.typicode.com/posts" # Test için sahte (dummy) bir API kullanıyoruz
        self.source_name = "Kalkınma Ajansı"
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def extract(self) -> List[RawProgram]:
        raw_programs = []
        print(f"[{self.source_name}] Veriler API'den çekiliyor...")

        try:
            # 1. ADIM: API'YE BAĞLAN
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
                await asyncio.sleep(1.0) # Sunucuyu yormamak için bekleme
                
                response = await client.get(self.api_url, timeout=20.0)
                
                if response.status_code != 200:
                    print(f"❌ API'ye bağlanılamadı. Hata Kodu: {response.status_code}")
                    return []
                
                print(f"✅ {self.source_name} sistemine başarıyla bağlanıldı!")
                
                # 2. ADIM: JSON VERİSİNİ OKU (BeautifulSoup'a gerek yok!)
                gelen_veri = response.json() 

                # 3. ADIM: VERİYİ ANAYASAMIZA (RawProgram) DÖNÜŞTÜR
                # Test API'miz bir liste döndüğü için üzerinde dönüyoruz (Senin ajansın yapısına göre burası değişebilir)
                # Test sürecini hızlandırmak için sadece ilk 3 veriyi alalım:
                for item in gelen_veri[:3]: 
                    program = RawProgram(
                        program_id=f"kalkinma_{item.get('id')}",
                        title=item.get("title", "Başlıksız Proje").capitalize(),
                        body=item.get("body", ""), # Metin kısmı
                        source=self.source_name,
                        category="Bölgesel Kalkınma",
                        official_url=f"https://kalkinma.gov.tr/detay/{item.get('id')}"
                    )
                    raw_programs.append(program)

        except Exception as e:
            print(f"❌ {self.source_name} çekilirken hata oluştu: {e}")

        print(f"[{self.source_name}] Toplam {len(raw_programs)} ham hibe bulundu.\n")
        return raw_programs