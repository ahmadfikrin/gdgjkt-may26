from difflib import SequenceMatcher
from engine.preprocess import extract_keywords, clean_text

def get_string_similarity(a: str, b: str) -> float:
    """
    Menghitung tingkat kemiripan rasio antara dua string teks menggunakan SequenceMatcher.
    """
    return SequenceMatcher(None, clean_text(a), clean_text(b)).ratio()

def get_jaccard_similarity(keywords_a: list[str], keywords_b: list[str]) -> float:
    """
    Menghitung tingkat kemiripan Jaccard berdasarkan irisan set kata kunci unik.
    """
    if not keywords_a or not keywords_b:
        return 0.0
    set_a = set(keywords_a)
    set_b = set(keywords_b)
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return float(intersection) / union if union > 0 else 0.0

def find_best_match(query: str, kb_issues: list[dict]) -> tuple[dict, float]:
    """
    Mencari entri basis pengetahuan terbaik yang memiliki kemiripan tertinggi dengan kueri pengguna.
    Mengembalikan tuple (entri_kb, skor_kemiripan_0_sampai_1).
    """
    query_keywords = extract_keywords(query)
    query_cleaned = clean_text(query)
    
    best_match = None
    max_score = 0.0
    
    for issue in kb_issues:
        # 1. Hitung kemiripan judul
        title_similarity = get_string_similarity(query_cleaned, clean_text(issue["title"]))
        
        # 2. Hitung kemiripan klaim/deskripsi
        claim_similarity = get_string_similarity(query_cleaned, clean_text(issue["claim"]))
        
        # 3. Hitung Jaccard similarity kata kunci
        issue_keywords = extract_keywords(issue["title"] + " " + issue["claim"])
        jaccard_similarity = get_jaccard_similarity(query_keywords, issue_keywords)
        
        # Bobot gabungan: 40% Judul, 30% Klaim, 30% Jaccard kata kunci
        combined_score = (title_similarity * 0.40) + (claim_similarity * 0.30) + (jaccard_similarity * 0.30)
        
        # Bonus kecocokan keyword penuh (jika ada irisan kata kunci penting)
        intersection_count = len(set(query_keywords).intersection(set(issue_keywords)))
        if intersection_count >= 2:
            combined_score += 0.05
            
        combined_score = min(combined_score, 1.0) # Batas atas 1.0
        
        if combined_score > max_score:
            max_score = combined_score
            best_match = issue
            
    return best_match, max_score
