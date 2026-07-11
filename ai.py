import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Əsas API açarını sistemdən oxuyuruq
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY_1")

# MƏCBURİ: main.py faylının açılışda çökməməsi üçün qlobal client obyekti
client = genai.Client(api_key=api_key if api_key else "dummy_key")

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

    # MODEL HOVUZU: Birində limit (429) bitən kimi, dərhal digərinə keçəcək!
    models_to_try = ["gemini-3.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    last_error = "Heç bir model cavab vermədi"

    for model_name in models_to_try:
        try:
            # Hər dövrdə ehtiyat modeli işə salmağa çalışırıq
            active_client = genai.Client(api_key=api_key)
            response = active_client.models.generate_content(
                model=model_name,
                contents=f"{SYSTEM_PROMPT}\n\nİstifadəçinin sualı: {question}",
            )
            return response.text # Əgər uğurludursa, dərhal cavabı bota qaytarır
        except Exception as e:
            last_error = str(e)
            continue # Əgər 429 xətası alsaq, dayanmır, növbəti ehtiyat modelə keçir
            
    return f"Süni intellekt modulunda müvəqqəti bağlantı xətası: {last_error}"
