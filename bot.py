
import os
import logging
import asyncio

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# -------------------------
# Logging
# -------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Hide Telegram API URLs and tokens from logs
logging.getLogger("httpx").setLevel(logging.WARNING)

# -------------------------
# Environment variables
# -------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "10000"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

if not WEBHOOK_URL:
    raise RuntimeError("WEBHOOK_URL is missing")

WEBHOOK_URL = WEBHOOK_URL.rstrip("/")

# -------------------------
# Main menu
# -------------------------

MENU = [
    ["📚 الدروس", "✏️ التمارين"],
    ["🧠 اختبر مستواك", "👤 ملفي الشخصي"],
    ["📊 تقدمي الدراسي", "🏆 الترتيب"],
    ["ℹ️ المساعدة"],
]

KEYBOARD = ReplyKeyboardMarkup(
    MENU,
    resize_keyboard=True
)

# -------------------------
# Commands
# -------------------------

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "مرحباً بك في MINDEX Academy 🎓\n\n"
        "رحلتك نحو التفوق في بكالوريا 2027 تبدأ هنا!\n\n"
        "اختاري الخدمة من القائمة:",
        reply_markup=KEYBOARD
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "📌 أوامر البوت:\n\n"
        "/start - تشغيل البوت\n"
        "/help - المساعدة\n"
        "/profile - ملفي الشخصي\n"
        "/lessons - الدروس\n"
        "/exercises - التمارين\n"
        "/quiz - اختبر مستواك\n"
        "/progress - تقدمي الدراسي\n"
        "/ranking - الترتيب"
    )


async def profile(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "👤 ملفك الشخصي\n\n"
        "سيتم تفعيل التسجيل والملف الشخصي قريباً."
    )


async def lessons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "📚 فضاء الدروس\n\n"
        "سيتم إضافة دروس الرياضيات حسب شعبتك."
    )


async def exercises(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "✏️ فضاء التمارين\n\n"
        "سيتم إضافة تمارين متدرجة مع الحلول."
    )


async def quiz(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🧠 اختبر مستواك\n\n"
        "اختبارات تحديد المستوى ستكون متاحة قريباً."
    )


async def progress(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "📊 تقدمك الدراسي\n\n"
        "سيظهر تقدمك ونقاطك هنا بعد تفعيل نظام الحسابات."
    )


async def ranking(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🏆 الترتيب\n\n"
        "سيتم تفعيل الترتيب الوطني وترتيب الولايات قريباً."
    )


# -------------------------
# Menu buttons
# -------------------------

async def menu_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text

    actions = {
        "📚 الدروس": lessons,
        "✏️ التمارين": exercises,
        "🧠 اختبر مستواك": quiz,
        "👤 ملفي الشخصي": profile,
        "📊 تقدمي الدراسي": progress,
        "🏆 الترتيب": ranking,
        "ℹ️ المساعدة": help_command,
    }

    action = actions.get(text)

    if action:
        await action(update, context)
    else:
        await update.message.reply_text(
            "اختاري خدمة من القائمة من فضلك 👇",
            reply_markup=KEYBOARD
        )


# -------------------------
# Start bot
# -------------------------

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("lessons", lessons))
    app.add_handler(CommandHandler("exercises", exercises))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CommandHandler("ranking", ranking))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            menu_handler
        )
    )

    # Python event loop setup
    asyncio.set_event_loop(asyncio.new_event_loop())

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="telegram",
        webhook_url=f"{WEBHOOK_URL}/telegram",
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
