import os
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# إعدادات البوت
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# القائمة الرئيسية
def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("📚 الدروس", callback_data="lessons"),
            InlineKeyboardButton("✏️ التمارين", callback_data="exercises")
        ],
        [
            InlineKeyboardButton("🧠 اختبر مستواك", callback_data="quiz"),
            InlineKeyboardButton("🎯 تحدي السرعة", callback_data="challenge")
        ],
        [
            InlineKeyboardButton("👤 ملفي الشخصي", callback_data="profile"),
            InlineKeyboardButton("📊 تقدمي", callback_data="progress")
        ],
        [
            InlineKeyboardButton("🏆 الترتيب", callback_data="ranking"),
            InlineKeyboardButton("ℹ️ المساعدة", callback_data="help")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


# أمر البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    welcome = (
        f"🎓 أهلاً {user.first_name} في MINDEX Academy!\n\n"
        "🇩🇿 رحلتك نحو التفوق في بكالوريا 2027 تبدأ من هنا.\n\n"
        "📐 تعلّم، تدرّب، اختبر مستواك وطوّر مهاراتك.\n\n"
        "✨ من الصفر نحو التميز!\n\n"
        "اختَر من القائمة:"
    )

    await update.message.reply_text(
        welcome,
        reply_markup=main_menu()
    )


# التعامل مع الأزرار
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "lessons":
        text = (
            "📚 قسم الدروس\n\n"
            "الدروس المنظمة حسب برنامج الرياضيات لبكالوريا 2027.\n\n"
            "سيتم إضافة الدروس والتحقق من مطابقتها للبرنامج الرسمي."
        )

    elif data == "exercises":
        text = (
            "✏️ قسم التمارين\n\n"
            "تمارين متدرجة في الصعوبة، مع حلول مفصلة.\n\n"
            "قريباً!"
        )

    elif data == "quiz":
        text = (
            "🧠 اختبر مستواك\n\n"
            "اختبارات لتقييم مكتسباتك وتحديد نقاط القوة والضعف.\n\n"
            "قريباً!"
        )

    elif data == "challenge":
        text = (
            "🎯 تحدي السرعة\n\n"
            "تحديات رياضية بوقت محدد لقياس سرعة ودقة الإجابة.\n\n"
            "قريباً!"
        )

    elif data == "profile":
        user = query.from_user
        text = (
            "👤 ملفك الشخصي\n\n"
            f"الاسم: {user.first_name}\n"
            f"Telegram ID: {user.id}\n\n"
            "سيتم إضافة معلومات التسجيل والشعبة والولاية لاحقاً."
        )

    elif data == "progress":
        text = (
            "📊 تقدمي الدراسي\n\n"
            "هنا ستظهر نتائجك، نقاطك، "
            "ومستوى تقدمك في الرياضيات."
        )

    elif data == "ranking":
        text = (
            "🏆 الترتيب الوطني\n\n"
            "ترتيب التلاميذ حسب النقاط والإنجازات.\n\n"
            "سيتم تفعيله بعد إنشاء نظام الحسابات."
        )

    elif data == "help":
        text = (
            "ℹ️ المساعدة\n\n"
            "/start - تشغيل البوت\n"
            "/help - المساعدة\n\n"
            "MINDEX Academy | BAC 2027 🎓"
        )

    else:
        text = "اختيار غير معروف."

    keyboard = [
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="home")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# العودة إلى القائمة الرئيسية
async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🎓 MINDEX Academy | BAC 2027\n\nاختَر القسم الذي تريده:",
        reply_markup=main_menu()
    )


# المساعدة
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك في MINDEX Academy! 🎓\n\n"
        "استعمل /start لفتح القائمة الرئيسية."
    )


# تشغيل البوت
def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is missing!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(home, pattern="^home$"))
    app.add_handler(CallbackQueryHandler(buttons))

    print("MINDEX Academy is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
