import os
import random
import time
import requests
from flask import Flask
import telebot
from telebot import types

app = Flask(__name__)

# O'zining URL manzilini avtomatik aniqlash (Render uchun)
RENDER_APP_NAME = os.environ.get("RENDER_EXTERNAL_URL", "https://english-bot-lsq4.onrender.com")

@app.route('/')
def home():
    return "Bot is running live 24/7 without sleeping!"

# 🔑 Bot tokeningiz
TOKEN = '8957612617:AAFaO6NPcZ69dbs7L53Jf2nv1zUdYcYV83Y'
bot = telebot.TeleBot(TOKEN)

# ==========================================
# 📊 BOT FOYDALANUVCHILARI BAZASI
# ==========================================
ALL_USERS = set()

# ==========================================
# 📚 1. SO'ZLAR BAZASI (To'liq saqlangan)
# ==========================================
VOCABULARY_POOL = [
    "1. **Analyze** - Tahlil qilmoq\n2. **Beneficial** - Foydali\n3. **Challenge** - Qiyinchilik\n4. **Develop** - Rivojlantirmoq\n5. **Essential** - Juda muhim",
    "1. **Achieve** - Erishmoq\n2. **Improve** - Yaxshilamoq\n3. **Success** - Muvaffaqiyat\n4. **Experience** - Tajriba\n5. **Support** - Qo'llab-quvvatlamoq",
    "1. **Accurate** - Aniq, xatosiz\n2. **Blame** - Ayblamoq\n3. **Consequences** - Oqibatlar\n4. **Delay** - Kechiktirmoq\n5. **Encourage** - Ruhlantirmoq"
]

COMP_ADJECTIVES = ["Advanced", "Basic", "Critical", "Dynamic", "Efficient", "Fundamental", "Global", "Intense", "Logical", "Modern", "Strategic", "Technical", "Universal", "Vital", "Creative"]
COMP_NOUNS = ["Analysis", "Concept", "Development", "Strategy", "System", "Knowledge", "Process", "Method", "Structure", "Theory", "Approach", "Function", "Progress", "Solution", "Outcome"]
COMP_TRANSLATIONS = {
    "Advanced": "Kengaytirilgan", "Basic": "Boshlang'ich", "Critical": "Jiddiy/Tanqidiy", "Dynamic": "Harakatchan", 
    "Efficient": "Samarali", "Fundamental": "Asosiy", "Global": "Umumiy", "Intense": "Kuchli", 
    "Logical": "Mantiqiy", "Modern": "Zamonaviy", "Strategic": "Strategik", "Technical": "Texnikaviy", 
    "Universal": "Universal", "Vital": "Hayotiy", "Creative": "Ijodiy",
    "Analysis": "tahlil", "Concept": "tushuncha", "Development": "rivojlanish", "Strategy": "strategiya", 
    "System": "tizim", "Knowledge": "bilim", "Process": "jarayon", "Method": "usul", 
    "Structure": "tuzilma", "Theory": "nazariya", "Approach": "yondashuv", "Function": "vazifa", 
    "Progress": "o'sish", "Solution": "yechim", "Outcome": "natija"
}

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

GEN_SUBJECTS = ["The teacher", "A student", "My friend", "The director", "An engineer", "The doctor", "A worker", "The scientist", "An actor", "The pilot"]
GEN_VERBS = [
    {"inf": "write", "s": "writes", "ing": "is writing", "ed": "wrote", "v3": "written"},
    {"inf": "read", "s": "reads", "ing": "is reading", "ed": "read", "v3": "read"},
    {"inf": "create", "s": "creates", "ing": "is creating", "ed": "created", "v3": "created"},
    {"inf": "explain", "s": "explains", "ing": "is explaining", "ed": "explained", "v3": "explained"},
    {"inf": "discover", "s": "discovers", "ing": "is discovering", "ed": "discovered", "v3": "discovered"},
    {"inf": "check", "s": "checks", "ing": "is checking", "ed": "checked", "v3": "checked"}
]
GEN_OBJECTS = ["the new report", "an amazing book", "the project", "the difficult rule", "a new planet", "the system code"]

user_data = {}

def init_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "history_words": [],
            "history_grammar": [],
            "history_generated_tests": set(),
            "test_queue": [],
            "total_requested": 0,
            "state": None
        }

def get_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("📖 Yangi so'z"), types.KeyboardButton("📝 Grammatika"))
    keyboard.add(types.KeyboardButton("🧠 Test ishlash"))
    return keyboard

def get_quantity_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("5 ta"), types.KeyboardButton("10 ta"), types.KeyboardButton("15 ta"))
    keyboard.add(types.KeyboardButton("20 ta"), types.KeyboardButton("25 ta"), types.KeyboardButton("30 ta"))
    keyboard.add(types.KeyboardButton("⬅️ Orqaga"))
    return keyboard

def generate_infinite_test(user_id):
    u = user_data[user_id]
    while True:
        subj = random.choice(GEN_SUBJECTS)
        verb = random.choice(GEN_VERBS)
        obj = random.choice(GEN_OBJECTS)
        tense_type = random.randint(0, 2)
        
        if tense_type == 0:
            question = f"{subj} ___ {obj} on a regular basis."
            correct = verb["s"]
            options = [verb["inf"], verb["s"], verb["ing"], verb["ed"]]
        elif tense_type == 1:
            question = f"Look! {subj} ___ {obj} right now."
            correct = verb["ing"]
            options = [verb["s"], verb["ed"], verb["ing"], verb["inf"]]
        else:
            question = f"{subj} ___ {obj} during the last meeting."
            correct = verb["ed"]
            options = [verb["inf"], verb["s"], verb["ing"], verb["ed"]]
            
        if question not in u["history_generated_tests"]:
            u["history_generated_tests"].add(question)
            options = list(set(options))
            while len(options) < 4:
                options.append(random.choice(["done", "going", "taken", "seen"]))
            random.shuffle(options)
            correct_idx = options.index(correct)
            return {"q": question, "o": options, "c": correct_idx}

@bot.message_handler(commands=['statistika'])
def show_stats(message):
    total_users = len(ALL_USERS)
    stat_text = (
        "📊 **Bot Foydalanuvchilari Statistikasi:**\n\n"
        f"👥 Botdan foydalangan jami odamlar soni: **{total_users} ta**\n\n"
        "📱 _Eslatma: Bu ro'yxat bot ishga tushgandan boshlab hisoblanadi._"
    )
    try:
        bot.send_message(message.chat.id, stat_text, parse_mode="Markdown")
    except Exception:
        pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    init_user(user_id)
    ALL_USERS.add(user_id)
    u = user_data[user_id]
    u["state"] = None
    u["test_queue"] = []
    
    welcome_text = (
        f"Salom, {message.from_user.first_name}! 👋\n\n"
        "Milliardlab takrorlanmas testlar va yuz minglab unikal so'zlar tizimi muvaffaqiyatli yoqildi!\n"
        "Xohlagan bo'limingizni tanlang: 👇"
    )
    try:
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())
    except Exception:
        pass

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    init_user(user_id)
    ALL_USERS.add(user_id)
    u = user_data[user_id]

    try:
        if message.text == "📖 Yangi so'z":
            avail = [w for w in VOCABULARY_POOL if w not in u["history_words"]]
            if avail:
                chosen = random.choice(avail)
                u["history_words"].append(chosen)
                bot.send_message(message.chat.id, f"📚 **Yangi so'zlar:**\n\n{chosen}", parse_mode="Markdown")
            else:
                while True:
                    adj = random.choice(COMP_ADJECTIVES)
                    noun = random.choice(COMP_NOUNS)
                    phrase = f"✨ **{adj} {noun}**"
                    translation = f"Tarjimasi: *{COMP_TRANSLATIONS[adj]} {COMP_TRANSLATIONS[noun]}*"
                    full_word = f"{phrase}\n{translation}"
                    
                    if full_word not in u["history_words"]:
                        u["history_words"].append(full_word)
                        bot.send_message(message.chat.id, f"📚 **Yangi akademik ibora:**\n\n{full_word}", parse_mode="Markdown")
                        break

        elif message.text == "📝 Grammatika":
            avail = [g for g in GRAMMAR_POOL if g not in u["history_grammar"]]
            if not avail: u["history_grammar"] = []; avail = GRAMMAR_POOL
            chosen = random.choice(avail)
            u["history_grammar"].append(chosen)
            bot.send_message(message.chat.id, f"📝 **Grammatika qoidasi:**\n\n{chosen}", parse_mode="Markdown")

        elif message.text == "🧠 Test ishlash":
            bot.send_message(message.chat.id, "Nechta mutloqo yangi test ishlamoqchisiz? Tanlang: 👇", reply_markup=get_quantity_menu())

        elif message.text in ["5 ta", "10 ta", "15 ta", "20 ta", "25 ta", "30 ta"]:
            quantity = int(message.text.split()[0])
            u["test_queue"] = []
            for _ in range(quantity):
                u["test_queue"].append(generate_infinite_test(user_id))
            u["total_requested"] = quantity
            bot.send_message(message.chat.id, f"🚀 {quantity} ta mutloqo yangi, takrorlanmas test tayyorlandi! Birinchisi ketdi:", reply_markup=get_main_menu())
            send_next_queue_test(message.chat.id, user_id)

        elif message.text == "⬅️ Orqaga":
            bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=get_main_menu())
            
    except Exception:
        pass

def send_next_queue_test(chat_id, user_id):
    u = user_data[user_id]
    try:
        if not u["test_queue"]:
            bot.send_message(chat_id, "🎉 Tanlangan paketdagi barcha unikal testlarni tugatdingiz! Hech bir savol yoki javob takrorlanmadi. 🏁")
            return
        test_data = u["test_queue"].pop(0)
        current_num = u["total_requested"] - len(u["test_queue"])
        bot.send_poll(
            chat_id=chat_id,
            question=f"🧠 [Test {current_num}/{u['total_requested']}] {test_data['q']}",
            options=test_data["o"],
            type="quiz",
            correct_option_id=test_data["c"],
            is_anonymous=False
        )
    except Exception:
        pass

@bot.poll_answer_handler(func=lambda pollAnswer: True)
def handle_poll_answer(pollAnswer):
    user_id = pollAnswer.user.id
    init_user(user_id)
    try:
        if user_data[user_id]["test_queue"]:
            send_next_queue_test(user_id, user_id)
        else:
            bot.send_message(user_id, "🎉 Paketdagi barcha unikal testlarni yechib bo'ldingiz!")
    except Exception:
        pass

# 🤖 24/7 DOIM UYG'OQ SAQLASH TIZIMI (KEEP-ALIVE PINGER)
def keep_alive_ping():
    while True:
        try:
            # Har 10 daqiqada (600 soniya) o'ziga o'zi so'rov yuboradi
            time.sleep(600)
            requests.get(RENDER_APP_NAME)
        except Exception:
            pass

if __name__ == "__main__":
    import threading
    # Uyg'otib turuvchi funksiyani alohida zanjirda (thread) ishga tushirish
    threading.Thread(target=keep_alive_ping, daemon=True).start()
    
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()
    bot.infinity_polling()
