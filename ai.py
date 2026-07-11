import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# MƏCBURİ: main.py faylının açılışda (import zamanı) çökməməsi üçün qlobal client obyekti saxlayırıq
class DummyClient:
    pass
client = DummyClient()

def scrape_unec_live_catalog(book_name):
    """
    UNEC rəsmi kataloqundan canlı məlumatları qazıyır.
    """
    try:
        encoded_query = urllib.parse.quote(book_name)
        search_url = f"http://library.unec.edu.az/search?q={encoded_query}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            raw_text = soup.get_text(separator="\n")
            clean_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
            return "\n".join(clean_lines)[:6000]
        return "empty"
    except Exception:
        return "empty"

def ask_gemini(question):
    """
    Tamamilə PULSUZ, LİMİTSİZ və APİ KEY tələb etməyən alternativ super server.
    Funksiyanın adını dəyişmirik ki, main.py faylımız zədələnməsin.
    """
    # Canlı sayt məlumatını çəkirik
    live_site_data = scrape_unec_live_catalog(question)

    SYSTEM_PROMPT = f"""
Sən UNEC Kitabxanasının rəsmi Süni İntellekt Assistentisən (UNEC Library AI Assistant).

Sənin vəzifən istifadəçinin sorğusunu və UNEC Elektron Kitabxana saytından gələn bu xam mətni eyni anda analiz etməkdir:
---
Sayt Məlumatı: {live_site_data}
---

İstifadəçi sorğuda hərf səhvi edibsə (məsələn: 'malyye', 'iqtisad'), onu daxilən düzəlt və cavabında "Axtarılan mövzu: **Maliyyə**" kimi qeyd et.

QƏTİ QAYDALAR:
1. Əgər yuxarıdakı sayt məlumatında həqiqətən kitabın REAL korpusu, otağı və rəf nömrəsi varsa, onları mətndən çıxarıb tələbəyə təqdim et.
2. Əgər saytdan gələn məlumat boşdursa və ya daxilində real rəf nömrəsi tapılmayıbsa, ƏSLA ÖZÜNDƏN RƏQƏM VƏ RƏF UYDURMA! Yalan danışmaq qadağandır.
3. Real rəf tapılmadıqda tələbəyə dürüstcə bu mesajı yaz:
   "📍 Qeyd: Bu mövzu üzrə kitablarımız mövcuddur, lakin rəsmi elektron kataloq bazasında rəf və sıra nömrəsi qeyd edilməmişdir. Kitabın fiziki yerini dəqiqləşdirmək üçün kitabxana daxilindəki terminallara və ya əməkdaşlarımıza yaxınlaşmağınız xahiş olunur."
4. Mövzuya uyğun 2 dənə dünyaca məşhur kitab tövsiyə et. Cavabları tam Azərbaycan dilində və səliqəli emojilərlə yaz. Özünü əsla başqa bir AI adlandırma, sən UNEC-in öz ağıllı köməkçisisən.
"""

    try:
        # Pulsuz və limitsiz qlobal süni intellekt qapısı
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"İstifadəçinin sualı: {question}"}
            ],
            "model": "openai" # Ən stabil və ağıllı mühit
        }
        
        # Sorğunu göndəririk
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.text
        else:
            return f"Alternativ server xətası (Status kod: {response.status_code})"
            
    except Exception as e:
        return f"Alternativ süni intellekt modulunda bağlantı xətası: {str(e)}"
