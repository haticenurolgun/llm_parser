from abc import ABC, abstractmethod
import asyncio
import httpx

class BaseFetcher(ABC):
    """
    Tüm veri çekme sınıfları (fetcher) için ortak kuralları belirleyen taslak (Interface).
    Böylece sistemimiz hangi sitenin nasıl çekildiğini umursamaz, sadece fetch() metodunu kullanır.
    """

    @abstractmethod
    async def fetch(self, url: str) -> str:
        """
        Verilen URL'ye gider ve sayfanın HTML veya JSON kaynak kodunu metin olarak döndürür.
        """
        pass


class HttpxFetcher(BaseFetcher):
   

    def __init__(self, delay_seconds: float = 1.0):
        # Siteyi çökertmemek ve banlanmamak için her istekten önce ne kadar bekleyeceğimiz
        self.delay_seconds = delay_seconds

        # Bot olduğumuzu gizlemek için tarayıcı taklidi yapıyoruz
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def fetch(self, url: str) -> str:
        # 1. ADIM: Hedef siteyi çok hızlı yorup engellenmemek için biraz bekle
        await asyncio.sleep(self.delay_seconds)

        try:
            # 2. ADIM: Her istek için yeni bir bağlantı (tarayıcı sekmesi) açıyoruz
            # Asenkron (async with) kullandığımız için bu işlem ana motoru dondurmaz
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
                
                # Siteye GET isteği at (Maksimum 20 saniye yanıt vermesini bekle)
                response = await client.get(url, timeout=20.0)

                # Eğer site "200 OK" dönmezse (Örn: 404 Not Found, 403 Forbidden), boş dön
                if response.status_code != 200:
                    print(f"Uyarı: İndirme başarısız. Durum Kodu: {response.status_code} - Link: {url}")
                    return ""

                # Sıkıntı yoksa, sitenin tüm HTML/JSON kodunu geri gönder

                print(f"Başarılı: İndirme tamamlandı -> {url} ")
                return response.text

        except Exception as e:
            # İnternet kopması, zaman aşımı (timeout) gibi anlık hatalarda programın çökmesini engelle
            print(f"Hata: İndirme işlemi başarısız oldu -> {url} (Detay: {e})")
            return ""