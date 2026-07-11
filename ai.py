import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Gemini Müştərisini başlatırıq
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
            model="gemini-3.5-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception:
        return user_query  # Xəta olarsa orijinal mətni saxla

def ask_gemini(question):
    # Öncə istifadəçinin səhvini düzəldirik (Mərhələ 1)
    corrected_term = get_corrected_search_term(question)

    SYSTEM_PROMPT = """
Sən UNEC Kitabxanasının rəsmi Süni İntellekt Assistentisən (UNEC Library AI Assistant). 
Sənin vəzifən UNEC tələbələrinə, müəllimlərinə və rəhbərliyə kitablar barədə mükəmməl rəqəmsal bələdçilik etməkdir.

İstifadəçi sənə kitab adı, mövzu və ya müəllif yazacaq. Sualda hərf səhvləri (məsələn: 'malyye', 'iqtisad', 'eynshteyn') və ya uzun cümlələr ola bilər.

Sənin cavab strukturun MÜTLƏQ və DAXİLƏN aşağıdakı formatda (emojilərlə və səliqəli) olmalıdır:

🎯 **Ağıllı Axtarış Düzəlişi**:
İlk olaraq istifadəçinin yazdığı mətndəki hərf səhvlərini və ya qarışıqlığı düzəlt. UNEC E-Kitabxana sisteminin (ALISA) tam dəqiq tapa bilməsi üçün ən doğru açar sözü (məsələn: "**Maliyyə**", "**İqtisadiyyatın prinsipləri**" və ya "**Eynşteyn**") qalın şriftlə tələbəyə göstər.

📚 **Tövsiyə Olunan Fundamental Kitablar**:
Həmin mövzu və ya açar söz üzrə dünyaca məşhur və mütləq oxunmalı olan 2 dənə əla kitabı, müəllifini və tələbəyə qazandıracağı faydanı bənd-bənd izah et.

🏢 **UNEC Kitabxana Fondları üzrə Bələdçi**:
Tələbəyə korpuslar barədə ümumi rəqəmsal naviqasiya ver:
- *1-ci Korpus (Əsas bina)*: Fundamental İqtisadiyyat, Maliyyə və Ümumi dərsliklər.
- *2-ci Korpus*: Marketinq, Biznesin idarə edilməsi və Menecment kitabları.
- *4-cü Korpus*: İnformasiya Texnologiyaları (İT), Mühəndislik və Rəqəmsal elmlər.

🔗 **Canlı Rəf və İnventar Nömrəsini Tapmaq Üçün**:
Tələbəyə bu cümləni və rəsmi linki mütləq kliklənən formada təqdim et:
"Kitabın kitabxana daxilindəki dəqiq otaq, rəf və inventar nömrəsini canlı görmək üçün [UNEC Elektron Kataloquna (ALISA)](https://e-library.unec.edu.az/alisaweb/#section-topline-2) daxil ola bilərsiniz. Sayt açıldıqdan sonra yuxarıda sizin üçün düzəltdiyim açar sözü axtarış xanasına yazmağınız kifayətdir!"

Qaydalar:
- Cavabları mütləq tam və səlis Azərbaycan dilində yaz.
- Çox nəzakətli, peşəkar və universitet səviyyəsinə uyğun ol.
- Özünü əsla Gemini və ya Google AI adlandırma. Sən UNEC-in rəsmi ağıllı köməkçisisən.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\nİstifadəçinin ilkin sualı:\n{question}\n\nDüzəldilmiş açar söz: {corrected_term}",
        )
        return response.text
    except Exception as e:
        return f"Süni intellekt modulunda müvəqqəti bağlantı xətası: {str(e)}"
