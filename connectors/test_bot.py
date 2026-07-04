import asyncio
from connectors.kalkinma_ajanslari import KalkinmaAjansiConnector

async def main():
    print("Test başlatılıyor...\n")
    
    # Sadece botumuzu çağırıyoruz (Pipeline, LLM veya Supabase yok!)
    bot = KalkinmaAjansiConnector()
    ham_veriler = await bot.extract()
    
    print("\n--- ÇEKİLEN İLK 3 VERİ ÖZETİ ---")
    for veri in ham_veriler[:3]:
        print(f"🆔 ID     : {veri.program_id}")
        print(f"📌 Başlık : {veri.title}")
        print(f"🔗 Link   : {veri.official_url}")
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())