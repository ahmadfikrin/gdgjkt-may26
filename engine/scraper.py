import requests
from bs4 import BeautifulSoup
import urllib.parse

# User-Agent standar agar scraper tidak diblokir oleh situs web
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
}

def scrape_url_content(url: str) -> dict:
    """
    Melakukan scraping pada URL untuk mengambil Judul (Title), Deskripsi Meta,
    dan paragraf pertama dari konten untuk dianalisis oleh Fact-Checking Engine.
    """
    result = {
        "url": url,
        "title": "",
        "description": "",
        "content": "",
        "success": False,
        "error": None
    }
    
    # Validasi URL sederhana
    parsed_url = urllib.parse.urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        result["error"] = "Format URL tidak valid"
        return result
        
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # Cek jika konten bertipe HTML
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            result["error"] = "Tautan bukan halaman HTML yang valid"
            return result
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Ambil Judul Halaman
        title_tag = soup.find('title')
        title = title_tag.string.strip() if title_tag else ""
        if not title:
            # Cari og:title
            og_title = soup.find('meta', property='og:title')
            title = og_title['content'].strip() if og_title and og_title.get('content') else ""
            
        # 2. Ambil Meta Description
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc['content'].strip()
        else:
            og_desc = soup.find('meta', property='og:description')
            if og_desc and og_desc.get('content'):
                description = og_desc['content'].strip()
                
        # 3. Ambil Paragraf Konten Utama
        paragraphs = soup.find_all('p')
        content_paragraphs = []
        for p in paragraphs:
            text = p.get_text().strip()
            # Hanya ambil paragraf yang memiliki teks signifikan
            if len(text) > 20 and not text.startswith(('cookie', 'iklan', 'iklan', 'javascript', 'baca juga')):
                content_paragraphs.append(text)
                if len(content_paragraphs) >= 3: # Ambil maksimal 3 paragraf awal
                    break
                    
        content = " ".join(content_paragraphs)
        
        # Jika p tidak ada, coba ambil tag artikel
        if not content:
            article = soup.find('article')
            if article:
                content = article.get_text().strip()[:500]
                
        result["title"] = title
        result["description"] = description
        result["content"] = content
        result["success"] = True
        
    except requests.exceptions.Timeout:
        result["error"] = "Waktu koneksi habis (Timeout)"
    except requests.exceptions.RequestException as e:
        result["error"] = f"Gagal memuat halaman: {str(e)}"
    except Exception as e:
        result["error"] = f"Kesalahan tidak dikenal saat scraping: {str(e)}"
        
    return result
