import urllib.parse
from engine.preprocess import extract_keywords

# Simulasi database pencarian web cadangan dari TurnBackHoax & Kominfo
MOCK_WEB_SEARCH_DB = [
    {
        "keywords": ["banjir", "jakarta", "tanggul", "jebol"],
        "title": "Banjir Bandang Jakarta Karena Tanggul Baswedan Jebol",
        "status": "🛑 HOAX",
        "confidence": 85,
        "explanation": "BPBD DKI Jakarta menyatakan bahwa genangan air di beberapa wilayah disebabkan oleh curah hujan yang ekstrem, bukan karena tanggul jebol. Informasi mengenai tanggul jebol adalah disinformasi lama yang diposting kembali.",
        "source": "https://turnbackhoax.id/2026/05/salah-banjir-tanggul-jebol-jakarta/",
        "category": "Bencana Alam"
    },
    {
        "keywords": ["gempa", "surabaya", "megathrust"],
        "title": "Gempa Bumi Megathrust Menghancurkan Kota Surabaya Hari Ini",
        "status": "🛑 HOAX",
        "confidence": 92,
        "explanation": "BMKG Klas I Juanda menegaskan Surabaya tidak berada langsung di zona megathrust selatan Jawa Timur. Tidak ada gempa bumi merusak berkekuatan tinggi di Surabaya hari ini.",
        "source": "https://www.komdigi.go.id/berita/berita-hoaks",
        "category": "Bencana Alam"
    },
    {
        "keywords": ["pajak", "motor", "gratis", "pemutihan"],
        "title": "Program Pemutihan dan Pembebasan Pajak Motor Seluruh Indonesia",
        "status": "⚠️ SEBAGIAN BENAR / BELUM DAPAT DIPASTIKAN",
        "confidence": 75,
        "explanation": "Program pemutihan pajak kendaraan bermotor (PKB) merupakan wewenang masing-masing Samsat Provinsi Daerah. Beberapa provinsi memang sedang mengadakan program ini, namun tidak serentak di seluruh Indonesia.",
        "source": "https://kominfo.go.id/berita/pemutihan-pajak-motor-daerah/",
        "category": "Pemerintahan"
    }
]

def search_fallback_sources(query: str) -> dict:
    """
    Melakukan pencarian fallback jika basis pengetahuan utama tidak menemukan kecocokan.
    Mencari entri relevan berdasarkan pencocokan kata kunci di database pencarian luar.
    """
    query_keywords = extract_keywords(query)
    if not query_keywords:
        return None
        
    best_match = None
    max_matches = 0
    
    for entry in MOCK_WEB_SEARCH_DB:
        # Hitung berapa banyak kata kunci query yang cocok dengan entri database cadangan
        matches = len(set(query_keywords).intersection(set(entry["keywords"])))
        if matches > max_matches:
            max_matches = matches
            best_match = entry
            
    # Kembalikan hasil jika ada minimal 2 kata kunci yang cocok
    if best_match and max_matches >= 2:
        return {
            "title": best_match["title"],
            "claim": query,
            "status": best_match["status"],
            "confidence": best_match["confidence"],
            "explanation": best_match["explanation"],
            "source": best_match["source"],
            "category": best_match["category"],
            "engine_used": "Fallback Engine (TurnBackHoax & Kominfo Web Crawler)"
        }
        
    # Jika tidak ditemukan kecocokan di database fallback, kembalikan status tidak cukup informasi
    # Sesuai PRD: "Jika ragu atau data tidak cukup, skor harus rendah dan mengembalikan nilai 'Informasi belum cukup untuk disimpulkan'"
    return {
        "title": "Informasi Belum Cukup untuk Disimpulkan",
        "claim": query,
        "status": "⚠️ SEBAGIAN BENAR / BELUM DAPAT DIPASTIKAN",
        "confidence": 30,
        "explanation": "Sistem pemeriksa fakta belum menemukan rujukan resmi atau bukti konkrit di basis pengetahuan utama (GitHub) maupun di portal TurnBackHoax dan Komdigi untuk memverifikasi kebenaran klaim ini.",
        "source": "https://www.komdigi.go.id/berita/berita-hoaks",
        "category": "Belum Terverifikasi",
        "engine_used": "Fallback Engine (No Match Found)"
    }
