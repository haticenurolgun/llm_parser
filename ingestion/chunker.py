"""
Hibe metinlerini satır sonlarından böler.
"""

def chunk_text(text: str, max_words_per_chunk: int = 400, overlap_lines: int = 1) -> list[str]:
    """
    Metni satır sonlarından (\n) ayırır.
    Kelime sınırı (400) aşılana kadar bu satırları aynı paketin (chunk) içine ekler.
    
    Args:
        text: Parçalanacak ham metin.
        max_words_per_chunk: Bir parçanın ulaşabileceği maksimum kelime sayısı.
        overlap_lines: Anlam kopukluğu olmasın diye bir sonraki parçaya 
                       önceki parçanın son kaç satırının ekleneceği.
    """
    if not text or not text.strip():
        return []

    # 1. Metni satır sonlarından (\n) listeye ayır ve boş satırları temizle
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    chunks = []
    start_index = 0

    # Tüm satırlar bitene kadar devam et
    while start_index < len(lines):
        current_chunk_lines = []
        current_word_count = 0
        end_index = start_index

        # 2. Kelime sınırı dolana kadar mevcut chunk'ın içine satır ekle
        while end_index < len(lines):
            line = lines[end_index]
            line_words = len(line.split())
            
            # Eğer bu yeni satırı eklediğimizde sınır aşılacaksa ve 
            # paketimizin içinde zaten en az 1 satır varsa, daha fazla ekleme yapma (döngüyü kır)
            if current_word_count + line_words > max_words_per_chunk and current_chunk_lines:
                break
                
            current_chunk_lines.append(line)
            current_word_count += line_words
            end_index += 1

        # 3. Oluşan bu paragraf grubunu tek bir metin haline getirip listeye kaydet
        # Satırları birleştirirken araya tekrar bir boşluk veya \n koyuyoruz
        chunk_string = "\n".join(current_chunk_lines)
        chunks.append(chunk_string)

        # 4. SİHİRLİ KISIM (OVERLAP - ÖRTÜŞME)
        # Bir sonraki parçaya geçerken, en son kaldığımız yerden (end_index) değil,
        # belirlediğimiz satır sayısı kadar geriden başlıyoruz ki bağlam kopmasın.
        step_forward = (end_index - start_index) - overlap_lines
        
        # Güvenlik Kilidi: Eğer overlap sayısı çok büyükse ve kod geriye doğru gidip
        # sonsuz döngüye girme riski yaratıyorsa, en az 1 satır ilerlemesini zorunlu kılıyoruz.
        if step_forward <= 0:
            step_forward = 1
            
        start_index += step_forward

    return chunks