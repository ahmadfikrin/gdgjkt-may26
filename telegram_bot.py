import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import engine

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def format_result(result: dict) -> str:
    """Formats the verification result into a readable Telegram message."""
    status = result.get("status", "TIDAK DIKETAHUI")
    if status == "HOAX":
        status_text = "🛑 HOAX"
    elif status == "FAKTA":
        status_text = "✅ FAKTA"
    else:
        status_text = "⚠️ SEBAGIAN BENAR / BELUM DAPAT DIPASTIKAN"

    score = result.get("confidence", 0)
    explanation = result.get("explanation", "Tidak ada penjelasan.")
    source = result.get("source", "Tidak diketahui")
    
    # Optional fields from scraping/ocr
    extracted = result.get("extracted_text")
    scraped = result.get("scraped_data")

    msg = f"**{status_text}** (Keyakinan: {score}%)\n\n"
    msg += f"**Penjelasan:**\n{explanation}\n\n"
    msg += f"**Sumber:** {source}\n"
    
    if extracted:
        msg += f"\n_Teks terdeteksi dari gambar:_\n`{extracted[:200]}...`\n"
        
    if scraped:
        title = scraped.get("title", "")
        msg += f"\n_Artikel terkait: {title}_\n"

    return msg

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_message = (
        f"Halo {user.first_name}! Saya adalah **Anti Fitnah Bot**.\n\n"
        "Kirimkan saya pesan teks, tautan berita, atau gambar screenshot yang berisi klaim atau isu, "
        "dan saya akan membantu Anda memverifikasi apakah informasi tersebut Fakta atau Hoax."
    )
    await update.message.reply_markdown(welcome_message)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages including URLs."""
    text = update.message.text
    
    # Send processing message
    processing_msg = await update.message.reply_text("⏳ Sedang memverifikasi data, mohon tunggu sebentar...")
    
    try:
        # Check if text contains a URL (simple check)
        # For simplicity, if it starts with http, treat as URL
        if text.startswith("http://") or text.startswith("https://"):
            scrape_res = engine.scrape_url_content(text)
            if not scrape_res["success"]:
                await processing_msg.edit_text(f"Gagal memproses tautan: {scrape_res.get('error')}")
                return
            query_analysis = f"{scrape_res['title']}. {scrape_res['content']}"
            kb_issues = engine.load_local_kb()
            result = engine.evaluate_fact_checking(query_analysis, kb_issues)
            result["scraped_data"] = {
                "title": scrape_res["title"],
                "snippet": scrape_res["content"][:100]
            }
        else:
            # Normal text verification
            kb_issues = engine.load_local_kb()
            result = engine.evaluate_fact_checking(text, kb_issues)
            
        reply_text = format_result(result)
        await processing_msg.edit_text(reply_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        await processing_msg.edit_text("Terjadi kesalahan saat memproses permintaan Anda.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo uploads for OCR."""
    processing_msg = await update.message.reply_text("⏳ Sedang mengunduh dan membaca gambar, mohon tunggu sebentar...")
    
    try:
        # Get highest resolution photo
        photo_file = await update.message.photo[-1].get_file()
        
        os.makedirs("temp", exist_ok=True)
        file_path = f"temp/{photo_file.file_id}.jpg"
        
        # Download the file
        await photo_file.download_to_drive(custom_path=file_path)
        
        # Extract text via OCR
        # We can pass caption as hint if available
        caption = update.message.caption
        extracted_text = engine.extract_text_from_image(file_path, hint_text=caption)
        
        if not extracted_text.strip():
            await processing_msg.edit_text("Gagal membaca teks dari gambar. Pastikan gambar cukup jelas.")
            return
            
        # Verify extracted text
        kb_issues = engine.load_local_kb()
        result = engine.evaluate_fact_checking(extracted_text, kb_issues)
        result["extracted_text"] = extracted_text
        
        reply_text = format_result(result)
        await processing_msg.edit_text(reply_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await processing_msg.edit_text("Terjadi kesalahan saat memproses gambar.")
    finally:
        # Cleanup
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set in .env")
        return

    # Sync KB on startup
    logger.info("Syncing KB from GitHub...")
    try:
        engine.sync_kb_from_github()
    except Exception as e:
        logger.error(f"Failed to sync KB on startup: {e}")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
