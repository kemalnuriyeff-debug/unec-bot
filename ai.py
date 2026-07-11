import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def get_corrected_search_term(user_query):
    """
    Mərhələ 1: İstifadəçinin yazdığı hərf səhvlərini və ya uzun cümlələri düzəldir,
    UNEC saytının başa düşəcəyi ən ideal 1-2 təmiz açar sözü çıxarır.
    """
    try:
        prompt = f"""
        Sən bir süni intellekt filtrisən. İstifadəçi UNEC kitabxanasından kitab axtarır. 
        Onun yazdığı mətndə hərf səhvləri, bütöv cümlələr və ya lazımsız sözlər ola bilər.
        Sənin tək vəzifən bu mətndən sırf kitabın ən doğru, rəsmi və dəqiq adını (və ya müəllifini) çıxarmaq və hərf səhvlərini düzəltməkdir.
        UNEC axtarış sisteminə (library.unec.edu.az) veriləcək ən ideal 1-2 açar sözü qaytar.

        Nümunələr:
        - "mənə maliyye sahəsində kitab ver" -> "Maliyyə"
        - "malyye" -> "Maliyyə"
        - "iqtisadın prinsipləri mənkyu" -> "İqtisadiyyatın prinsipləri"
        - "eynshteyn nisbiliyin" -> "Eynşteyn"
        - "makroiqtisad" -> "Makroiqtisadiyyat"
        - "menecment düyməsi" -> "Menecment"

        İstifadəçinin yazdığı mətn: "{user_query}"
        
        Cavab olaraq YALNIZ düzəldilmiş təmiz axtarış sözünü qaytar. Heç bir əlavə izah, nöqtə, cümlə və ya emoci yazma!
        """
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception:
        return user_query  # Xəta olarsa orijinal mətni saxla

def scrape_unec_library(book_name):
    """
    Mərhələ 2: Gemini tərəfindən düzəldilmiş dəqiq sözlə UNEC saytından canlı axtarış edir.
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
            final_text = "\n".join(clean_lines)
            
            return final_text[:6000]
        else:
            return "empty"
            
    except Exception:
        return "empty"

def ask_gemini(question):
    # Öncə istifadəçinin səhvini düzəldirik (Mərhələ 1)
    corrected_term = get_corrected_search_term(question)
    
    # Düzəldilmiş sözlə saytda canlı axtarış edirik (Mərhələ 2)
    live_site_data = scrape_unec_library(corrected_term)

    SYSTEM_PROMPT = f"""
Sən UNEC Library AI Assistant-san. UNEC tələbələrinə və rəhbərliyinə kitab tapmaqda kömək edirsən.

Biz istifadəçinin yazdığı mətndəki açar sözü tapıb "{corrected_term}" olaraq UNEC Elektron Kitabxanasında canlı axtardıq. Saytdan gələn CANLI NƏTİCƏLƏR:
---
{live_site_data}
---

Sənin Vəzifən:
1. Yuxarıdakı canlı sayt məlumatını oxu. Əgər daxildə həqiqətən kitab(lar) tapılıbsa, həmin kitabların adını, müəllifini, yerləşdiyi korpusu/filialı, rəf və otaq nömrələrini çox səliqəli, qalın şriftlərlə və emojilərlə tələbəyə təqdim et.
2. Əgər yuxarıdakı mətndə heç bir kitab nəticəsi yoxdursa (və ya mətn çox boşdursa və ya "empty" yazılıbsa), öz daxili super intellektindən istifadə edərək tələbəyə "{corrected_term}" mövzusunda oxuna biləcək 2-3 dənə dünyaca məşhur əla kitab tövsiyə et. Lakin yerini bilmədiyin üçün əsla rəf nömrəsi uydurma! Və nəzakətlə qeyd et ki, bu mövzu üzrə rəsmi kataloqda dəqiq rəf tapılmadı, lakin bu kitabları oxuya bilərlər.
3. Həmişə çox peşəkar ol, cavabları mütləq Azərbaycan dilində yaz və özünü heç vaxt Gemini adlandırma. Sən UNEC-in rəsmi ağıllı köməkçisisən.
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=f"{SYSTEM_PROMPT}\n\nİstifadəçinin ilkin sualı:\n{question}",
    )
    return response.text
