import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import engine

app = FastAPI(
    title="Anti Fitnah Fact-Checking Engine",
    description="Backend API dan Dashboard Pengujian Mesin Pemeriksa Fakta Terintegrasi",
    version="1.0"
)

# Buat direktori temp untuk penyimpanan screenshot sementara dan static/templates jika belum ada
os.makedirs("temp", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount files statis (CSS/JS/Gambar)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Konfigurasi Templates Jinja2
templates = Jinja2Templates(directory="templates")


# --- Model Data Pydantic ---
class TextVerifyRequest(BaseModel):
    text: str

class UrlVerifyRequest(BaseModel):
    url: str


# --- Endpoints REST API ---

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """
    Menyajikan halaman utama web playground pengujian untuk pengguna.
    """
    kb_meta = engine.get_kb_metadata()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "last_sync": kb_meta["last_sync"],
            "total_count": kb_meta["total_count"]
        }
    )

@app.post("/api/verify/text")
async def verify_text(payload: TextVerifyRequest):
    """
    Endpoint untuk memverifikasi klaim teks langsung.
    """
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Teks kueri tidak boleh kosong")
        
    kb_issues = engine.load_local_kb()
    result = engine.evaluate_fact_checking(payload.text, kb_issues)
    return JSONResponse(content=result)

@app.post("/api/verify/url")
async def verify_url(payload: UrlVerifyRequest):
    """
    Endpoint untuk melakukan scraping pada URL dan memverifikasi isinya.
    """
    if not payload.url.strip():
        raise HTTPException(status_code=400, detail="URL tidak boleh kosong")
        
    # Lakukan scraping konten web
    scrape_res = engine.scrape_url_content(payload.url)
    if not scrape_res["success"]:
        return JSONResponse(status_code=400, content={
            "success": False,
            "error": scrape_res["error"]
        })
        
    # Gabungkan judul dan paragraf pertama untuk dianalisis
    query_analysis = f"{scrape_res['title']}. {scrape_res['content']}"
    
    kb_issues = engine.load_local_kb()
    result = engine.evaluate_fact_checking(query_analysis, kb_issues)
    
    # Tambahkan info tambahan scraping ke response
    result["scraped_data"] = {
        "title": scrape_res["title"],
        "description": scrape_res["description"],
        "snippet": scrape_res["content"][:200] + "..." if len(scrape_res["content"]) > 200 else scrape_res["content"]
    }
    
    return JSONResponse(content=result)

@app.post("/api/verify/image")
async def verify_image(
    file: UploadFile = File(...),
    extracted_text_hint: str = Form(None)
):
    """
    Endpoint untuk menerima unggahan gambar screenshot, menjalankan OCR,
    dan memverifikasi teks klaim hasil ekstraksi.
    """
    # Pastikan file adalah gambar
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar (PNG/JPG/JPEG)")
        
    # Simpan file sementara di folder temp/
    file_path = f"temp/{file.filename}"
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Ekstrak teks menggunakan modul OCR (mendukung hint_text cadangan)
        extracted_text = engine.extract_text_from_image(file_path, hint_text=extracted_text_hint)
        
        if not extracted_text.strip():
            return JSONResponse(status_code=422, content={
                "success": False,
                "error": "OCR gagal mendeteksi tulisan dalam gambar. Silakan masukkan hint teks secara manual."
            })
            
        # Verifikasi hasil OCR
        kb_issues = engine.load_local_kb()
        result = engine.evaluate_fact_checking(extracted_text, kb_issues)
        
        # Tambahkan metadata teks hasil ekstraksi
        result["extracted_text"] = extracted_text
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses gambar: {str(e)}")
    finally:
        # Bersihkan file sementara jika ada
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

@app.post("/api/kb/sync")
async def sync_knowledge_base():
    """
    Endpoint untuk menyinkronkan database lokal dengan GitHub Issue #2.
    """
    res = engine.sync_kb_from_github()
    kb_meta = engine.get_kb_metadata()
    res.update(kb_meta)
    return JSONResponse(content=res)

@app.get("/api/kb/status")
async def get_kb_status():
    """
    Endpoint untuk melihat metadata status basis pengetahuan saat ini.
    """
    kb_meta = engine.get_kb_metadata()
    # Muat semua isu untuk dikirim ke UI daftar
    issues = engine.load_local_kb()
    return JSONResponse(content={
        "last_sync": kb_meta["last_sync"],
        "total_count": kb_meta["total_count"],
        "issues": issues
    })
