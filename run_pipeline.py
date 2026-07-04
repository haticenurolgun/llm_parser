"""
run_pipeline.py
Sistemin ana giriş noktasıdır (Entry Point).
Kullanıcıdan terminal üzerinden parametre alır, doğru botu (connector) seçer 
ve asenkron pipeline başlatır.
"""

import asyncio
import argparse
from html import parser

# Sistemin diğer parçalarını içeri aktarıyoruz

from connectors.kosgeb import KosgebConnector
from connectors.kalkinma_ajanslari import KalkinmaAjansiConnector
from ingestion.pipeline import process_in_batches


async def main():
    # 1. KOMUT SATIRI PARAMETRELERİNİ AYARLAMA
    parser = argparse.ArgumentParser(description="Destekçi AI - Hibe ve Destek Toplama Motoru")
    
    # Kullanıcıdan '--source' adında mecburi bir parametre bekliyoruz
    parser.add_argument(
        "--source", 
        type=str, 
        required=True, 
        choices=["kosgeb", "kalkinma"], # Sadece bu seçeneklere izin ver
        help="Veri çekilecek kaynağı belirtin (Örn: kosgeb veya kalkinma)"
    )

    args = parser.parse_args()
    print(f"\n🚀 Destekçi AI Motoru Başlatılıyor... Hedef: {args.source.upper()}\n")

    # 2. DOĞRU CONNECTOR SEÇME 
    connector = None
    if args.source == "kosgeb":
        connector = KosgebConnector()
    elif args.source == "kalkinma":
        connector = KalkinmaAjansiConnector() 
    
    if not connector:
        print("Hata: Geçerli bir connector bulunamadı.")
        return
    

    # 3. VERİ ÇEKME AŞAMASI

    print("Aşama 1: Web'den ham veriler çekiliyor...")
    raw_data = await connector.extract()
    
    if not raw_data:
        print("Uyarı: Kaynaktan hiçbir veri çekilemedi. Program sonlandırılıyor.")
        return

    # 4. İŞLEME VE YÜKLEME AŞAMASI
    print(f"Aşama 2: {len(raw_data)} adet ham veri yapay zeka motoruna gönderiliyor...")
    
    # parçalama, pydantic, embedding ve supabase yükleme işlemlerini yapan ana fonksiyonu çağırıyoruz!
    # API limitlerini korumak için 15'erli paketler halinde işliyoruz.
    await process_in_batches(raw_programs=raw_data, batch_size=15)
    
    print("\n✅ Tüm ETL (Extract-Transform-Load) süreci başarıyla tamamlandı!")

# Python dosyasının doğrudan çalıştırıldığından emin olma kontrolü
if __name__ == "__main__":

    # Asenkron başlatıyoruz
    asyncio.run(main())