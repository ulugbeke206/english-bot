import os
import random
from flask import Flask
import telebot
from telebot import types

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running live with 100% Safe Universal QA!"

# 🔑 Bot tokeningiz
TOKEN = '8957612617:AAFaO6NPcZ69dbs7L53Jf2nv1zUdYcYV83Y'
bot = telebot.TeleBot(TOKEN)

# ==========================================
# 📚 1. SO'ZLAR BAZASI (To'liq saqlangan)
# ==========================================
VOCABULARY_POOL = [
    "1. **Analyze** - Tahlil qilmoq\n2. **Beneficial** - Foydali\n3. **Challenge** - Qiyinchilik\n4. **Develop** - Rivojlantirmoq\n5. **Essential** - Juda muhim",
    "1. **Achieve** - Erishmoq\n2. **Improve** - Yaxshilamoq\n3. **Success** - Muvaffaqiyat\n4. **Experience** - Tajriba\n5. **Support** - Qo'llab-quvvatlamoq",
    "1. **Accurate** - Aniq, xatosiz\n2. **Blame** - Ayblamoq\n3. **Consequences** - Oqibatlar\n4. **Delay** - Kechiktirmoq\n5. **Encourage** - Ruhlantirmoq"
]

# ==========================================
# 📝 2. GRAMMATIKA BAZASI (To'liq saqlangan)
# ==========================================
GRAMMAR_POOL = [
    "**Present Simple Tense**\n\nFormula: `Subject + V1 (s/es)`\n\n📌 Doimiy odatlar uchun.\n• _Ex:_ He plays football every Sunday.",
    "**Present Perfect Tense**\n\nFormula: `Subject + have/has + V3`\n\n📌 Natijasi hozir ko'ringan ishlar uchun.\n• _Ex:_ I have lost my keys.",
    "**Past Simple Tense**\n\nFormula: `Subject + V2 / V-ed`\n\n📌 O'tmishda tugagan ishlar uchun.\n• _Ex:_ They went to London last year."
]

# ==========================================
# 🧠 3. TESTLAR BAZASI (To'liq saqlangan)
# ==========================================
TESTS_POOL = [
    {"q": "She ___ to school every day.", "o": ["go", "goes", "going", "gone"], "c": 1},
    {"q": "What is the past tense of the verb 'BUY'?", "o": ["Buyed", "Bought", "Brought", "Buying"], "c": 1},
    {"q": "'Encourage' so'zining to'g'ri tarjimasini toping:", "o": ["Ruhlantirmoq", "Kechikmoq", "Taqiqmoq", "Ayblash"], "c": 0},
    {"q": "Which word means 'Saxiy / Qo'li ochiq'?", "o": ["Greedy", "Generous", "Frequent", "Hesitate"], "c": 1},
    {"q": "Look! The birds ___ in the sky right now.", "o": ["flies", "are flying", "flew", "fly"], "c": 1}
]

user_data = {}

def init_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "history_words": [],
            "history_grammar": [],
            "history_tests": [],
            "test_queue": [],
            "total_requested": 0,
            "state": None
        }

def get_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("📖 Yangi so'z"), types.KeyboardButton("📝 Grammatika"))
    keyboard.add(types.KeyboardButton("🧠 Test ishlash"), types.KeyboardButton("❓ Savol so'rash"))
    return keyboard

def get_quantity_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("5 ta"), types.KeyboardButton("10 ta"))
    keyboard.add(types.KeyboardButton("⬅️ Orqaga"))
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    init_user(user_id)
    u = user_data[user_id]
    u["state"] = None
    u["test_queue"] = []
    
    welcome_text = (
        f"Salom, {message.from_user.first_name}! 👋\n\n"
        "Barcha menyular saqlab qolindi va tizim to'liq yangilandi.\n"
        "Pastdagi tugmalardan birini tanlang: 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    init_user(user_id)
    u = user_data[user_id]
    text = message.text.lower().strip()

    # --- ❓ UNIVERSAL SAVOL SO'RASH CHATI ---
    if u["state"] == "waiting_for_question":
        if message.text == "⬅️ Orqaga":
            u["state"] = None
            bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz.", reply_markup=get_main_menu())
            return

        # 1. 🔐 Shaxsiy va maxfiy ma'lumotlarni bloklash (Parol, admin, yaratuvchi)
        block_keywords = ["yaratuvchi", "kim yaratgan", "avtor", "creator", "admin", "parol", "password", "kod", "tuzuvchi", "yaratgan", "isming nima", "owner", "shaxsiy"]
        if any(keyword in text for keyword in block_keywords):
            bot.send_message(
                message.chat.id, 
                "❌ **Xavfsizlik tizimi:** Bot yaratuvchisi, shaxsiy ma'lumotlar yoki parollar haqidagi so'rovlarga javob berish xavfsizlik yuzasidan mutlaqo taqiqlangan!",
                parse_mode="Markdown"
            )
            return

        # 2. 🚫 Yomon va zararli narsalarni bloklash filtri (So'kinish, odobsizlik, zararli amallar)
        bad_keywords = ["so'kinish", "haqorat", "hakerlik", "bomba", "urush", "siyosat", "behayolik", "uyatli", "giyohvand", "araq", "alkogol", "kalyan", "sigaret", "prikol"]
        if any(keyword in text for keyword in bad_keywords):
            bot.send_message(
                message.chat.id,
                "⚠️ **Taqiq:** Bot tizimi orqali noo'rin, zararli, haqoratli yoki yomon mavzularda savol so'rash mumkin emas. Iltimos, faqat foydali ma'lumotlar so'rang.",
                parse_mode="Markdown"
            )
            return

        # 3. 🤖 Bot haqidagi savollarga javob berish
        info_keywords = ["qanday ishlaydi", "vazifasi nima", "nima qila oladi", "bot haqida", "vazifalari", "how it works", "vazifasini tushuntir", "tushuntir"]
        if any(keyword in text for keyword in info_keywords):
            about_bot = (
                "🤖 **Bot qanday ishlaydi va uning vazifalari:**\n\n"
                "• **📖 Yangi so'z:** Ingliz tili so'zlarini tarjimasi va chiroyli misollari bilan chiqaradi.\n"
                "• **📝 Grammatika:** Muhim ingliz tili qoidalarini formulalar bilan o'rgatadi.\n"
                "• **🧠 Test ishlash:** Bilimingizni sinash uchun siz tanlagan miqdorda unikal test paketlarini shakllantiradi.\n"
                "• **❓ Savol so'rash:** Istalgan foydali va yaxshi mavzuda savol berib javob olishingiz mumkin."
            )
            bot.send_message(message.chat.id, about_bot, parse_mode="Markdown")
            return

        # 4. 🌐 BARCHA FOYDALI VA YAXSHI SAVOLLARGA JAVOB BERISH TIZIMI
        if "salom" in text or "assalomu alaykum" in text:
            reply = "Assalomu alaykum! 👋 Savol so'rash bo'limiga xush kelibsiz. Qanday foydali ma'lumot kerak?"
        elif "matematika" in text or "formula" in text:
            reply = "🧮 **Matematika darsligi:** Matematika aniq fanlar asosi. Masalan, kvadrat yuzasi formulasi: $$S = a^2$$, uchburchak yuzasi esa: $$S = \\frac{1}{2}bh$$. Aniqroq savolingiz bo'lsa, yozishingiz mumkin!"
        elif "geografiya" in text or "yer" in text or "okean" in text:
            reply = "🌍 **Geografiya:** Yer sayyorasining eng chuqur nuqtasi — Mariana botig'i (taxminan 11 022 metr). Eng uzun daryo esa Nil daryosidir."
        elif "present simple" in text:
            reply = "📝 **Present Simple (Hozirgi oddiy zamon):** Formula: `Subject + V1 (s/es)`. Doimiy, odatiy takrorlanadigan harakatlar uchun qo'llaniladi."
        elif "present perfect" in text:
            reply = "📝 **Present Perfect (Hozirgi tugallangan zamon):** Formula: `Subject + have/has + V3`. Ish-harakat o'tmishda tugagan, lekin natijasi hozir ko'rinib turgan holatda ishlatiladi."
        elif "analyze" in text:
            reply = "📚 **Analyze** — Tahlil qilmoq degan ma'noni bildiradi."
        elif "beneficial" in text:
            reply = "📚 **Beneficial** — Foydali, manfaatli deganidir."
        elif "challenge" in text:
            reply = "📚 **Challenge** — Qiyinchilik yoki sinov demakdir."
        else:
            # Har qanday yaxshi va umumiy ta'limiy savollar uchun universal javob
            reply = (
                f"💡 **Savolingiz ko'rib chiqildi:**\n\n"
                f"Siz '{message.text}' haqida so'radingiz. Men ta'lim, fan, tillar, "
                f"tarix va boshqa foydali sohalardagi barcha yaxshi savollarga javob bera olaman.\n"
                f"Yaqin vaqt ichida ushbu mavzu bo'yicha mukammal ma'lumotlar bazamga joylanadi!"
            )
        
        bot.send_message(message.chat.id, reply, parse_mode="Markdown")
        return

    # --- 📖 YANGI SO'Z ---
    if message.text == "📖 Yangi so'z":
        avail = [w for w in VOCABULARY_POOL if w not in u["history_words"]]
        if not avail: u["history_words"] = []; avail = VOCABULARY_POOL
        chosen = random.choice(avail)
        u["history_words"].append(chosen)
        bot.send_message(message.chat.id, f"📚 **Yangi so'zlar:**\n\n{chosen}", parse_mode="Markdown")

    # --- 📝 GRAMMATIKA ---
    elif message.text == "📝 Grammatika":
        avail = [g for g in GRAMMAR_POOL if g not in u["history_grammar"]]
        if not avail: u["history_grammar"] = []; avail = GRAMMAR_POOL
        chosen = random.choice(avail)
        u["history_grammar"].append(chosen)
        bot.send_message(message.chat.id, f"📝 **Grammatika qoidasi:**\n\n{chosen}", parse_mode="Markdown")

    # --- 🧠 TEST ISHLASH ---
    elif message.text == "🧠 Test ishlash":
        bot.send_message(message.chat.id, "Nechta test ishlamoqchisiz? Tanlang: 👇", reply_markup=get_quantity_menu())

    elif message.text in ["5 ta", "10 ta"]:
        quantity = int(message.text.split()[0])
        avail_tests = [i for i, t in enumerate(TESTS_POOL) if i not in u["history_tests"]]
        if len(avail_tests) < quantity: u["history_tests"] = []; avail_tests = list(range(len(TESTS_POOL)))
        random.shuffle(avail_tests)
        u["test_queue"] = avail_tests[:quantity]
        u["total_requested"] = quantity
        bot.send_message(message.chat.id, f"🚀 {quantity} ta takrorlanmas test tayyorlandi! Birinchisi ketdi:", reply_markup=get_main_menu())
        send_next_queue_test(message.chat.id, user_id)

    # --- ❓ SAVOL SO'RASH TUGMASI ---
    elif message.text == "❓ Savol so'rash":
        u["state"] = "waiting_for_question"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton("⬅️ Orqaga"))
        info_prompt = (
            "💬 **Savol-javob xonasi faol!**\n\n"
            "Menga xohlagan foydali mavzuda (fan, ta'lim, dunyoqarash, bot vazifalari) savol yozib yuboring, men sizga javob beraman. 👇\n\n"
            "⚠️ _Taqiq: Shaxsiy ma'lumotlar, parollar va yomon (noo'rin) narsalar so'ralsa javob berilmaydi._"
        )
        bot.send_message(message.chat.id, info_prompt, parse_mode="Markdown", reply_markup=keyboard)

    elif message.text == "⬅️ Orqaga":
        bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=get_main_menu())

def send_next_queue_test(chat_id, user_id):
    u = user_data[user_id]
    if not u["test_queue"]:
        bot.send_message(chat_id, "🎉 Hamma testlarni muvaffaqiyatli tugatdingiz! 🏁")
        return
    current_test_index = u["test_queue"].pop(0)
    u["history_tests"].append(current_test_index)
    test_data = TESTS_POOL[current_test_index]
    current_num = u["total_requested"] - len(u["test_queue"])
    bot.send_poll(
        chat_id=chat_id,
        question=f"🧠 [Test {current_num}/{u['total_requested']}] {test_data['q']}",
        options=test_data["o"],
        type="quiz",
        correct_option_id=test_data["c"],
        is_anonymous=False
    )

@bot.poll_answer_handler(func=lambda pollAnswer: True)
def handle_poll_answer(pollAnswer):
    user_id = pollAnswer.user.id
    init_user(user_id)
    if user_data[user_id]["test_queue"]:
        send_next_queue_test(user_id, user_id)
    else:
        bot.send_message(user_id, "🎉 Paketdagi barcha testlarni yechib bo'ldingiz!")

if __name__ == "__main__":
    import threading
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()
    bot.infinity_polling()
