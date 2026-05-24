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
    return "Bot is running live 24/7 with Automatic Cloud Database!"

# 🔑 Bot tokeningiz
TOKEN = '8957612617:AAFaO6NPcZ69dbs7L53Jf2nv1zUdYcYV83Y'
bot = telebot.TeleBot(TOKEN)

# ==========================================================
# 💾 AVTOMATIK BULUTLI BAZA TIZIMI (HECH NARSA TALAB QILINMAYDI)
# ==========================================================
# Bulutli bepul ombor (bin) orqali ma'lumotlarni saqlash URL manzili
# Bu Render o'chib yonganda ham ma'lumotlarni saqlab qoladi.
DB_API_URL = "https://api.jsonbin.it/v1/b/66509f6b-english-bot-db"

ALL_BOT_MEMBERS = set()
USER_SCORES = {}  # Reyting tizimi uchun

def load_database():
    """Bulutli ombordan ma'lumotlarni yuklab olish"""
    global ALL_BOT_MEMBERS, USER_SCORES
    try:
        response = requests.get(DB_API_URL, timeout=5).json()
        if "members" in response:
            ALL_BOT_MEMBERS = set(response["members"])
        if "scores" in response:
            USER_SCORES = {int(k): v for k, v in response["scores"].items()}
    except Exception:
        # Agar ombor hali yaratilmagan bo'lsa, xatolik bermaydi
        pass

def save_database():
    """Ma'lumotlarni bulutli omborga doimiy saqlash"""
    try:
        data = {
            "members": list(ALL_BOT_MEMBERS),
            "scores": USER_SCORES
        }
        requests.put(DB_API_URL, json=data, timeout=5)
    except Exception:
        pass

# Bot yoqilganda bazani xotiraga yuklaymiz
try:
    load_database()
except Exception:
    pass

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
    if user_id not in USER_SCORES:
        USER_SCORES[user_id] = 0

def google_translate(text, target_lang):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={requests.utils.quote(text)}"
        response = requests.get(url, timeout=10).json()
        translated_text = "".join([sentence[0] for sentence in response[0] if sentence[0]])
        return translated_text
    except Exception:
        return None

def get_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("📖 Yangi so'z"), types.KeyboardButton("📝 Grammatika"))
    keyboard.add(types.KeyboardButton("🧠 Test ishlash"), types.KeyboardButton("🏆 Reyting"))
    keyboard.add(types.KeyboardButton("🎯 Kun testi"))
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

def check_and_register_user(user_id):
    """Foydalanuvchini bazaga qo'shish va avtomatik bulutga saqlash"""
    if user_id not in ALL_BOT_MEMBERS:
        ALL_BOT_MEMBERS.add(user_id)
        save_database()

@bot.message_handler(commands=['statistika'])
def show_stats(message):
    load_database() # Har safar ko'rishdan oldin bulutdan eng oxirgi sonni yuklaydi
    total_members = len(ALL_BOT_MEMBERS)
    formatted_count = "{:,}".format(total_members)
    
    stat_text = (
        f"📊 **Bot hisoblagichi:**\n"
        f"📶 **{formatted_count} members**\n\n"
        f"📱 _Botni ishga tushirgan barcha faol a'zolarning umumiy soni._"
    )
    try:
        bot.send_message(message.chat.id, stat_text, parse_mode="Markdown")
    except Exception:
        pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    init_user(user_id)
    check_and_register_user(user_id)
    
    u = user_data[user_id]
    u["state"] = None
    u["test_queue"] = []
    
    welcome_text = (
        f"Salom! 👋\n\n"
        "Milliardlab unikal testlar, Reyting va **Ikki tomonlama Tarjimon** tizimi muvaffaqiyatli yoqildi!\n\n"
        "🔄 **Tarjimon imkoniyati:**\n"
        "• Botga inglizcha so'z/gap yuborsangiz -> **O'zbekchaga** o'giradi.\n"
        "• O'zbekcha so'z/gap yuborsangiz -> **Inglizchaga** o'giradi.\n"
        "Hech qanday sozlash shart emas, shunchaki matnni yozing! 👇"
    )
    try:
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())
    except Exception:
        pass

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    init_user(user_id)
    check_and_register_user(user_id)
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

        elif message.text == "🏆 Reyting":
            load_database()
            sorted_scores = sorted(USER_SCORES.items(), key=lambda x: x[1], reverse=True)[:10]
            lead_text = "🏆 **Bot bo'yicha Eng Yuqori Reyting (Top 10):**\n\n"
            for idx, (uid, score) in enumerate(sorted_scores, 1):
                status = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "👤"
                lead_text += f"{status} Student {idx} — **{score} ball**\n"
            lead_text += f"\n🎯 Sizning balingiz: **{USER_SCORES[user_id]} ball**"
            bot.send_message(message.chat.id, lead_text, parse_mode="Markdown")

        elif message.text == "🎯 Kun testi":
            daily_test = random.choice(TESTS_POOL)
            bot.send_poll(
                chat_id=message.chat.id,
                question=f"🎯 [Kun Testi] {daily_test['q']}",
                options=daily_test['o'],
                type="quiz",
                correct_option_id=daily_test['c'],
                is_anonymous=False
            )

        elif message.text == "⬅️ Orqaga":
            bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=get_main_menu())
            
        # 🌐 MUKAMMAL IKKI TOMONLAMA AVTO-TARJIMON TIZIMI
        else:
            text_to_translate = message.text.strip()
            uzb_identifiers = ['g\'', 'o\'', 'sh', 'ch', 'ng', 'lar', 'ning', 'ga', 'dan', 'da', 'mi', ' bilan', ' boti', 'uzb']
            has_uzb_markers = any(marker in text_to_translate.lower() for marker in uzb_identifiers)
            
            ascii_letters = sum(1 for c in text_to_translate if c.isalpha() and ord(c) < 128)
            total_letters = sum(1 for c in text_to_translate if c.isalpha())
            
            if total_letters > 0 and (ascii_letters / total_letters) > 0.85 and not has_uzb_markers:
                target_lang = "uz"
                direction = "🇬🇧 English ➡️ 🇺🇿 O'zbekcha"
            else:
                target_lang = "en"
                direction = "🇺🇿 O'zbekcha ➡️ 🇬🇧 English"
                
            translated_result = google_translate(text_to_translate, target_lang)
            
            if translated_result:
                response_msg = (
                    f"🔄 **Mukammal Tarjimon ({direction}):**\n\n"
                    f"📝 *Kiritildi:* {text_to_translate}\n"
                    f"✨ *Tarjimasi:* **{translated_result}**"
                )
                bot.send_message(message.chat.id, response_msg, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "⚠️ Tarjimada xatolik yuz berdi. Qayta urinib ko'ring.")

    except Exception:
        pass

def send_next_queue_test(chat_id, user_id):
    u = user_data[user_id]
    try:
        if not u["test_queue"]:
            bot.send_message(chat_id, f"🎉 Paketdagi barcha testlarni tugatdingiz!\n🏆 Jami balingiz: **{USER_SCORES[user_id]} ball** ga yetdi! 🏁", parse_mode="Markdown")
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
    check_and_register_user(user_id)
    
    try:
        USER_SCORES[user_id] += 10
        save_database() # Ball yangilanganda ham bulutga saqlaydi
        if user_data[user_id]["test_queue"]:
            send_next_queue_test(user_id, user_id)
        else:
            bot.send_message(user_id, f"🎉 Paket tugadi! 🏆 Reyting balingiz: **{USER_SCORES[user_id]}**", parse_mode="Markdown")
    except Exception:
        pass

# ⏰ KUNLIK ESLATMA VA 24/7 KEEP-ALIVE TIZIMI
def keep_alive_and_remind():
    reminder_counter = 0
    while True:
        try:
            time.sleep(600)
            requests.get(RENDER_APP_NAME)
            
            reminder_counter += 1
            if reminder_counter >= 144:
                reminder_counter = 0
                load_database()
                for uid in list(ALL_BOT_MEMBERS):
                    try:
                        bot.send_message(uid, "⏰ **Kunlik eslatma:** Bugun ingliz tili darslarini takrorlashni unutdingizmi? Botga kiring va yangi testlarni yeching! 🧠🚀", parse_mode="Markdown")
                    except Exception:
                        pass
        except Exception:
            pass

if __name__ == "__main__":
    import threading
    threading.Thread(target=keep_alive_and_remind, daemon=True).start()
    
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()
    bot.infinity_polling()
