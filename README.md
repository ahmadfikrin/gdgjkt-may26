# Anti Fitnah · Fact-Checking Engine & Dashboard (Peran 2)

Selamat datang di repositori **Anti Fitnah Fact-Checking Engine**! Proyek ini dirancang sebagai "otak" pintar dari Bot Telegram Anti Fitnah untuk memverifikasi kebenaran klaim, isu, atau berita secara instan di Indonesia dengan integrasi data basis pengetahuan dinamis dari GitHub dan mesin pencari cadangan (*fallback*).

Repositori ini berisi implementasi lengkap untuk **Peran 2 (Fact-Checking Engine & Data Integration Lead)** beserta **Testing Web Playground Dashboard** yang premium dengan visualisasi interaktif.

---

## 🚀 Fitur Utama (Peran 2)

1. **Penerimaan Input Multi-Format (Input Handling)**:
   * **Pembersihan Teks & Normalisasi**: Menghapus tanda baca, konversi huruf kecil, dan menyaring *stop-words* Bahasa Indonesia untuk mendeteksi esensi utama klaim.
   * **Real-time Web Scraping**: Pustaka crawler otomatis untuk mengekstrak judul halaman, meta deskripsi, dan paragraf pertama artikel berita dari tautan URL.
   * **OCR (Optical Character Recognition)**: Integrasi dengan engine OCR (Tesseract) untuk membaca screenshot gambar, lengkap dengan hint cadangan pintar untuk kelancaran pengujian lokal.

2. **Integrasi Basis Pengetahuan GitHub (Primary Knowledge Base)**:
   * Mengambil data hoax dan fakta secara dinamis dari komentar repositori `https://github.com/anti-fitnah/gdgjkt-may26/issues/6` via API/Web Parser.
   * Caching lokal cerdas dalam file `knowledge_base.json` untuk meningkatkan kecepatan respons di bawah 1 detik dan menghindari limitasi rate limit API GitHub.

3. **Mesin Kemiripan Teks (Text Similarity Matcher)**:
   * Menggunakan algoritma gabungan kemiripan Jaccard (set kata kunci unik) dan Sequence Matcher (kesamaan susunan klaim) untuk menghitung skor kecocokan persentase.

4. **Mesin Cadangan Cerdas (Fallback Search Engine)**:
   * Berjalan otomatis jika kemiripan dengan basis pengetahuan GitHub di bawah 55%.
   * Melakukan pencarian sekunder di situs-situs terpercaya yang terverifikasi (Kominfo, TurnBackHoax, Tirto.id) untuk mengembalikan status kesimpulan.

5. **Penilaian Skor Keyakinan & Format Hasil (Scoring Mechanism)**:
   * Menghasilkan status kesimpulan: `[ 🛑 HOAX ]`, `[ ✅ FAKTA ]`, atau `[ ⚠️ SEBAGIAN BENAR / BELUM DAPAT DIPASTIKAN ]` beserta persentase keyakinan akurasi, rujukan link resmi, dan ringkasan bantahan yang terstruktur.

---

## 🛠️ Persyaratan Sistem

Pastikan Anda memiliki:
* **Python 3.10 ke atas** (Proyek dikembangkan menggunakan Python 3.13.13)
* *Tesseract OCR* (Opsional, modul Python tetap berjalan dengan simulasi teks cerdas jika tidak terinstall)

---

## 📦 Cara Memulai & Instalasi

1. **Kloning Repositori**:
   ```bash
   git clone https://github.com/anti-fitnah/gdgjkt-may26.git
   cd gdgjkt-may26
   ```

2. **Install Dependensi Python**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan Server Lokal**:
   ```bash
   python -m uvicorn app:app --reload
   ```

4. **Buka Web Playground**:
   Buka peramban (browser) Anda dan akses alamat:
   ```
   http://127.0.0.1:8000/
   ```

---

## 🗺️ Struktur Proyek

```
/
├── engine/                  # Paket Inti Fact-Checking
│   ├── __init__.py          # API Ekspos Utama
│   ├── preprocess.py        # Pembersihan Teks & Stop-Words
│   ├── ocr.py               # Pemindaian Teks Gambar (OCR)
│   ├── scraper.py           # Web Scraper Tautan & Berita
│   ├── github_kb.py         # Integrasi API GitHub & Local Cache
│   ├── matcher.py           # Kalkulasi Kemiripan Teks
│   ├── fallback.py          # Pencarian Cadangan Luar
│   └── scorer.py            # Penentu Skor Akurasi Akhir
│
├── static/                  # File Statis Dashboard
│   ├── css/style.css        # Desain Glassmorphism Gelap Premium
│   └── js/main.js           # AJAX Request & Animasi Gauge Interaktif
│
├── templates/               # Templating HTML
│   └── index.html           # Layout Web Dashboard Utama
│
├── app.py                   # Server Utama FastAPI (Endpoint REST API)
├── requirements.txt         # Daftar Library Pendukung
└── README.md                # Dokumentasi Proyek
```

---

## 🔗 Dokumentasi REST API

### 1. Verifikasi Klaim Teks langsung
* **Endpoint**: `POST /api/verify/text`
* **Body Request**:
  ```json
  {
    "text": "Apakah besok Jakarta libur nasional pemilu?"
  }
  ```

### 2. Verifikasi Konten Tautan URL
* **Endpoint**: `POST /api/verify/url`
* **Body Request**:
  ```json
  {
    "url": "https://www.komdigi.go.id/berita/berita-hoaks"
  }
  ```

### 3. Verifikasi Screenshot Gambar (OCR)
* **Endpoint**: `POST /api/verify/image`
* **Body Request** (Multipart Form-Data):
  * `file`: File gambar (screenshot)
  * `extracted_text_hint` (Opsional): Hint teks manual jika Tesseract OCR lokal tidak aktif.

### 4. Sinkronisasi Data GitHub
* **Endpoint**: `POST /api/kb/sync`
* **Kegunaan**: Menarik data terbaru dari GitHub Issue #2 secara dinamis dan memperbarui cache basis pengetahuan lokal.
