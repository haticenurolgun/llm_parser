import asyncio
from typing import List 
from ingestion.llm_setup import extract_structured_data, generate_embeddings_batch
from ingestion.models import GrantProgram
from connectors.base import RawProgram
from ingestion.database import upload_to_supabase   
from ingestion.chunker import chunk_text


def chunk_list(data, batch_size):
    """Listeyi belirli büyüklükte parçalara ayırır."""

    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

async def process_in_batches(raw_programs: List[RawProgram], batch_size: int = 15):
    """
    Tüm ETL (Extract-Transform-Load) sürecini asenkron paketler halinde yöneten ana şef.
    """
    # ... (önceki chunk_list ve döngü başlangıcı kısımları aynı) ...
    
    batches = list(chunk_list(raw_programs, batch_size))

    for idx, batch in enumerate(batches):
        print(f"\n--- Batch {idx + 1}/{len(batches)} İşleniyor ---")
        
        # 1. LLM GÖREVLERİNİ HAZIRLA VE ÇALIŞTIR
        tasks = [extract_structured_data(program.body) for program in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        cloned_programs_to_embed: List[GrantProgram] = []

        # 2. CHUNKING (PARÇALAMA) VE KLONLAMA İŞLEMİ
        for original_raw, result in zip(batch, results):
            if isinstance(result, Exception):
                print(f"Hata: LLM veriyi işleyemedi - {result}")
                continue # Hatalıysa atla, sistem çökmesin
            
            # LLM bize tek bir 'GrantProgram' nesnesi döndü.
            # Şimdi orijinal uzun metni alıp parçalara ayırıyoruz:
            chunks = chunk_text(original_raw.body)
            
            # Oluşan her bir parça için, elimizdeki Pydantic nesnesinin bir kopyasını yaratıyoruz
            for chunk_idx, chunk_string in enumerate(chunks):
                # model_copy() ile Pydantic nesnesini klonluyoruz
                klon = result.model_copy() 
                
                # Eksik alanları donanım mantığıyla üzerine zımbalıyoruz
                klon.body_chunk = chunk_string
                klon.chunk_index = chunk_idx
                
                # Senin eski kodundaki harika fikir: ID'yi URL + Chunk Index yapıyoruz ki 
                # veritabanında her parçanın benzersiz (unique) bir satırı olsun!
                klon.program_id = f"{original_raw.official_url}__chunk{chunk_idx}"
                
                # URL'i de nesneye ekliyoruz
                klon.official_url = original_raw.official_url
                
                cloned_programs_to_embed.append(klon)

        # 3. TOPLU EMBEDDING (VEKTÖRLEŞTİRME)
        if cloned_programs_to_embed:
            print(f"{len(cloned_programs_to_embed)} adet metin parçası için vektör alınıyor...")
            
            # Modellerin içindeki o zengin 'semantic_search_text' metinlerini topluyoruz
            texts_to_embed = [p.semantic_search_text for p in cloned_programs_to_embed]
            
            try:
                # Tek bir API isteğiyle tüm klonların vektörlerini alıyoruz
                batch_embeddings = await generate_embeddings_batch(texts_to_embed)
                
                # Dönen vektörleri sırasıyla klon nesnelerimize yapıştırıyoruz
                for klon_prog, emb in zip(cloned_programs_to_embed, batch_embeddings):
                    klon_prog.embedding = emb
                    
            except Exception as e:
                print(f"Embedding alınırken hata oluştu: {e}")
                # Hata olsa bile listeyi silmiyoruz, Supabase'e embedding=NULL olarak gidecekler

        # 4. SUPABASE'E YÜKLEME (LOAD)
        if cloned_programs_to_embed:
            upload_to_supabase(cloned_programs_to_embed)

        # API Limitleri için kısa bir nefes arası
        await asyncio.sleep(1)
        
    print("\nTüm veri işleme ve yükleme süreci başarıyla tamamlandı!")