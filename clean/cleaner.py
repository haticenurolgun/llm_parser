from bs4 import BeautifulSoup

def clean_html(raw_html: str) -> str:
    """
    html'deki gereksiz etiketleri ve boşlukları temizler, sadece metni döner.
"""
    if not raw_html:
        return ""

    # html kodunu bir ağaç yapısına çeviriyoruz ki içinde gezebilelim
    html_tree = BeautifulSoup(raw_html, "html.parser")

    # metin olarak işimize yaramayacak etiketler
    tags_to_remove = ["script", "style", "noscript", "nav", "footer", "header", "svg", "button"]

    for tag_name in tags_to_remove:
        found_tags = html_tree.find_all(tag_name)
        for unw_tag in found_tags:
            unw_tag.decompose()

    # artık sadece asıl metni alıyoruz
    # separator=" " => kelimeler birbirine yapışmasın diye
    # strip=True => baştaki sondaki boşlukları temizler
    
    final_text = html_tree.get_text(separator=" ", strip=True)

    return final_text


  


