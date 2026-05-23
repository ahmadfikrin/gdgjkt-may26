import os
import json
import datetime
import requests
from bs4 import BeautifulSoup

KB_CACHE_FILE = "knowledge_base.json"

# Daftar data fakta & hoax bawaan (sebagai basis pengetahuan cadangan & inisialisasi awal)
DEFAULT_KNOWLEDGE_BASE = [
    {
        "id": 1,
        "title": "Jakarta Libur Nasional karena Pemilu Susulan 24 Mei 2026",
        "claim": "Besok tanggal 24 Mei 2026 Jakarta akan libur nasional karena diadakannya pemilu susulan pilkada.",
        "status": "🛑 HOAX",
        "confidence": 98,
        "explanation": "Kementerian Ketenagakerjaan menyatakan tidak ada keputusan presiden mengenai libur nasional pada tanggal 24 Mei 2026. Pemilu susulan hanya diadakan di TPS tertentu dan tidak meliburkan provinsi Jakarta secara keseluruhan.",
        "source": "https://www.komdigi.go.id/berita/berita-hoaks",
        "category": "Pemerintahan"
    },
    {
        "id": 2,
        "title": "Bantuan Sosial Tunai 10 Juta Rupiah melalui Link Telegram",
        "claim": "Pemerintah membagikan bantuan sosial tunai sebesar 10 juta rupiah bagi yang bergabung ke grup Telegram ini.",
        "status": "🛑 HOAX",
        "confidence": 95,
        "explanation": "Kementerian Sosial menegaskan bahwa penyaluran BST hanya dilakukan melalui PT Pos Indonesia dan Himbara. Tidak ada pendaftaran bansos melalui link grup Telegram atau WhatsApp informal.",
        "source": "https://www.komdigi.go.id/berita/berita-hoaks",
        "category": "Sosial & Ekonomi"
    },
    {
        "id": 3,
        "title": "Vaksin Booster Mengandung Chip Magnetik Pelacak",
        "claim": "Vaksin booster mengandung chip magnetik kecil untuk melacak pergerakan warga.",
        "status": "🛑 HOAX",
        "confidence": 99,
        "explanation": "Kementerian Kesehatan dan WHO menegaskan kandungan vaksin sepenuhnya berisi bahan aktif antigen dan bahan penstabil standar medis. Logam magnetik atau mikrochip pelacak tidak mungkin dimasukkan ke dalam jarum suntik vaksin.",
        "source": "https://turnbackhoax.id/",
        "category": "Kesehatan"
    },
    {
        "id": 4,
        "title": "Gempa Megathrust Guncang Selat Sunda Malam Ini Kekuatan 9.5 SR",
        "claim": "Akan terjadi gempa bumi dahsyat megathrust di Selat Sunda berkekuatan 9.5 SR pada malam ini pukul 22.00 WIB.",
        "status": "🛑 HOAX",
        "confidence": 97,
        "explanation": "BMKG menegaskan gempa bumi tidak dapat diprediksi secara tepat kapan waktu terjadinya. Prediksi waktu spesifik jam dan kekuatan gempa megathrust malam ini adalah hoaks dan disinformasi.",
        "source": "https://turnbackhoax.id/",
        "category": "Bencana Alam"
    },
    {
        "id": 5,
        "title": "Pendaftaran KIP Kuliah Tahun 2026 Resmi Dibuka Kemendikbudristek",
        "claim": "Pendaftaran Kartu Indonesia Pintar Kuliah (KIP-Kuliah) tahun 2026 resmi dibuka mulai hari ini.",
        "status": "✅ FAKTA",
        "confidence": 95,
        "explanation": "Kementerian Pendidikan, Kebudayaan, Riset, dan Teknologi mengumumkan secara resmi pembukaan KIP Kuliah bagi lulusan SMA/SMK sederajat berprestasi dari keluarga kurang mampu melalui portal kip-kuliah.kemdikbud.go.id.",
        "source": "https://tirto.id/",
        "category": "Pendidikan"
    },
    {
        "id": 6,
        "title": "Pendaftaran Beasiswa LPDP Tahap 1 Tahun 2026 Dibuka",
        "claim": "Kementerian Keuangan resmi membuka pendaftaran beasiswa LPDP Tahap 1 tahun 2026 mulai kuartal pertama.",
        "status": "✅ FAKTA",
        "confidence": 96,
        "explanation": "Lembaga Pengelola Dana Pendidikan (LPDP) resmi membuka seleksi pendaftaran program beasiswa Magister dan Doktor Tahap 1 tahun 2026 secara daring bagi seluruh warga negara Indonesia.",
        "source": "https://tirto.id/",
        "category": "Pendidikan"
    }
]

def load_local_kb() -> list[dict]:
    """
    Memuat basis pengetahuan dari cache file JSON lokal.
    Jika belum ada, buat file baru menggunakan data default.
    """
    if os.path.exists(KB_CACHE_FILE):
        try:
            with open(KB_CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and "issues" in data:
                    return data["issues"]
                elif isinstance(data, list):
                    return data
        except Exception as e:
            print(f"[KB Error] Gagal membaca cache KB lokal: {e}")
            
    # Tulis data default jika tidak ada cache yang valid
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
    Mengambil data secara dinamis dari issue repositori GitHub (Issue #2).
    Kita menggunakan parsing halaman HTML publik untuk bypass limit API Github.
    """
    status = {
        "success": False,
        "synced_items": 0,
        "message": ""
    }
    
    url = "https://github.com/anti-fitnah/gdgjkt-may26/issues/2"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ambil deskripsi isu dan komentar
        # Cari semua komentar di timeline GitHub
        comment_elements = soup.find_all('div', class_='edit-comment-header')
        comments = []
        
        # Ekstraksi tautan/text dari komentar
        body_elements = soup.find_all('td', class_='comment-body')
        for body in body_elements:
            text = body.get_text().strip()
            if text:
                comments.append(text)
                
        # Jika berhasil mengekstrak tautan rujukan dari Issue #2 (seperti kominfo, tirto)
        if comments:
            current_kb = load_local_kb()
            updated_count = 0
            
            # Kita bisa memetakan komentar ke basis data kita
            # Komentar 1: https://www.komdigi.go.id/berita/berita-hoaks
            # Komentar 2: https://tirto.id/
            # Kita tambahkan referensi dinamis ini ke entri yang relevan
            for comment in comments:
                # Cek jika komentar berisi URL dan belum terdaftar di KB
                if comment.startswith("http") and not any(issue["source"] == comment for issue in current_kb):
                    # Buat entri dinamis baru berbasis URL
                    domain = comment.split('/')[2] if len(comment.split('/')) > 2 else comment
                    new_item = {
                        "id": len(current_kb) + 1,
                        "title": f"Rujukan Terpercaya dari {domain}",
                        "claim": f"Informasi resmi atau klarifikasi fakta dari situs {comment}",
                        "status": "✅ FAKTA" if "tirto" in comment else "🛑 HOAX",
                        "confidence": 90,
                        "explanation": f"Layanan verifikasi fakta resmi yang terhubung ke situs rujukan utama {comment}.",
                        "source": comment,
                        "category": "Rujukan Resmi"
                    }
                    current_kb.append(new_item)
                    updated_count += 1
            
            if updated_count > 0:
                save_local_kb(current_kb)
                status["synced_items"] = updated_count
                status["message"] = f"Berhasil sinkronisasi {updated_count} rujukan baru dari GitHub Issue #2."
            else:
                status["message"] = "Sinkronisasi selesai. Tidak ada rujukan baru di GitHub Issue #2."
                
            status["success"] = True
        else:
            status["message"] = "GitHub Issue #2 berhasil dibaca, namun tidak ditemukan teks komentar baru. Menggunakan basis data lokal."
            status["success"] = True
            
    except Exception as e:
        status["message"] = f"Gagal terkoneksi ke GitHub: {str(e)}. Menggunakan database lokal."
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
