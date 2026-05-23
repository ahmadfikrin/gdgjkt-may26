import os
import json
import datetime
import requests
from bs4 import BeautifulSoup

KB_CACHE_FILE = "knowledge_base.json"

# Daftar data fakta & hoax bawaan dari Issue #6 (sebagai basis pengetahuan cadangan & inisialisasi awal)
DEFAULT_KNOWLEDGE_BASE = [
    {
        "id": 1,
        "title": "[HOAKS] Komdigi Akan Nonaktifkan Media Sosial pada 28 Maret 2026",
        "claim": "Beredar unggahan di media sosial yang mengklaim bahwa pada **28 Maret 2026**, pemerintah melalui Kementerian Komunikasi dan Digital (Komdigi) akan **menonaktifkan seluruh platform media sosial** seperti TikTok, Instagram, Facebook, dan YouTube sehingga masyarakat tidak dapat mengaksesnya.",
        "status": "🛑 HOAX",
        "confidence": 95,
        "explanation": "Klaim tersebut **tidak benar**. Kebijakan yang berlaku mulai 28 Maret 2026 adalah implementasi **PP TUNAS (PP Nomor 17 Tahun 2025)** tentang Tata Kelola Penyelenggaraan Sistem Elektronik dalam Perlindungan Anak, yang diatur lebih lanjut dalam **Peraturan Menteri Komdigi Nomor 9 Tahun 2026**.\n\nKebijakan tersebut **hanya menonaktifkan akun pengguna berusia di bawah 16 tahun** pada platform digital berisiko tinggi — bukan menutup atau mematikan platform media sosial secara keseluruhan.",
        "source": "https://pusiknas.polri.go.id/detail_artikel/komdigi_disebut_akan_nonaktifkan_media_sosial,_polri:_hoaks",
        "category": "Kebijakan Pemerintah"
    },
    {
        "id": 2,
        "title": "[HOAKS] Tautan Pendaftaran CPNS 2026 Resmi Dibuka",
        "claim": "Beredar postingan di media sosial (Facebook, TikTok) yang mengklaim terdapat **tautan resmi pendaftaran CPNS 2026** dengan narasi seperti:\n\n*\"RESMI DIBUKA PENDAFTARAN CPNS, LULUSAN SMA D3 S1 PENEMPATAN DI SELURUH WILAYAH INDONESIA\"*\n\nTautan tersebut mengarah ke formulir digital yang meminta data pribadi seperti **nama sesuai KTP, nomor telepon, hingga nomor Telegram**.",
        "status": "🛑 HOAX",
        "confidence": 98,
        "explanation": "Klaim ini **tidak benar dan berpotensi penipuan (phishing)**. Hingga saat ini pemerintah **belum mengeluarkan pengumuman resmi** terkait seleksi CPNS 2026.\n\nPendaftaran CPNS **hanya dilakukan melalui portal resmi**:\n- **SSCASN BKN**: [https://sscasn.bkn.go.id/](https://sscasn.bkn.go.id)\n\nTautan yang beredar di media sosial bertujuan **mencuri data pribadi** pengguna. Masyarakat diminta tidak mengklik atau mengisi formulir dari sumber tidak resmi.",
        "source": "https://www.liputan6.com/cek-fakta/read/6278160/deretan-hoaks-cpns-2026-yang-beredar-di-media-sosial-simak-faktanya",
        "category": "Penipuan Digital / Phishing"
    },
    {
        "id": 3,
        "title": "[SEBAGIAN BENAR] Tahun 2026 Rakyat Indonesia Akan Kehilangan Tanah Akibat Aturan Baru Pemerintah",
        "claim": "Beredar narasi di media sosial yang mengklaim bahwa **aturan baru pemerintah pada 2026 akan menyebabkan rakyat Indonesia kehilangan tanah mereka**, seolah pemerintah dapat mengambil alih tanah milik rakyat secara sepihak.",
        "status": "⚠️ SEBAGIAN BENAR / BELUM DAPAT DIPASTIKAN",
        "confidence": 80,
        "explanation": "Narasi ini **mendistorsi fakta**. Benar bahwa terdapat kebijakan baru terkait pertanahan pada 2026, namun klaim bahwa \"rakyat akan kehilangan tanah\" adalah **framing yang menyesatkan**.\n\n**Fakta yang benar:**\n- Pemerintah memang mengeluarkan kebijakan terkait **digitalisasi sertifikat tanah** dan pembaruan sistem agraria.\n- Kebijakan tersebut **tidak mengizinkan pengambilalihan tanah rakyat secara sepihak**.\n- Tanah yang berpotensi terdampak hanya tanah **tanpa sertifikat resmi atau dalam sengketa hukum** yang sudah berjalan lama.\n\n**Yang menyebabkan miskonsepsi:**\n- Narasi di media sosial menghilangkan konteks hukum dan mencampur adukkan beberapa regulasi berbeda seolah menjadi satu ancaman tunggal.",
        "source": "https://www.komdigi.go.id/berita/berita-hoaks/detail/hoaks-tahun-2026-rakyat-indonesia-akan-kehilangan-tanah-akibat-aturan-baru-pemerintah",
        "category": "Kebijakan Pertanahan"
    },
    {
        "id": 4,
        "title": "[FAKTA] Akun Media Sosial Pengguna di Bawah 16 Tahun Dinonaktifkan Mulai 28 Maret 2026",
        "claim": "Beredar informasi bahwa mulai **28 Maret 2026**, pemerintah akan menonaktifkan akun media sosial pengguna berusia di bawah 16 tahun.",
        "status": "✅ FAKTA",
        "confidence": 97,
        "explanation": "Informasi ini **benar**. Kebijakan tersebut adalah bagian dari implementasi **PP TUNAS** (Peraturan Pemerintah Nomor 17 Tahun 2025 tentang Tata Kelola Penyelenggaraan Sistem Elektronik dalam Perlindungan Anak), yang diatur lebih lanjut oleh **Peraturan Menteri Komdigi Nomor 9 Tahun 2026**.\n\n**Detail kebijakan:**\n- Akun pengguna berusia **di bawah 16 tahun** pada platform digital berisiko tinggi akan dinonaktifkan.\n- Kebijakan ini berlaku mulai **28 Maret 2026**.\n- Tujuannya adalah menciptakan **ruang digital yang lebih aman bagi anak-anak**.\n- Platform media sosial secara keseluruhan **tidak dimatikan** — hanya akun pengguna di bawah umur.\n\n**Catatan penting:** Klaim ini sering **disalahpahami** sebagai \"seluruh media sosial dinonaktifkan\" — yang merupakan hoaks (lihat: hoaks-001).",
        "source": "https://klinikhoaks.jatimprov.go.id/post/media-sosial-akan-dinonaktifkan-komdigi-pada-28-maret-2026-69b4e7a129460",
        "category": "Kebijakan Perlindungan Anak Digital"
    }
]

def load_local_kb() -> list[dict]:
    """
    Memuat basis pengetahuan dari cache file JSON lokal.
    Jika belum ada, coba lakukan sinkronisasi dinamis langsung dari GitHub Issue #6 terlebih dahulu.
    Jika gagal, baru gunakan data bawaan sebagai cadangan.
    """
    if os.path.exists(KB_CACHE_FILE):
        try:
            with open(KB_CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and "issues" in data:
                    issues = data["issues"]
                    # Jika terdeteksi data bawaan yang tidak lengkap atau menggunakan format lama (seperti data libur pemilu 6 item),
                    # coba sinkronisasi ulang secara dinamis untuk menjamin kebaruan data.
                    if issues and any(issue.get("title") == "Jakarta Libur Nasional karena Pemilu Susulan 24 Mei 2026" for issue in issues):
                        print("[KB] Cache lokal berisi data statis lama. Mencoba sinkronisasi ulang dinamis...")
                        sync_res = sync_kb_from_github()
                        if sync_res.get("success"):
                            with open(KB_CACHE_FILE, 'r', encoding='utf-8') as f2:
                                data2 = json.load(f2)
                                return data2.get("issues", DEFAULT_KNOWLEDGE_BASE)
                    return issues
                elif isinstance(data, list):
                    return data
        except Exception as e:
            print(f"[KB Error] Gagal membaca cache KB lokal: {e}")
            
    # Jika cache file tidak ada, coba sinkronisasi secara dinamis langsung dari GitHub
    print("[KB] Cache lokal tidak ditemukan. Mencoba sinkronisasi dinamis dari GitHub Issue #6...")
    sync_res = sync_kb_from_github()
    if sync_res.get("success"):
        try:
            with open(KB_CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("issues", DEFAULT_KNOWLEDGE_BASE)
        except Exception:
            pass
            
    # Tulis data default jika tidak ada cache yang valid dan sinkronisasi gagal
    save_local_kb(DEFAULT_KNOWLEDGE_BASE)
    return DEFAULT_KNOWLEDGE_BASE

def save_local_kb(issues: list[dict]):
    """
    Menyimpan daftar data isu ke file JSON lokal beserta metadata sinkronisasi.
    """
    payload = {
        "last_sync": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_count": len(issues),
        "issues": issues
    }
    try:
        with open(KB_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[KB Error] Gagal menulis cache KB lokal: {e}")

def sync_kb_from_github() -> dict:
    """
    Mengambil data secara dinamis dari issue repositori GitHub (Issue #6).
    Mendukung penarikan melalui GitHub REST API sebagai metode utama (sangat andal dan rapi),
    serta Web Scraping HTML menggunakan BeautifulSoup sebagai metode cadangan jika API terkena rate limit.
    Mengekstrak komentar yang berisi struktur YAML frontmatter dan Markdown GFM.
    """
    import re
    status = {
        "success": False,
        "synced_items": 0,
        "message": ""
    }
    
    comments = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    # METODE 1: Menggunakan GitHub REST API (Sangat Handal, format terstruktur)
    api_url = "https://api.github.com/repos/anti-fitnah/gdgjkt-may26/issues/6/comments"
    try:
        print("[KB Sync] Mengakses GitHub REST API...")
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            res_json = response.json()
            for comment_data in res_json:
                body = comment_data.get("body", "")
                if body:
                    comments.append(body)
            print(f"[KB Sync] Berhasil mendapatkan {len(comments)} komentar via REST API.")
    except Exception as e:
        print(f"[KB Sync API Warning] Gagal menggunakan GitHub REST API: {e}")
        
    # METODE 2: Fallback ke HTML Scraping jika Metode REST API gagal atau tidak membuahkan hasil
    if not comments:
        url = "https://github.com/anti-fitnah/gdgjkt-may26/issues/6"
        try:
            print("[KB Sync] Melakukan HTML Scraping sebagai fallback...")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            script = soup.find('script', attrs={'data-target': 'react-app.embeddedData'})
            
            if not script:
                for s in soup.find_all('script'):
                    if s.string and "preloadedQueries" in s.string:
                        script = s
                        break
                        
            if script:
                data = json.loads(script.string)
                queries = data["payload"]["preloadedQueries"]
                for q in queries:
                    if "result" in q and "data" in q["result"] and q["result"]["data"]:
                        repo = q["result"]["data"].get("repository")
                        if repo and "issue" in repo and repo["issue"]:
                            edges = repo["issue"]["frontTimelineItems"]["edges"]
                            for edge in edges:
                                node = edge.get("node", {})
                                if node.get("__typename") == "IssueComment":
                                    body = node.get("body", "")
                                    if body:
                                        comments.append(body)
                print(f"[KB Sync] Berhasil mendapatkan {len(comments)} komentar via HTML Scraping.")
        except Exception as e:
            print(f"[KB Sync HTML Error] Gagal melakukan HTML Scraping: {e}")
            
    if not comments:
        status["message"] = "Gagal menyinkronkan data dari GitHub. (Kedua metode REST API & HTML Scraping tidak membuahkan hasil)"
        status["success"] = False
        return status
        
    parsed_entries = []
    for c in comments:
        if c.strip().startswith("---"):
            parts = c.split("---")
            if len(parts) >= 3:
                frontmatter_raw = parts[1]
                markdown_raw = parts[2]
                
                # Parse frontmatter
                fm = {}
                for line in frontmatter_raw.strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        fm[k.strip()] = v.strip()
                        
                # Parse tags
                tags_raw = fm.get("tags", "[]")
                tags = [t.strip().strip("'\"") for t in tags_raw.strip("[]").split(",")]
                
                # Cari tautan rujukan resmi
                urls = re.findall(r'https?://\S+', frontmatter_raw)
                source_url = urls[0] if urls else "https://github.com/anti-fitnah/gdgjkt-may26"
                
                # Ekstrak judul dari markdown heading #
                title_match = re.search(r'^#\s*(.*)$', markdown_raw.strip(), re.M)
                title = title_match.group(1).strip() if title_match else fm.get("id", "Klaim Terverifikasi")
                
                # Ekstrak klaim dari ## Klaim yang Beredar
                claim_match = re.search(r'## Klaim yang Beredar\s*\n\n?([\s\S]*?)(?=\n\n?##|$)', markdown_raw)
                claim = claim_match.group(1).strip() if claim_match else "Klaim dari media sosial."
                claim = re.sub(r'^>\s*', '', claim, flags=re.M).strip()
                
                # Ekstrak penjelasan dari ## Penjelasan
                exp_match = re.search(r'## Penjelasan\s*\n\n?([\s\S]*?)(?=\n\n?##|$)', markdown_raw)
                explanation = exp_match.group(1).strip() if exp_match else "Penjelasan resmi terverifikasi."
                explanation = re.sub(r'^>\s*', '', explanation, flags=re.M).strip()
                
                # Pemetaan Status
                status_raw = fm.get("status", "HOAX").upper()
                status_str = "🛑 HOAX"
                if "FAKTA" in status_raw:
                    status_str = "✅ FAKTA"
                elif "SEBAGIAN" in status_raw or "WARNING" in status_raw:
                    status_str = "⚠️ SEBAGIAN BENAR / BELUM DAPAT DIPASTIKAN"
                    
                confidence = int(fm.get("confidence", "95"))
                category = fm.get("kategori", "Umum").strip("'\"")
                
                parsed_entries.append({
                    "id": len(parsed_entries) + 1,
                    "title": title,
                    "claim": claim,
                    "status": status_str,
                    "confidence": confidence,
                    "explanation": explanation,
                    "source": source_url,
                    "category": category
                })
                
    if parsed_entries:
        # Berhasil melakukan parsing entries, simpan ke lokal cache
        save_local_kb(parsed_entries)
        status["success"] = True
        status["synced_items"] = len(parsed_entries)
        status["message"] = f"Berhasil menarik secara dinamis {len(parsed_entries)} data kasus dari komentar GitHub Issue #6!"
    else:
        status["message"] = "Berhasil memuat komentar, namun tidak dapat memparsing format komentar GFM Issue #6."
        status["success"] = False
        
    return status

def get_kb_metadata() -> dict:
    """
    Mengembalikan data statistik cache lokal KB saat ini.
    """
    if os.path.exists(KB_CACHE_FILE):
        try:
            with open(KB_CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    "last_sync": data.get("last_sync", "Belum pernah"),
                    "total_count": data.get("total_count", 0)
                }
        except Exception:
            pass
            
    # Inisialisasi awal jika belum ada file
    load_local_kb()
    return {
        "last_sync": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_count": len(DEFAULT_KNOWLEDGE_BASE)
    }
