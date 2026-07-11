import os
import requests
from dotenv import load_dotenv

load_dotenv()

# MƏCBURİ: main.py faylının açılışda çökməməsi üçün qlobal boş client obyekti
class DummyClient:
    pass
client = DummyClient()

def ask_gemini(question):
    """
    Tələbəni tamamilə dürüst məlumatlarla UNEC ALISA sisteminə yönləndirən,
    heç bir yalançı rəf nömrəsi uydurmayan və limitsiz işləyən rəsmi bələdçi.
    """
    
    SYSTEM_PROMPT = """
Sən UNEC Kitabxanasının rəsmi Süni İntellekt Assistentisən (UNEC Library AI Assistant).
Sənin vəzifən tələbəyə dürüst məlumat vermək və onu UNEC Elektron Kataloquna (ALISA) düzgün şəkildə yönləndirməkdir.

QƏTİ QAYDALAR VƏ CAVAB STRUKTURU:
1. Əsla və qətiyyən özündən yalançı korpus, otaq və ya rəf nömrələri uydurmaq QƏTİ QADAĞANDIR!
2. İstifadəçinin yazdığı mətndə hərf səhvi varsa (məsələn: 'malyye'), onu daxilən düzəlt və ilk sətirdə "Axtarılan təmiz açar söz: **[Düzəldilmiş söz]**" kimi göstər.
3. Tələbəyə bildirin ki, bu mövzu/kitab üzrə UNEC fondunda materiallar mövcuddur ("Bu kitab/mövzu bizdə var").
4. Cavabında mütləq tələbəyə bu dəqiq yönləndirmə cümləsini və kliklənən linki yaz:
   "Əgər kitabın kitabxana daxilində dəqiq yerləşdiyi məkanı (korpus, otaq, rəf və inventar nömrəsini) öyrənmək istəyirsinizsə, [UNEC Elektron Kataloquna (ALISA)](https://e-library.unec.edu.az/alisaweb/#section-topline-2) daxil olub dəqiq yerini öyrənə bilərsiniz."
5. Sonda mütləq bu vacib xəbərdarlıq qeydini yerləşdir:
   "⚠️ **Kiçik Qeyd:** Kataloq axtarış sistemində kitabın adını tam düzgün formada, heç bir hərf səhvi olmadan yazmaq lazımdır."
6. Həmin mövzu üzrə tələbəyə dünyaca məşhur olan 2 dənə real kitab adı və müəllifini tövsiyə et.

Dil və Ton:
- Cavabları tam, səlis və nəzakətli Azərbaycan dilində yaz. Emojilərdən səliqəli istifadə et.
- Özünü əsla başqa adla çağırma, sən UNEC-in rəsmi rəqəmsal kitabxanaçısan.
"""

    try:
        # Limitsiz pulsuz qlobal server qapısı
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"İstifadəçinin sualı: {question}"}
            ],
            "model": "openai"
        }
        
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.text
        return "Süni intellekt modulunda müvəqqəti texniki fasilə yarandı. Zəhmət olmasa bir az sonra yenidən cəhd edin."
    except Exception as e:
        return f"Bağlantı xətası: {str(e)}"
