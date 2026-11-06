
import os
import logging
import asyncio
import sqlite3
import random

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from content import LESSONS, DIFFICULTIES, CHALLENGE_TYPES


# =====================================
# CONFIGURATION
# =====================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logging.getLogger("httpx").setLevel(logging.WARNING)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").rstrip("/")
PORT = int(os.getenv("PORT", "10000"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

if not WEBHOOK_URL:
    raise RuntimeError("WEBHOOK_URL is missing")

DB_NAME = "mindex.db"


# =====================================
# DATABASE
# =====================================

def db():
    return sqlite3.connect(DB_NAME)


def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                branch TEXT DEFAULT '',
                wilaya TEXT DEFAULT '',
                xp INTEGER DEFAULT 0,
                quizzes INTEGER DEFAULT 0,
                correct INTEGER DEFAULT 0
            )
        """)


def register_student(user):
    with db() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO students
            (user_id, full_name)
            VALUES (?, ?)
        """, (user.id, user.full_name))


def get_student(user_id):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM students WHERE user_id = ?",
            (user_id,)
        ).fetchone()


def update_student(user_id, branch=None, wilaya=None):
    with db() as conn:
        if branch is not None:
            conn.execute(
                "UPDATE students SET branch = ? WHERE user_id = ?",
                (branch, user_id)
            )
        if wilaya is not None:
            conn.execute(
                "UPDATE students SET wilaya = ? WHERE user_id = ?",
                (wilaya, user_id)
            )


def add_score(user_id, points, correct=0):
    with db() as conn:
        conn.execute("""
            UPDATE students
            SET xp = xp + ?,
                quizzes = quizzes + 1,
                correct = correct + ?
            WHERE user_id = ?
        """, (points, correct, user_id))


# =====================================
# MENUS
# =====================================

MAIN_MENU = [
    ["📚 الدروس", "✏️ التمارين"],
    ["🧠 اختبر مستواك", "⚡ التحديات"],
    ["👤 ملفي الشخصي", "📊 تقدمي الدراسي"],
    ["🏆 الترتيب", "ℹ️ المساعدة"],
]

KEYBOARD = ReplyKeyboardMarkup(
    MAIN_MENU,
    resize_keyboard=True
)

BACK_MENU = ReplyKeyboardMarkup(
    [["🔙 القائمة الرئيسية"]],
    resize_keyboard=True
)

BRANCHES = [
    "رياضيات",
    "تقني رياضي",
    "علوم تجريبية",
    "تسيير واقتصاد",
]

WILAYAS = [
    "أدرار", "الشلف", "الأغواط", "أم البواقي",
    "باتنة", "بجاية", "بسكرة", "بشار",
    "البليدة", "البويرة", "تمنراست", "تبسة",
    "تلمسان", "تيارت", "تيزي وزو", "الجزائر",
    "الجلفة", "جيجل", "سطيف", "سعيدة",
    "سكيكدة", "سيدي بلعباس", "عنابة", "قالمة",
    "قسنطينة", "المدية", "مستغانم", "المسيلة",
    "معسكر", "ورقلة", "وهران", "البيض",
    "إليزي", "برج بوعريريج", "بومرداس", "الطارف",
    "تندوف", "تيسمسيلت", "الوادي", "خنشلة",
    "سوق أهراس", "تيبازة", "ميلة", "عين الدفلى",
    "النعامة", "عين تموشنت", "غرداية", "غليزان",
    "تيميمون", "برج باجي مختار", "أولاد جلال",
    "بني عباس", "عين صالح", "عين قزام",
    "تقرت", "جانت", "المغير", "المنيعة",
]

# =====================================
# QUIZ DATA
# =====================================

QUESTIONS = [
    {
        "question": "إذا كانت f(x)=x²، فما قيمة f'(2)؟",
        "options": ["2", "4", "6", "8"],
        "answer": 1,
        "explanation": "f'(x)=2x وبالتالي f'(2)=4."
    },
    {
        "question": "ما نهاية (1/n) عندما n يؤول إلى +∞؟",
        "options": ["1", "+∞", "0", "-∞"],
        "answer": 2,
        "explanation": "مقلوب عدد طبيعي متزايد يؤول إلى الصفر."
    },
    {
        "question": "ما مشتقة الدالة e^x؟",
        "options": ["x e^x", "e^x", "1/e^x", "x"],
        "answer": 1,
        "explanation": "الدالة الأسية مشتقتها هي نفسها."
    },
    {
        "question": "إذا كان U(n)=3n+2، فما U(4)؟",
        "options": ["10", "12", "14", "16"],
        "answer": 2,
        "explanation": "U(4)=3×4+2=14."
    },
    {
        "question": "ما قيمة ln(e)؟",
        "options": ["0", "1", "e", "-1"],
        "answer": 1,
        "explanation": "اللوغاريتم الطبيعي والأسية دالتان عكسيتان."
    },
]


# =====================================
# GENERAL FUNCTIONS
# =====================================

async def show_main_menu(update):
    await update.message.reply_text(
        "اختاري الخدمة التي تريدينها 👇",
        reply_markup=KEYBOARD
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_student(user)

    await update.message.reply_text(
        "مرحباً بك في MINDEX Academy 🎓\n\n"
        "منصة المرافقة الذكية للتحضير لبكالوريا 2027.\n\n"
        "رحلتك نحو التفوق تبدأ من هنا! ✨",
        reply_markup=KEYBOARD
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ مساعدة MINDEX Academy\n\n"
        "/start - القائمة الرئيسية\n"
        "/lessons - الدروس\n"
        "/exercises - التمارين\n"
        "/quiz - اختبار المستوى\n"
        "/profile - الملف الشخصي\n"
        "/progress - التقدم الدراسي\n"
        "/ranking - الترتيب\n"
        "/help - المساعدة",
        reply_markup=KEYBOARD
    )


# =====================================
# PROFILE
# =====================================

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    student = get_student(user_id)

    if not student:
        register_student(update.effective_user)
        student = get_student(user_id)

    await update.message.reply_text(
        "👤 ملفك الشخصي\n\n"
        f"الاسم: {student[1]}\n"
        f"الشعبة: {student[2] or 'غير محددة'}\n"
        f"الولاية: {student[3] or 'غير محددة'}\n"
        f"النقاط: {student[4]} XP\n"
        f"عدد الاختبارات: {student[5]}",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["🎓 اختيار الشعبة"],
                ["📍 اختيار الولاية"],
                ["🔙 القائمة الرئيسية"],
            ],
            resize_keyboard=True
        )
    )


async def choose_branch(update, context):
    keyboard = [[branch] for branch in BRANCHES]
    keyboard.append(["🔙 القائمة الرئيسية"])

    await update.message.reply_text(
        "🎓 اختاري شعبتك:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


async def choose_wilaya(update, context):
    keyboard = [[wilaya] for wilaya in WILAYAS]
    keyboard.append(["🔙 القائمة الرئيسية"])

    await update.message.reply_text(
        "📍 اختاري ولايتك:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


# =====================================
# LESSONS
# =====================================

async def lessons(update, context):
    branch = "رياضيات"
    topics = LESSONS.get(branch, [])

    if not topics:
        await update.message.reply_text(
            "لا توجد وحدات مسجلة حالياً."
        )
        return

    keyboard = [
        [f"📖 {topic}"]
        for topic in topics
    ]
    keyboard.append(["🔙 القائمة الرئيسية"])

    await update.message.reply_text(
        "📚 فضاء الدروس\n\n"
        "الوحدات المتاحة حالياً لشعبة الرياضيات:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


async def show_lesson(update, context, topic):
    await update.message.reply_text(
        f"📖 {topic}\n\n"
        "محتوى هذه الوحدة قيد الإعداد.\n"
        "سيتم توفير الشرح المنظم والأمثلة والملخصات."
    )


# =====================================
# EXERCISES
# =====================================

async def exercises(update, context):
    await update.message.reply_text(
        "✏️ فضاء التمارين\n\n"
        "سيتم تنظيم التمارين حسب:\n"
        "🟢 سهل\n"
        "🟡 متوسط\n"
        "🔴 صعب\n"
        "🏆 مستوى بكالوريا\n\n"
        "محتوى التمارين قيد الإعداد.",
        reply_markup=BACK_MENU
    )


# =====================================
# QUIZ
# =====================================

async def quiz(update, context):
    context.user_data["quiz_questions"] = random.sample(
        QUESTIONS,
        min(5, len(QUESTIONS))
    )
    context.user_data["quiz_index"] = 0
    context.user_data["quiz_score"] = 0
    context.user_data["quiz_correct"] = 0
    context.user_data["quiz_active"] = True

    await send_question(update, context)


async def send_question(update, context):
    index = context.user_data["quiz_index"]
    questions = context.user_data["quiz_questions"]

    if index >= len(questions):
        score = context.user_data["quiz_score"]
        correct = context.user_data["quiz_correct"]
        user_id = update.effective_user.id

        add_score(user_id, score, correct)

        context.user_data["quiz_active"] = False

        await update.message.reply_text(
            "🏁 انتهى الاختبار!\n\n"
            f"الإجابات الصحيحة: {correct}/{len(questions)}\n"
            f"النقاط المكتسبة: {score} XP\n\n"
            "استمري في التعلم والتطور! 🎓",
            reply_markup=KEYBOARD
        )
        return

    question = questions[index]

    keyboard = [
        [option]
        for option in question["options"]
    ]

    keyboard.append(["🔙 القائمة الرئيسية"])

    await update.message.reply_text(
        f"🧠 السؤال {index + 1}/{len(questions)}\n\n"
        f"{question['question']}",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


async def answer_question(update, context):
    if not context.user_data.get("quiz_active"):
        return False

    index = context.user_data["quiz_index"]
    questions = context.user_data["quiz_questions"]
    question = questions[index]

    answer = update.message.text
    options = question["options"]

    if answer not in options:
        await update.message.reply_text(
            "اختاري إجابة من الخيارات المعروضة."
        )
        return True

    selected = options.index(answer)

    if selected == question["answer"]:
        context.user_data["quiz_score"] += 10
        context.user_data["quiz_correct"] += 1

        result = "✅ إجابة صحيحة! +10 XP"
    else:
        correct_answer = options[question["answer"]]
        result = f"❌ إجابة غير صحيحة.\nالإجابة الصحيحة: {correct_answer}"

    result += "\n\n" + question["explanation"]

    context.user_data["quiz_index"] += 1

    await update.message.reply_text(result)
    await send_question(update, context)

    return True


# =====================================
# CHALLENGES
# =====================================

async def challenges(update, context):
    keyboard = [
        ["⚡ تحدي يومي"],
        ["🧠 تحدي التفكير"],
        ["🏆 تحدي شامل"],
        ["🔙 القائمة الرئيسية"]
    ]

    await update.message.reply_text(
        "⚡ فضاء التحديات\n\n"
        "اختاري نوع التحدي:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


async def daily_challenge(update, context):
    question = random.choice(QUESTIONS)

    context.user_data["challenge"] = question

    await update.message.reply_text(
        "⚡ تحدي MINDEX\n\n"
        f"{question['question']}\n\n"
        + "\n".join(question["options"]),
        reply_markup=BACK_MENU
    )


# =====================================
# PROGRESS
# =====================================

async def progress(update, context):
    student = get_student(update.effective_user.id)

    if not student:
        register_student(update.effective_user)
        student = get_student(update.effective_user.id)

    await update.message.reply_text(
        "📊 تقدمك الدراسي\n\n"
        f"النقاط: {student[4]} XP\n"
        f"الاختبارات: {student[5]}\n"
        f"الإجابات الصحيحة: {student[6]}\n\n"
        "واصل العمل لتحقيق هدفك! 🎓",
        reply_markup=KEYBOARD
    )


# =====================================
# RANKING
# =====================================

async def ranking(update, context):
    with db() as conn:
        rows = conn.execute("""
            SELECT full_name, xp
            FROM students
            ORDER BY xp DESC
            LIMIT 10
        """).fetchall()

    if not rows:
        await update.message.reply_text(
            "لا يوجد ترتيب حالياً."
        )
        return

    message = "🏆 أفضل 10 تلاميذ في MINDEX\n\n"

    for index, row in enumerate(rows, start=1):
        message += f"{index}. {row[0]} — {row[1]} XP\n"

    await update.message.reply_text(
        message,
        reply_markup=KEYBOARD
    )


# =====================================
# MENU HANDLER
# =====================================

async def menu_handler(update, context):
    if not update.message or not update.message.text:
        return

    text = update.message.text

    if await answer_question(update, context):
        return

    if text == "🔙 القائمة الرئيسية":
        context.user_data["quiz_active"] = False
        await show_main_menu(update)

    elif text == "📚 الدروس":
        await lessons(update, context)

    elif text == "✏️ التمارين":
        await exercises(update, context)

    elif text == "🧠 اختبر مستواك":
        await quiz(update, context)

    elif text == "⚡ التحديات":
        await challenges(update, context)

    elif text == "⚡ تحدي يومي":
        await daily_challenge(update, context)

    elif text in ["🧠 تحدي التفكير", "🏆 تحدي شامل"]:
        await update.message.reply_text(
            "هذا التحدي قيد الإعداد."
        )

    elif text == "👤 ملفي الشخصي":
        await profile(update, context)

    elif text == "🎓 اختيار الشعبة":
        await choose_branch(update, context)

    elif text == "📍 اختيار الولاية":
        await choose_wilaya(update, context)

    elif text in BRANCHES:
        update_student(update.effective_user.id, branch=text)
        await update.message.reply_text(
            f"تم تسجيل شعبتك: {text} ✅",
            reply_markup=KEYBOARD
        )

    elif text in WILAYAS:
        update_student(update.effective_user.id, wilaya=text)
        await update.message.reply_text(
            f"تم تسجيل ولايتك: {text} ✅",
            reply_markup=KEYBOARD
        )

    elif text == "📊 تقدمي الدراسي":
        await progress(update, context)

    elif text == "🏆 الترتيب":
        await ranking(update, context)

    elif text == "ℹ️ المساعدة":
        await help_command(update, context)

    elif text.startswith("📖 "):
        await show_lesson(update, context, text[3:])

    elif context.user_data.get("challenge"):
        question = context.user_data["challenge"]
        if text in question["options"]:
            if question["options"].index(text) == question["answer"]:
                await update.message.reply_text(
                    "✅ إجابة صحيحة! أحسنتِ."
                )
                add_score(update.effective_user.id, 10)
            else:
                await update.message.reply_text(
                    "❌ إجابة غير صحيحة.\n"
                    f"الإجابة الصحيحة: {question['options'][question['answer']]}"
                )
            context.user_data.pop("challenge", None)

    else:
        await update.message.reply_text(
            "اختاري خدمة من القائمة من فضلك 👇",
            reply_markup=KEYBOARD
        )


# =====================================
# MAIN
# =====================================

def main():
    init_db()

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
