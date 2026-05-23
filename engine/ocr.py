import os
from PIL import Image

try:
    import pytesseract
    # Coba inisialisasi pytesseract
    pytesseract_available = True
except ImportError:
    pytesseract_available = False

# Daftar kata kunci simulasi berdasarkan nama file atau karakteristik gambar
MOCK_IMAGE_OCR = {
    'jakarta_libur': "Benarkah besok Jakarta libur nasional karena pemilu susulan?",
    'bansos_cair': "Pemerintah bagikan bantuan sosial tunai 10 juta rupiah lewat link telegram ini",
    'vaksin_chip': "Bahaya! Vaksin booster mengandung chip magnetik yang melacak tubuh kita",
    'gempa_megathrust': "Breaking News: Megathrust akan mengguncang Selat Sunda malam ini kekuatan 9.5 SR"
}

def extract_text_from_image(image_path: str, hint_text: str = None) -> str:
    """
    Mengekstrak teks dari gambar menggunakan pytesseract jika tersedia.
    Jika tidak tersedia atau gagal, menggunakan fallback cerdas berbasis nama file
    dan hint_text yang dikirimkan oleh pengguna/UI.
    """
    # Jika ada hint_text langsung dari input pengujian manual, prioritaskan itu
    if hint_text:
        return hint_text.strip()
        
    if not os.path.exists(image_path):
        return ""

    extracted = ""
    
    # 1. Coba gunakan Pytesseract jika modul terpasang
    if pytesseract_available:
        try:
            img = Image.open(image_path)
            extracted = pytesseract.image_to_string(img, lang='ind')
            # Coba bahasa inggris jika indonesia tidak terinstall atau kosong
            if not extracted.strip():
                extracted = pytesseract.image_to_string(img, lang='eng')
        except Exception as e:
            print(f"[OCR Warning] Gagal mengekstrak dengan Tesseract: {e}")

    # 2. Mekanisme Cadangan (Fallback) jika OCR kosong
    if not extracted.strip():
        filename = os.path.basename(image_path).lower()
        # Cari kecocokan kata kunci nama file untuk demo
        matched_demo = False
        for key, mock_text in MOCK_IMAGE_OCR.items():
            if key in filename:
                extracted = mock_text
                matched_demo = True
                break
                
        if not matched_demo:
            # Fallback generik jika tidak ada kecocokan demo
            extracted = "[Simulasi Teks dari Gambar]: Klaim isu nasional penting terkini hari ini"
            
    return extracted.strip()
