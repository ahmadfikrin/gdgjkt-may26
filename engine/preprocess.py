import re

# Daftar stop words Bahasa Indonesia yang umum untuk memfilter kata kunci penting
INDONESIAN_STOPWORDS = {
    'yang', 'dan', 'di', 'dari', 'untuk', 'adalah', 'itu', 'ini', 'dengan', 'ke', 'oleh',
    'pada', 'juga', 'saya', 'kamu', 'dia', 'mereka', 'kita', 'kami', 'anda', 'apakah',
    'benarkah', 'hoax', 'fakta', 'atau', 'tapi', 'namun', 'saja', 'bisa', 'ada', 'telah',
    'sudah', 'akan', 'ingin', 'dapat', 'sangat', 'bagaimana', 'kenapa', 'mengapa', 'apa',
    'siapa', 'kapan', 'dimana', 'kah', 'sih', 'dong', 'kok', 'lah', 'pun', 'tentang',
    'seperti', 'secara', 'sebagai', 'maka', 'karena', 'jika', 'kalau', 'bahwa', 'tersebut'
}

def clean_text(text: str) -> str:
    """
    Membersihkan teks dengan mengubah ke huruf kecil dan menghapus karakter non-alphanumeric.
    """
    if not text:
        return ""
    # Ubah ke huruf kecil
    text = text.lower()
    # Hapus URL
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # Hapus karakter non-alphanumeric (simpan spasi)
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    # Hapus spasi berlebih
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_keywords(text: str) -> list[str]:
    """
    Membersihkan teks dan mengekstrak kata kunci unik dengan menyaring stop words.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []
    words = cleaned.split()
    # Ambil kata yang unik dan tidak termasuk dalam stop words
    keywords = []
    for word in words:
        if word not in INDONESIAN_STOPWORDS and len(word) > 2:
            if word not in keywords:
                keywords.append(word)
    return keywords
