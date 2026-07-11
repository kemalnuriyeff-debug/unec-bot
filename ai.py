import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

SYSTEM_PROMPT = """
Sən UNEC Library AI Assistant-san.

Sənin vəzifən:
- UNEC tələbələrinə kömək etmək.
- Kitab tövsiyələri vermək.
- Elmi mənbələr haqqında məlumat vermək.
- Məqalə və tədqiqat üçün istiqamət göstərmək.
- Kitabxana xidmətlərini izah etməkimport os
import requests
import urllib.parse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def scrape_unec_library(book_name):
    """
    UNEC Elektron Kitabxana saytından (library.unec.edu.az) canlı axtarış edir
    və tapılan nəticələrin xam mətnini süni intellektə ötürür.
    """
    try:
        # Kitab adını internet linkinə uyğun formata salırıq
        encoded_query = urllib.parse.quote(book_name)
        
        # UNEC Kitabxanasının standart axtarış linki strukturunu hədəf alırıq
        search_url = f"http://library.unec.edu.az/search?q={encoded_query}"
        
        # Saytın bizi bot kimi bloklamaması üçün özümüzü insan kimi təqdim edirik
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # Sayta canlı sorğu göndəririk (Maksimum 10 saniyə gözləyirik)
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Saytdakı lazımsız dizayn, menyu və reklam kodlarını təmizləyirik
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
                
            # Səhifədə qalan təmiz mətnləri götürürük
            raw_text = soup.get_text(separator="\n")
            clean_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
            final_text = "\n".join(clean_lines)
            
            # Süni intellektə çox böyük yük getməməsi üçün ilk 6000 simvolu kəsirik
            return final_text[:6000]
        else:
            return f"UNEC Kitabxana saytı cavab vermədi (Status kodu: {response.status_code})"
            
    except Exception as e:
        # Əgər sayt tamamilə çökübsə və ya internet kəsilibsə bu xəta qayıdır
        return f"Canlı axtarış sistemində müvəqqəti texniki fasilə: {str(e)}"

def ask_gemini(question):
    # İstifadəçinin yazdığı mətni (kitab adını) rəsmi sayt daxilində canlı axtarırıq
    live_site_data = scrape_unec_library(question)

    SYSTEM_PROMPT = f"""
Sən UNEC Library AI Assistant-san. UNEC tələbələrinə və rəhbərliyinə kitab tapmaqda kömək edirsən.

Sənin qərar verməyin üçün UNEC Elektron Kitabxana saytından (library.unec.edu.az) gələn CANLI AXtARIŞ NƏTİCƏLƏRİ aşağıdadır:
---
{live_site_data}
---

Qaydalar və Vəzifən:
1. Yuxarıda verilən canlı sayt məlumatını diqqətlə analiz et. Əgər istifadəçinin axtardığı kitab (və ya ona yaxın nəticə) bu mətndə VARSA, kitabın adını, müəllifini, hansı korpusda/filialda olduğunu və əgər qeyd edilibsə RƏF, SIRA və OTAQ nömrəsini daxildən tapıb tələbəyə çox səliqəli, qalın şriftlərlə və emojilərlə təqdim et. Sayt linkini də qeyd edə bilərsən.
2. Əgər yuxarıdakı mətndə heç bir kitab tapılmayıbsa və ya "Sayt cavab vermədi" kimi xətalar varsa, öz daxili intellektindən istifadə edərək tələbəyə həmin mövzuda oxuna biləcək 2-3 əla kitab tövsiyə et. Lakin bu zaman yerini bilmədiyin üçün əsla rəf nömrəsi uydurma! Nəzakətlə bu cümləni yaz:
   "📍 Qeyd: Bu kitab üzrə elektron kataloqda canlı axtarış etdim, lakin dəqiq rəf nömrəsini təsdiqləmək üçün kitabxana daxilindəki fiziki terminallara yaxınlaşmağınız və ya uneclibrary saytından birbaşa yoxlamağınız xahiş olunur."
3. Həmişə çox nəzakətli, peşəkar ol və cavabları mütləq Azərbaycan dilində yaz.
4. Özünü heç vaxt Gemini, Google və ya başqa bir AI adlandırma. Sən UNEC-in rəsmi rəqəmsal kitabxanaçısan.
"""

    response = client.models.generate_content(
        model="models/gemini-3.5-flash",
        contents=f"{SYSTEM_PROMPT}\n\nİstifadəçinin sualı:\n{question}",
    )
    return response.text
