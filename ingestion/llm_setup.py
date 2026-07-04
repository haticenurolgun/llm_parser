from google import genai
from google.genai import types
from tenacity import retry, wait_exponential, stop_after_attempt
from ingestion.models import GrantProgram
import os

#tenacity kod ilk denemede hata alırsa, exponential backoff ile tekrar denemek için kullanılır.

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@retry(wait=wait_exponential(multiplier=1, min=4, max=15), stop=stop_after_attempt(5))

async def exact_structered_data(cleaned_text: str) -> GrantProgram:

    f"""
    Temizlenmiş metni Gemini'ye asenkron olarak gönderir ve çıktının, 
    sıkı bir şekilde doğrulanmış GrantProgram Pydantic modeliyle uyumlu olmasını sağlar.
    API hız sınırlamalarına karşı dayanıklılık sağlamak için tenacity kullanılır.
    """
    
    #llm'in cevabını nasıl (hangi formatta) üretmesi gerektiğini belirtmek için GenerateContentConfig kullanıyoruz.
    config = types.GenerateContentConfig(
        response_mime_type="application/json", #cevabın JSON formatında olmasını istiyorum
        response_schema=GrantProgram,
        temperature=0.1, # modelin daha deterministik ve tutarlı cevaplar üretmesini sağlamak için düşük sıcaklık kullanıyoruz
    )


   
    prompt = f"""
    Aşağıdaki metni analiz et ve verileri istenen formatta çıkar.

   ÖNEMLİ KURALLAR:
    1. Anlamsal Eşleştirme (Semantic Matching): Aradığın alanın adı metinde birebir geçmeyebilir. Eş anlamlı kelimeleri, dolaylı anlatımları ve metnin genel bağlamını dikkate alarak çıkarım yap.
       - Örnek ("Şirket Şartı"): "tüzel kişilik gereklidir", "vergi levhası zorunludur", "işletme kaydı belgesi" gibi ifadeleri şirket kurulusu sarti olarak değerlendir.
       - Örnek ("Resmi Link"): "başvuru adresi", "detaylar için web sitemiz", "portala gitmek için" ibarelerinin yanındaki URL'leri resmi URL olarak al.
    2. Format Katılığı: Her alan için şemadaki (description) açıklamasında belirtilen formata AYNEN uy.
    3. Sayısal Alanlar: Sayısal alanlarda (örnek: destek orani) sadece rakam yaz, % işareti veya başka bir yazı ekleme.
    4. Sınırlandırma: Bilgi metinde hiçbir şekilde, dolaylı yoldan bile yoksa tahmin etme, o alan için "null" döndür.

    Analiz Edilecek Metin: {cleaned_text}""" 


    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash-lite",  
        contents=prompt,
        config=config
    )

    # Pydantic modelini kullanarak doğrulama yapıyoruz
    return GrantProgram.model_validate_json(response.text)  


@retry(wait=wait_exponential(multiplier=1, min=1, max=5), stop=stop_after_attempt(3))
async def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Verilen metin listesini (chunk'ları) tek seferde Gemini Embedding API'sine gönderir.
    Döngü kurmadan 15-20 metni aynı anda yolladığı için ağ hızını inanılmaz artırır.
    Her bir metin için 768 boyutlu vektör (float listesi) döner.
    """
    # client objesinin dosyanın üst kısımlarında genai.Client(...) olarak tanımlandığını varsayıyoruz.
    result = await client.aio.models.embed_content(
        model='text-embedding-0001',  # Gemini Embedding modeli
        contents=texts,
        task_type="RETRIEVAL_DOCUMENT" # Supabase'de arama yapacağımız için bu tip optimize eder
    )
    
    # API'den dönen karmaşık objenin içinden sadece matematiksel vektörleri (float listelerini) çekip alıyoruz
    embeddings = [embedding.values for embedding in result.embeddings]
    return embeddings