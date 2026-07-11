import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Aktiv açarları sistemdən oxuyuruq
key1 = os.getenv("GEMINI_API_KEY_1") or os.getenv("GEMINI_API_KEY")
key2 = os.getenv("GEMINI_API_KEY_2")

# MƏCBURİ: main.py faylının açılışda çökməməsi üçün qlobal client obyektini yaradırıq
client = genai.Client(api_key=key1 if key1 else "dummy_key")

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
2. Əgər saytdan gələn məlumat boşdursa və ya daxilində real rəf nömrəsi tapılmayıbsa, ƏSLA ÖZÜNDƏN RƏQƏM VƏ RƏF UYDURMA!
3. Real rəf tapılmadıqda tələbəyə dürüstcə bu mesajı yaz:
   "📍 Qeyd: Bu mövzu üzrə kitablarımız mövcuddur, lakin rəsmi elektron kataloq bazasında rəf və sıra nömrəsi qeyd edilməmişdir. Kitabın fiziki yerini dəqiqləşdirmək üçün kitabxana daxilindəki terminallara və ya əməkdaşlarımıza yaxınlaşmağınız xahiş olunur."
4. Mövzuya uyğun 2 dənə dünyaca məşhur kitab tövsiyə et. Cavabları tam Azərbaycan dilində və səliqəli emojilərlə yaz. Özünü əsla Gemini adlandırma.
"""

    keys_to_try = [key1, key2]
    last_error = "Açarlar təyin edilməyib"
    
    for key in keys_to_try:
        if not key:
            continue
        try:
            # Hər cəhddə aktiv açarla sorğu göndəririk
            active_client = genai.Client(api_key=key)
            response = active_client.models.generate_content(
                model="gemini-3.5-flash",
                contents=f"{SYSTEM_PROMPT}\n\nİstifadəçinin sualı: {question}",
            )
            return response.text
        except Exception as e:
            last_error = str(e)
            continue
            
    return f"Süni intellekt modulunda müvəqqəti bağlantı xətası: {last_error}"
