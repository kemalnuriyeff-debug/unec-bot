import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Gemini Müştərisini başladırıq
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def get_corrected_search_term(user_query):
    """
    Mərhələ 1: Tələbənin yazdığı mətndən hərf səhvlərini təmizləyir.
    """
    try:
        prompt = f"Sən hərf səhvi düzəldən filtrisən. Bu mətndəki səhvləri düzəldib UNEC kitabxana axtarışı üçün 1 dənə təmiz açar söz qaytar (Məsələn: 'malyye' yazılarsa 'Maliyyə' qaytar). Mətn: {user_query}. Cavab olaraq YALNIZ düzəldilmiş təmiz sözü qaytar, əlavə heç nə yazma."
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception:
        return user_query

def scrape_unec_live_catalog(book_name):
    """
    Mərhələ 2: UNEC rəsmi kataloqundan (library.unec.edu.az) REAL məlumatları canlı qazıyır.
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
            
            # Lazımsız dizayn kodlarını təmizləyirik
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
                
            raw_text = soup.get_text(separator="\n")
            clean_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
            return "\n".join(clean_lines)[:6000] # İlk 6000 simvolu ötürürük
        return "empty"
    except Exception:
        return "empty"

def ask_gemini(question):
    # 1. Sözü düzəldirik
    corrected_term = get_corrected_search_term(question)
    
    # 2. Saytdan REAL məlumatı çəkirik
    live_site_data = scrape_unec_live_catalog(corrected_term)

    SYSTEM_PROMPT = f"""
Sən UNEC Kitabxanasının rəsmi Süni İntellekt Assistentisən (UNEC Library AI Assistant).
Sənin tək vəzifən aşağıda UNEC Elektron Kitabxana saytından gələn REAL VƏ CANLI mətni oxuyub tələbəyə məlumat verməkdir.

Axtarılan təmiz söz: "{corrected_term}"
UNEC Saytından gələn REAL CANLI MƏLUMATLAR:
---
{live_site_data}
---

QƏTİ QAYDALAR:
1. Yuxarıdakı canlı məlumatı diqqətlə analiz et. Əgər bu mətndə axtarılan kitabın HƏQİQİ korpusu, otağı, rəf nömrəsi və ya inventar kodu VARSA, onları mətndən tap və tələbəyə çox səliqəli, qalın şriftlərlə təqdim et.
2. Əgər yuxarıdakı canlı mətndə heç bir kitab tapılmayıbsa və ya kitab tapılsa da RƏF NÖMRƏSİ QEYD EDİLMƏYİBSƏ, ƏSLA VƏ QƏTİYYƏN ÖZÜNDƏN RƏF NÖMRƏSİ UYDURMA! Yalan rəqəmlər yazmaq qəti qadağandır.
3. Real rəf nömrəsi tapılmadıqda tələbəyə dürüstcə bu mesajı yaz:
   "📍 Qeyd: Bu mövzu üzrə kitablarımız mövcuddur, lakin rəsmi elektron kataloq bazasında rəf və sıra nömrəsi qeyd edilməmişdir. Kitabın fiziki yerini dəqiqləşdirmək üçün kitabxana daxilindəki terminallara və ya əməkdaşlarımıza yaxınlaşmağınız xahiş olunur."
4. Həmişə çox peşəkar ol, cavabları mütləq tam Azərbaycan dilində yaz və özünü əsla Gemini adlandırma.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\nİstifadəçinin ilkin sualı:\n{question}",
        )
        return response.text
    except Exception as e:
        return f"Süni intellekt modulunda müvəqqəti bağlantı xətası: {str(e)}"
