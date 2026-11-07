# =====================================
# MINDEX ACADEMY - BAC 2027
# BOT V2
# =====================================

import os
import json
import random
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

import database as db
from content import (
    LESSONS,
    LESSON_DESCRIPTIONS,
    DAILY_CHALLENGE_QUESTIONS,
    LEVEL_TEST_QUESTIONS,
    XP_REWARDS,
    LEVELS,
    MONTHLY_CHAMPION_TITLE,
)

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
# GENERAL FUNCTIONS
# =====================================

async def show_main_menu(update):
    await update.message.reply_text(
        "اختاري الخدمة التي تريدينها 👇",
        reply_markup=KEYBOARD
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    db.register_student(user.id, user.full_name)

    await update.message.reply_text(
        "مرحباً بك في MINDEX Academy 🎓\n\n"
        "منصة المرافقة للتحضير لبكالوريا 2027.\n\n"
        "رحلتك نحو التفوق تبدأ من هنا! ✨",
        reply_markup=KEYBOARD
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ مساعدة MINDEX Academy\n\n"
        "/start - القائمة الرئيسية\n"
        "/profile - الملف الشخصي\n"
        "/quiz - اختبار المستوى\n"
        "/ranking - الترتيب\n"
        "/help - المساعدة",
        reply_markup=KEYBOARD
    )


# =====================================
# PROFILE
# =====================================

async def profile(update, context):
    user = update.effective_user
    db.register_student(user.id, user.full_name)

    student = db.get_student(user.id)

    await update.message.reply_text(
        "👤 ملفك الشخصي\n\n"
        f"الاسم: {student['full_name']}\n"
        f"الشعبة: {student['branch'] or 'غير محددة'}\n"
        f"الولاية: {student['wilaya'] or 'غير محددة'}\n"
        f"النقاط: {student['xp']} XP\n"
        f"الاختبارات: {student['quizzes']}\n"
        f"الإجابات الصحيحة: {student['correct']}",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["🎓 تغيير الشعبة"],
                ["📍 تغيير الولاية"],
                ["🔙 القائمة الرئيسية"],
            ],
            resize_keyboard=True
        )
    )


async def choose_branch(update, context):
    context.user_data["profile_step"] = "branch"

    keyboard = [[x] for x in BRANCHES]
    keyboard.append(["🔙 القائمة الرئيسية"])

    await update.message.reply_text(
        "🎓 اختاري شعبتك:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


async def choose_wilaya(update, context):
    context.user_data["profile_step"] = "wilaya"

    keyboard = [[x] for x in WILAYAS]
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
    student = db.get_student(update.effective_user.id)
    branch = student["branch"] if student else ""

    if not branch:
        await update.message.reply_text(
            "اختاري شعبتك أولاً من الملف الشخصي.",
            reply_markup=KEYBOARD
        )
        return

    topics = LESSONS.get(branch, [])

    keyboard = [[f"📖 {topic}"] for topic in topics]
    keyboard.append(["🔙 القائمة الرئيسية"])

    await update.message.reply_text(
        f"📚 دروس شعبة {branch}\n\n"
        "اختاري الوحدة التي تريدين مراجعتها:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


async def show_lesson(update, context, topic):
    description = LESSON_DESCRIPTIONS.get(
        topic,
        "محتوى هذه الوحدة قيد الإعداد."
    )

    await update.message.reply_text(
        f"📖 {topic}\n\n"
        f"{description}\n\n"
        "سيتم إضافة الدرس المفصل والأمثلة والتمارين تدريجياً.",
        reply_markup=BACK_MENU
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
        "بنك التمارين قيد التطوير.",
        reply_markup=BACK_MENU
    )


# =====================================
# QUIZ SYSTEM
# =====================================

async def begin_test(update, context, attempt_type):
    user_id = update.effective_user.id

    if attempt_type == "daily":
        source = DAILY_CHALLENGE_QUESTIONS
        total = 10
        title = "⚡ التحدي اليومي"
    else:
        source = LEVEL_TEST_QUESTIONS
        total = min(5, len(source))
        title = "🧠 اختبار المستوى"

    old_attempt = db.get_attempt(user_id, attempt_type)

    if old_attempt:
        if old_attempt["status"] == "completed":
            await update.message.reply_text(
                "لقد استعملت محاولتك اليوم بالفعل. "
                "عودي غداً لتحدٍ جديد! 🌟",
                reply_markup=KEYBOARD
            )
            return

        questions = json.loads(old_attempt["question_data"])

        context.user_data["active_test"] = {
            "type": attempt_type,
            "questions": questions,
        }

        await update.message.reply_text(
            "وجدت محاولة غير مكتملة، سنواصل من حيث توقفتِ."
        )

        await send_active_question(update, context)
        return

    questions = random.sample(source, total)

    created = db.create_attempt(
        user_id,
        attempt_type,
        total,
        json.dumps(questions, ensure_ascii=False)
    )

    if not created:
        await update.message.reply_text(
            "لم نتمكن من إنشاء المحاولة. حاولي مجدداً."
        )
        return

    context.user_data["active_test"] = {
        "type": attempt_type,
        "questions": questions,
    }

    await update.message.reply_text(
        f"{title}\n\n"
        f"عدد الأسئلة: {total}\n"
        "اختاري إجابة واحدة لكل سؤال.\n"
        "ستحصلين على التصحيح والشرح بعد كل إجابة.\n\n"
        "بالتوفيق! 🎓"
    )

    await send_active_question(update, context)


async def send_active_question(update, context):
    state = context.user_data.get("active_test")

    if not state:
        return

    attempt_type = state["type"]
    attempt = db.get_attempt(
        update.effective_user.id,
        attempt_type
    )

    if not attempt:
        return

    questions = state["questions"]
    index = attempt["current_index"]

    if index >= len(questions):
        await finish_test(update, context)
        return

    question = questions[index]

    keyboard = [[option] for option in question["options"]]

    await update.message.reply_text(
        f"السؤال {index + 1}/{len(questions)}\n\n"
        f"{question['question']}",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


async def answer_active_test(update, context):
    state = context.user_data.get("active_test")

    if not state:
        return False

    user_id = update.effective_user.id
    attempt_type = state["type"]

    attempt = db.get_attempt(user_id, attempt_type)

    if not attempt or attempt["status"] != "in_progress":
        context.user_data.pop("active_test", None)
        return False

    questions = state["questions"]
    index = attempt["current_index"]

    if index >= len(questions):
        await finish_test(update, context)
        return True

    question = questions[index]
    answer = update.message.text

    if answer not in question["options"]:
        await update.message.reply_text(
            "اختاري إجابة من الخيارات المعروضة."
        )
        return True

    selected = question["options"].index(answer)
    is_correct = selected == question["answer"]

    score = attempt["score"]
    correct = attempt["correct"]

    if is_correct:
        score += XP_REWARDS["correct_answer"]
        correct += 1

        result = "✅ إجابة صحيحة! +10 XP"
    else:
        correct_answer = question["options"][question["answer"]]

        result = (
            "❌ إجابة غير صحيحة.\n"
            f"الإجابة الصحيحة: {correct_answer}"
        )

    result += "\n\n📘 الشرح:\n" + question["explanation"]

    next_index = index + 1

    db.update_attempt(
        user_id,
        attempt_type,
        score,
        correct,
        next_index
    )

    await update.message.reply_text(result)

    if next_index >= len(questions):
        await finish_test(update, context)
    else:
        await send_active_question(update, context)

    return True


async def finish_test(update, context):
    state = context.user_data.get("active_test")

    if not state:
        return

    user_id = update.effective_user.id
    attempt_type = state["type"]

    attempt = db.get_attempt(user_id, attempt_type)

    if not attempt:
        return

    db.finish_attempt(user_id, attempt_type)

    if attempt["score"] > 0:
        db.add_xp(
            user_id,
            attempt["score"],
            event_type=attempt_type
        )

    context.user_data.pop("active_test", None)

    title = (
        "⚡ انتهى التحدي اليومي!"
        if attempt_type == "daily"
        else "🧠 انتهى اختبار المستوى!"
    )

    await update.message.reply_text(
        f"{title}\n\n"
        f"الإجابات الصحيحة: {attempt['correct']}/{attempt['total']}\n"
        f"النقاط المكتسبة: {attempt['score']} XP\n\n"
        "استمري في التعلم والتطور! 🌟",
        reply_markup=KEYBOARD
    )


# =====================================
# CHALLENGES
# =====================================

async def challenges(update, context):
    keyboard = [
        ["⚡ تحدي يومي"],
        ["🧠 اختبر مستواك"],
        ["🔙 القائمة الرئيسية"]
    ]

    await update.message.reply_text(
        "⚡ فضاء التحديات\n\n"
        "اختاري التحدي:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


# =====================================
# PROGRESS
# =====================================

async def progress(update, context):
    student = db.get_student(update.effective_user.id)

    if not student:
        await update.message.reply_text(
            "استعملي /start أولاً."
        )
        return

    await update.message.reply_text(
        "📊 تقدمك الدراسي\n\n"
        f"النقاط: {student['xp']} XP\n"
        f"الاختبارات: {student['quizzes']}\n"
        f"الإجابات الصحيحة: {student['correct']}\n\n"
        "كل خطوة تقربك من هدفك! 🎓",
        reply_markup=KEYBOARD
    )


# =====================================
# RANKINGS
# =====================================

async def ranking_menu(update, context):
    keyboard = [
        ["📅 ترتيب اليوم"],
        ["📆 ترتيب الأسبوع"],
        ["🗓️ ترتيب الشهر"],
        ["📍 ترتيب الولايات"],
        ["🎓 ترتيب الشعب"],
        ["🔙 القائمة الرئيسية"]
    ]

    await update.message.reply_text(
        "🏆 اختاري نوع الترتيب:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


async def show_student_ranking(update, period):
    rows = db.get_ranking(10, period)

    names = {
        "daily": "اليومي",
        "weekly": "الأسبوعي",
        "monthly": "الشهري",
    }

    message = f"🏆 الترتيب {names[period]}\n\n"

    if not rows:
        message += "لا توجد نتائج حالياً."
    else:
        for i, row in enumerate(rows, start=1):
            message += (
                f"{i}. {row['full_name']} — "
                f"{row['xp']} XP\n"
            )

        if period == "monthly":
            message += (
                "\n🥇 صاحب المركز الأول هو "
                f"حامل لقب {MONTHLY_CHAMPION_TITLE}"
            )

    await update.message.reply_text(
        message,
        reply_markup=KEYBOARD
    )


async def show_group_ranking(update, group, period="monthly"):
    rows = db.get_group_ranking(group, period)

    title = "الولايات" if group == "wilaya" else "الشعب"

    message = f"🏆 ترتيب {title}\n\n"

    if not rows:
        message += "لا توجد نتائج حالياً."
    else:
        for i, row in enumerate(rows, start=1):
            message += (
                f"{i}. {row['name']} — "
                f"{row['points']} XP\n"
            )

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
    user_id = update.effective_user.id

    db.register_student(
        user_id,
        update.effective_user.full_name
    )

    # Continue an active test before processing menus.
    if await answer_active_test(update, context):
        return

    profile_step = context.user_data.get("profile_step")

    if profile_step == "branch":
        if text in BRANCHES:
            db.update_branch(user_id, text)
            context.user_data.pop("profile_step", None)

            await update.message.reply_text(
                f"تم تسجيل شعبتك: {text} ✅",
                reply_markup=KEYBOARD
            )
        return

    if profile_step == "wilaya":
        if text in WILAYAS:
            db.update_wilaya(user_id, text)
            context.user_data.pop("profile_step", None)

            await update.message.reply_text(
                f"تم تسجيل ولايتك: {text} ✅",
                reply_markup=KEYBOARD
            )
        return

    if text == "🔙 القائمة الرئيسية":
        await show_main_menu(update)

    elif text == "📚 الدروس":
        await lessons(update, context)

    elif text == "✏️ التمارين":
        await exercises(update, context)

    elif text == "🧠 اختبر مستواك":
        await begin_test(update, context, "level")

    elif text == "⚡ التحديات":
        await challenges(update, context)

    elif text == "⚡ تحدي يومي":
        await begin_test(update, context, "daily")

    elif text == "👤 ملفي الشخصي":
        await profile(update, context)

    elif text == "🎓 تغيير الشعبة":
        await choose_branch(update, context)

    elif text == "📍 تغيير الولاية":
        await choose_wilaya(update, context)

    elif text == "📊 تقدمي الدراسي":
        await progress(update, context)

    elif text == "🏆 الترتيب":
        await ranking_menu(update, context)

    elif text == "📅 ترتيب اليوم":
        await show_student_ranking(update, "daily")

    elif text == "📆 ترتيب الأسبوع":
        await show_student_ranking(update, "weekly")

    elif text == "🗓️ ترتيب الشهر":
        await show_student_ranking(update, "monthly")

    elif text == "📍 ترتيب الولايات":
        await show_group_ranking(update, "wilaya")

    elif text == "🎓 ترتيب الشعب":
        await show_group_ranking(update, "branch")

    elif text == "ℹ️ المساعدة":
        await help_command(update, context)

    elif text.startswith("📖 "):
        await show_lesson(update, context, text[3:])

    else:
        await update.message.reply_text(
            "اختاري خدمة من القائمة من فضلك 👇",
            reply_markup=KEYBOARD
        )


# =====================================
# MAIN
# =====================================

def main():
    db.init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("lessons", lessons))
    app.add_handler(CommandHandler("exercises", exercises))
    app.add_handler(CommandHandler("quiz", lambda u, c: begin_test(u, c, "level")))
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CommandHandler("ranking", ranking_menu))

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
