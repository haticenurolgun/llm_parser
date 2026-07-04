import os
from supabase import create_client
from ingestion.models import GrantProgram

# Supabase istemcisini başlat (Bunu dosyanın en üstünde yapabilirsin)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_to_supabase(programs: list[GrantProgram]):
    """
    Pydantic modellerinden oluşan listeyi alır, veritabanına uyumlu JSON'a çevirir
    ve Supabase'e tek seferde (Bulk Upsert) yazar.
    """
    if not programs:
        print("Yüklenecek veri bulunamadı.")
        return

    # Pydantic nesnelerini Supabase'in anlayacağı sözlüklere (dict) çeviriyoruz.
    # model_dump() metodu bizim yerimize tarihleri string'e vb. çevirir.
    rows_to_insert = []
    for prog in programs:
        rows_to_insert.append(prog.model_dump())

    try:
        print(f"{len(rows_to_insert)} adet kayıt Supabase'e gönderiliyor...")
        
        # duplicate kayıtları önlemek için program_id üzerinden upsert yapıyoruz
        response = (
            supabase.table("programs")
            .upsert(rows_to_insert, on_conflict="program_id")
            .execute()
        )
        print(f"✅ Başarılı! {len(response.data)} satır veritabanına işlendi.")
        
    except Exception as e:
        print(f"❌ Supabase yükleme hatası: {e}")