import os
import subprocess
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== KONFIGURASI =====
TOKEN = os.getenv("TELEGRAM_TOKEN")
BOOSTER_PATH = os.getenv("BOOSTER_PATH", ".")  # Path ke folder Tiktok-Booster

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== FUNGSI MENU =====
def get_main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🚀 Boost Views", callback_data="boost"),
            InlineKeyboardButton("📊 Status", callback_data="status"),
        ],
        [
            InlineKeyboardButton("⏹️ Stop Proses", callback_data="stop"),
            InlineKeyboardButton("❓ Bantuan", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== HANDLER COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 **TikTok View Booster Bot**\n\n"
        "Saya bisa membantu meningkatkan views video TikTok-mu.\n\n"
        "📌 **Cara Pakai:**\n"
        "1. Kirim link video TikTok\n"
        "2. Pilih menu Boost Views\n"
        "3. Tunggu proses selesai\n\n"
        "⚠️ **Catatan:** Hanya untuk edukasi!",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

async def boost_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Sertakan URL TikTok!\n\n"
            "Contoh: `/boost https://www.tiktok.com/@user/video/12345`",
            parse_mode="Markdown"
        )
        return
    
    url = context.args[0]
    chat_id = update.effective_chat.id
    
    await update.message.reply_text(f"⏳ **Memproses boost untuk:**\n`{url}`\n\nIni akan memakan waktu 2-5 menit...", parse_mode="Markdown")
    
    try:
        # Jalankan main.py sebagai subproses
        process = subprocess.Popen(
            ["python3", "main.py", url],
            cwd=BOOSTER_PATH,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=600)  # 10 menit timeout
        
        if process.returncode == 0:
            await update.message.reply_text(
                f"✅ **Proses selesai!**\n\n"
                f"📊 **Hasil:**\n{stdout[:1000] if stdout else 'Views bertambah!'}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"❌ **Error:**\n```\n{stderr[:500]}\n```",
                parse_mode="Markdown"
            )
    except subprocess.TimeoutExpired:
        process.kill()
        await update.message.reply_text("⏰ **Timeout!** Proses memakan waktu terlalu lama (lebih dari 10 menit).")
    except Exception as e:
        await update.message.reply_text(f"❌ **Gagal menjalankan:**\n`{str(e)}`", parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ **Bantuan**\n\n"
        "📌 **Perintah:**\n"
        "/start - Tampilkan menu utama\n"
        "/boost <url> - Boost views untuk video TikTok\n"
        "/status - Cek status proses\n"
        "/stop - Hentikan proses\n"
        "/help - Tampilkan bantuan\n\n"
        "⚠️ **Catatan:** Gunakan dengan bijak!"
    )

# ===== HANDLER CALLBACK =====
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "boost":
        await query.edit_message_text(
            "📤 **Kirim link video TikTok:**\n\n"
            "Contoh: `https://www.tiktok.com/@user/video/12345`\n\n"
            "Atau gunakan perintah: `/boost <url>`",
            parse_mode="Markdown"
        )
    elif data == "status":
        await query.edit_message_text(
            "📊 **Status Proses**\n\n"
            "Saat ini tidak ada proses berjalan.\n"
            "Gunakan /boost untuk memulai."
        )
    elif data == "stop":
        await query.edit_message_text(
            "⏹️ **Proses dihentikan** (jika ada).\n"
            "Untuk memulai ulang, gunakan /boost."
        )
    elif data == "help":
        await query.edit_message_text(
            "❓ **Bantuan**\n\n"
            "1. Kirim link video TikTok\n"
            "2. Pilih Boost Views\n"
            "3. Tunggu 2-5 menit\n"
            "4. Lihat hasilnya!"
        )

# ===== MAIN =====
def main():
    if not TOKEN:
        logger.error("❌ TELEGRAM_TOKEN tidak ditemukan!")
        return
    
    app = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("boost", boost_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("🤖 TikTok Booster Bot berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
