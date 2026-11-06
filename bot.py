import os
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"].rstrip("/")
PORT = int(os.environ.get("PORT", 10000))

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("📚 الدروس", callback_data="lessons"),
            InlineKeyboardButton("✏️ التمارين", callback_data="exercises")
        ],
        [
            InlineKeyboardButton("🧠 اختبر مستواك", callback_data="quiz"),
            InlineKeyboardButton("🎯 التحدي اليومي", callback_data="challenge")
        ],
        [
            InlineKeyboardButton("🤖 اسأل MINDEX AI", callback_data="ai"),
            InlineKeyboardButton("👤 ملفي الشخصي", callback_data="profile")
        ],
        [
            InlineKeyboardButton("📊 تقدمي", callback_data="progress"),
            InlineKeyboardButton("🏆 الترتيب", callback_data="ranking")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.message.reply_text(
        f"🎓 أهلاً {user.first_name} في MINDEX Academy!\n\n"
        "🇩🇿 رحلتك نحو بكالوريا 2027 تبدأ هنا.\n\n"
        "📐 تعلّم، تدرّب، اختبر مستواك وطوّر مهاراتك.\n\n"
        "✨ من الصفر نحو التميز!",
        reply_markup=main_menu()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎓 مرحباً بك في MINDEX Academy!\n"
        "استعمل /start لفتح القائمة الرئيسية."
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    sections = {
        "lessons": "📚 قسم الدروس\n\nالدروس حسب البرنامج الوزاري المعتمد.",
        "exercises": "✏️ قسم التمارين\n\nتمارين متدرجة مع حلول مفصلة.",
        "quiz": "🧠 اختبر مستواك\n\nاختبارات لتقييم مكتسباتك.",
        "challenge": "🎯 التحدي اليومي\n\nتحدٍّ جديد كل يوم.",
        "ai": "🤖 MINDEX AI\n\nاطرح أسئلتك حول الرياضيات وطرق الدراسة والتحضير للبكالوريا.",
        "profile": "👤 ملفك الشخصي\n\nسيتم إضافة بيانات التسجيل لاحقاً.",
        "progress": "📊 تقدمي\n\nستظهر هنا نتائجك ونقاط تقدمك.",
        "ranking": "🏆 الترتيب\n\nالترتيب الوطني وترتيب الولاية."
    }

    if query.data == "home":
        await query.edit_message_text(
            "🎓 MINDEX Academy | BAC 2027\n\nاختَر القسم:",
            reply_markup=main_menu()
        )
        return

    text = sections.get(query.data, "اختيار غير معروف.")

    keyboard = [[
        InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="home")
    ]]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(buttons))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="telegram",
        webhook_url=f"{WEBHOOK_URL}/telegram"
    )


if __name__ == "__main__":
    main()
