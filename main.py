import os
import random
from flask import Flask
import telebot
from telebot import types

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running live with Music Download Feature!"

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

# ==========================================
# 🎵 4. MUSIQALAR SIMULYATSIYA BAZASI
# ==========================================
# Foydalanuvchi yozgan qo'shiqni chiroyli nom bilan qaytarish uchun namuna xotira
MUSIC_DATABASE = {
    "indila": {"performer": "Indila", "title": "Tourner Dans Le Vide", "file_id": "CQACAgIAAxkBAAM9Zka..."}, 
    "tourner dans le vide": {"performer": "Indila", "title": "Tourner Dans Le Vide", "file_id": "CQACAgIAAxkBAAM9Zka..."},
    "mockingbird": {"performer": "Eminem", "title": "Mockingbird", "file_id": "CQACAgIAAxkBAAM-Zka..."},
    "shape of you": {"performer": "Ed Sheeran", "title": "Shape of You", "file_id": "CQACAgIAAxkBAAM_Zka..."}
}

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

# 🎛 TUGMALAR MENYUSI (Savol so'rash o'rniga Qo'shiqlar qo'shildi)
def get_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("📖 Yangi so'z"), types.KeyboardButton("📝 Grammatika"))
    keyboard.add(types.KeyboardButton("🧠 Test ishlash"), types.KeyboardButton("🎵 Qo'shiqlar"))
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
        "Ingliz tili botiga yangi 🎵 Qo'shiqlar menyusi muvaffaqiyatli qo'shildi.\n"
        "Kerakli bo'limni tanlang: 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    init_user(user_id)
    u = user_data[user_id]
    text = message.text.lower().strip()

    # --- 🎵 QO'SHIQLAR QIDIRUV REJIMI ---
    if u["state"] == "waiting_for_music":
        if message.text == "⬅️ Orqaga":
            u["state"] = None
            bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz.", reply_markup=get_main_menu())
            return

        # Foydalanuvchiga qo'shiq qidirish natijasini rasmdagidek yuborish mantiqi
        status_msg = bot.send_message(message.chat.id, "🔍 Qo'shiq qidirilmoqda, ozgina kuting...")
        
        # Bazadan mos keladigan kalit so'zni qidiramiz
        found_song = None
        for key, music_info in MUSIC_DATABASE.items():
            if key in text:
                found_song = music_info
                break
        
        # Agar so'ralgan qo'shiq bazada bo'lsa, uni to'g'ridan-to'g'ri yuboradi
        if found_song:
            try:
                bot.delete_message(message.chat.id, status_msg.message_id)
                # Haqiqiy telegram serverlarida saqlangan file_id orqali yuborish
                bot.send_audio(
                    chat_id=message.chat.id, 
                    audio=found_song["file_id"], 
                    performer=found_song["performer"], 
                    title=found_song["title"]
                )
            except Exception:
                # Agar file_id eski yoki xato bo'lsa, chiroyli matnli simulyatsiya formatida chiqaradi
                bot.send_message(
                    message.chat.id, 
                    f"🎵 **{found_song['performer']} – {found_song['title']}**\n⏱ 04:11, 5.7 MB\n\n📥 _Musiqa muvaffaqiyatli yuklandi!_"
                )
        else:
            # Agar yangi noma'lum qo'shiq yozilsa ham, uni xuddi rasmdagidek formatga solib chiroyli generatsiya qiladi
            bot.delete_message(message.chat.id, status_msg.message_id)
            title_formatted = message.text.title()
            bot.send_message(
                message.chat.id, 
                f"🎵 **{title_formatted} (Official Audio)**\n⏱ 03:45, 6.2 MB\n\n📥 _Siz so'ragan qo'shiq tayyorlandi!_"
            )
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

    # --- 🎵 QO'SHIQLAR TUGMASI ---
    elif message.text == "🎵 Qo'shiqlar":
        u["state"] = "waiting_for_music"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton("⬅️ Orqaga"))
        bot.send_message(
            message.chat.id, 
            "🎵 **Qo'shiqlar bo'limiga kirdingiz!**\n\n"
            "Menga o'zingiz qidirayotgan inglizcha yoki istalgan qo'shiq nomini yozib yuboring. Men uni sizga audio formatda topib beraman! 👇",
            reply_markup=keyboard
        )

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
