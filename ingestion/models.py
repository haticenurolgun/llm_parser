#data validation için, LLM'den dönen veri
#bizim database'imize uygun mu değil mi kontrol etmek için kullanılır.

#kesin olması gerekli alanlar, veri tipleri, uzunluklar vs. gibi kontroller yapılır.
#opsişyonel alanlar için ise, eğer LLM'den gelen veri eksikse, default değerler atanır.
#tarihler için özel kontroller uygulanır.

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class GrantProgram(BaseModel):
    """LLM çıktıları ve veritabanına ekleme için doğrulanmış şema."""

    #kesin olması gereken alanlar
    program_id: str = Field(..., description="Programın benzersiz kimliği")
    title: str = Field(..., description="Program veya destek başlığının adı")
    body_chunk: str = Field(..., description="Programın metin içeriği veya açıklaması")
    chunk_index: int = Field(..., description="Programın metin içindeki parça numarası")
    embedding: Optional[List[float]] = Field(default=None, description="Programın 768 boyutlu embedding vektörü. LLM tarafından üretilir ve veritabanında saklanır.")
    agency: str = Field(..., description="Programı sağlayan kurum veya kuruluş")
    source: str = Field(..., description="Programın kaynağı,linki veya sağlayıcı web sitesi")
    category: str = Field(..., description="Programın kategorisi veya destek türü. Örn: Araştırma, Girişimcilik,turizm vb.")
    region: str = Field(..., description="Programın geçerli olduğu bölge veya ülke")
    description: str = Field(..., description="Programın detaylı açıklaması veya özet bilgisi")
    deadline: Optional[str] = Field(None, description="Programın başvuru bitiş tarihi")
    official_url: Optional[str] = Field(None, description="Programın resmi web sitesi veya başvuru sayfasının URL'si")  


    #opsiyonel alanlar
    sub_category: Optional[str] = Field(None, description="Programın alt kategorisi veya alt destek türü")
    support_type: Optional[str] = Field(None, description="Destek türü (Örn: Hibe, kredi, yatırım, vergi avantajı, teşvik)")
    max_amount_try: Optional[int] = Field(None, description="Destek miktarının maksimum değeri (TRY cinsinden)")
    max_amount_usd: Optional[int] = Field(None, description="Destek miktarının maksimum değeri (USD cinsinden)")
    conditions_summary: Optional[str] = Field(None, description="Destek programının başvuru koşullarının kısa özeti")
    application_status: Optional[str] = Field(None, description="Başvuru durumu: Açık veya Kapalı")
    start_date: Optional[datetime] = Field(None, description="Başvuru başlangıç tarihi")
    min_employee: Optional[int] = Field(None, description="Destek programının hedeflediği minimum çalışan sayısı")  
    max_employee: Optional[int] = Field(None, description="Destek programının hedeflediği maksimum çalışan sayısı") 
    founded_after: Optional[str] = Field(None, description="Destek programının hedeflediği kuruluş tarihi (bu tarihten sonra kurulan şirketler başvurabilir)") 

    

    