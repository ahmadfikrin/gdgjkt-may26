from engine.matcher import find_best_match
from engine.fallback import search_fallback_sources

def evaluate_fact_checking(query: str, kb_issues: list[dict]) -> dict:
    """
    Mengevaluasi klaim/kueri pengguna terhadap basis pengetahuan utama (GitHub Issues).
    Jika skor kemiripan rendah (< 0.55), maka sistem beralih ke pencarian fallback.
    Mengembalikan payload terstruktur yang sesuai dengan spesifikasi PRD.
    """
    if not query or not query.strip():
        return {
            "status": "⚠️ SEBAGIAN BENAR / BELUM DAPAT DIPASTIKAN",
            "confidence": 0,
            "title": "Kueri Kosong",
            "explanation": "Kueri yang Anda masukkan kosong. Silakan kirimkan klaim teks, tautan, atau gambar yang ingin diverifikasi.",
            "source": "https://www.komdigi.go.id/berita/berita-hoaks",
            "category": "N/A",
            "engine_used": "Scoring Engine (Empty Input)"
        }

    # 1. Lakukan pencarian di basis pengetahuan utama
    best_issue, similarity_score = find_best_match(query, kb_issues)
    
    # Ambang batas keyakinan utama adalah 55%
    if best_issue and similarity_score >= 0.55:
        # Konversi skor kemiripan desimal ke persentase (e.g., 0.85 -> 85%)
        # Kita kombinasikan skor kemiripan tekstual dengan keyakinan artikel dasar
        base_confidence = best_issue["confidence"]
        final_confidence = int((base_confidence * 0.70) + (similarity_score * 30))
        final_confidence = min(max(final_confidence, 55), 99)
        
        return {
            "status": best_issue["status"],
            "confidence": final_confidence,
            "title": best_issue["title"],
            "explanation": best_issue["explanation"],
            "source": best_issue["source"],
            "category": best_issue["category"],
            "engine_used": "Primary Knowledge Base (GitHub Issue #2)"
        }
        
    # 2. Jika tidak ditemukan atau skor rendah, gunakan Fallback Engine
    fallback_result = search_fallback_sources(query)
    
    return fallback_result
