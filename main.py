import os
import random
from flask import Flask
import telebot
from telebot import types

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running live with Big Data!"

# Amaldagi bot tokeningiz
TOKEN = '8957612617:AAFaO6NPcZ69dbs7L53Jf2nv1zUdYcYV83Y'
bot = telebot.TeleBot(TOKEN)

# 📚 1. KATTA SO'ZLAR TO'PLAMI (Buni xohlagancha qator qo'shib ko'paytirish mumkin)
VOCABULARY_POOL = [
    "1. **Analyze** - Tahlil qilmoq\n2. **Beneficial** - Foydali\n3. **Challenge** - Qiyinchilik\n4. **Develop** - Rivojlantirmoq\n5. **Essential** - Juda muhim",
    "1. **Achieve** - Erishmoq\n2. **Improve** - Yaxshilamoq\n3. **Success** - Muvaffaqiyat\n4. **Experience** - Tajriba\n5. **Support** - Qo'llab-quvvatlamoq",
    "1. **Accurate** - Aniq, xatosiz\n2. **Blame** - Ayblamoq\n3. **Consequences** - Oqibatlar\n4. **Delay** - Kechiktirmoq\n5. **Encourage** - Ruhlantirmoq",
    "1. **Frequent** - Tez-tez bo'ladigan\n2. **Generous** - Saxiy, qo'li ochiq\n3. **Hesitate** - Ikklanmoq\n4. **Influence** - Ta'sir ko'rsatmoq\n5. **Maintain** - Saqlamoq (holatni)",
    "1. **Predict** - Bashorat qilmoq\n2. **Reject** - Rad etmoq\n3. **Valuable** - Qadrli, qimmatli\n4. **Vast** - Ulkan, keng\n5. **Wealth** - Boylik, farovonlik",
    "1. **Abolish** - Bekor qilmoq\n2. **Bargain** - Savdolashmoq\n3. **Cautious** - Ehtiyotkor\n4. **Defend** - Himoya qilmoq\n5. **Eager** - Intizor, chanqoq",
    "1. **Abundant** - Mo'l-ko'l, serob\n2. **Accumulate** - To'plamoq, yig'moq\n3. **Accuse** - Ayblamoq (sudda)\n4. **Acquire** - Ortmoq, ega bo'lmoq\n5. **Ambitious** - Shijoatli, ulkan maqsadli"
]

# 📝 2. KATTA GRAMMATIKA TO'PLAMI
GRAMMAR_POOL = [
    "**Present Simple Tense**\n\nFormula: `Subject + V1 (s/es)`\n\n📌 Doimiy odatlar uchun.\n• _Ex:_ He plays football every Sunday.",
    "**Present Perfect Tense**\n\nFormula: `Subject + have/has + V3`\n\n📌 Natijasi hozir ko'ringan ishlar uchun.\n• _Ex:_ I have lost my keys.",
    "**Past Simple Tense**\n\nFormula: `Subject + V2 / V-ed`\n\n📌 O'tmishda tugagan ishlar uchun.\n• _Ex:_ They went to London last year.",
    "**Future Simple Tense**\n\nFormula: `Subject + will + V1`\n\n📌 Kelajakdagi qarorlar uchun.\n• _Ex:_ I will call you tomorrow.",
    "**Modal Verbs - Can / Could**\n\n📌 'Can' hozirgi, 'Could' o'tmishdagi qobiliyat.\n• _Ex:_ She can speak three languages.",
    "**Present Continuous Tense**\n\nFormula: `Subject + am/is/are + V-ing`\n\n📌 Ayni damda sodir bo'layotgan jarayonlar.\n• _Ex:_ I am studying English right now.",
    "**Past Continuous Tense**\n\nFormula: `Subject + was/were + V-ing`\n\n📌 O'tmishdagi ma'lum bir vaqtda davom etgan ishlar.\n• _Ex:_ I was watching TV at 8 PM yesterday."
]

# 🧠 3. KATTA TESTLAR TO'PLAMI
TESTS_POOL = [
    {"q": "She ___ to school every day.", "o": ["go", "goes", "going", "gone"], "c": 1},
    {"q": "What is the past tense of the verb 'BUY'?", "o": ["Buyed", "Bought", "Brought", "Buying"], "c": 1},
    {"q": "'Encourage' so'zining to'g'ri tarjimasini toping:", "o": ["Ruhlantirmoq", "Kechikmoq", "Taqiqmoq", "Ayblash"], "c": 0},
    {"q": "Which word means 'Saxiy / Qo'li ochiq'?", "o": ["Greedy", "Generous", "Frequent", "Hesitate"], "c": 1},
    {"q": "Look! The birds ___ in the sky right now.", "o": ["flies", "are flying", "flew", "fly"], "c": 1},
    {"q": "Yesterday I ___ a very interesting book.", "o": ["readed", "read", "reads", "reading"], "c": 1},
    {"q": "If I have enough money, I ___ a new car next year.", "o": ["buy", "will buy", "bought", "buying"], "c": 1}
]

# FOYDALANUVCHI PROGRESINI SAQLASH
user_progress = {}

def generate_next_lesson(user_id):
    if user_id not in user_progress:
        user_progress[user_id] = {
            "lesson_count": 1,
            "history_words": [],
            "history_grammar": [],
            "history_tests": [],
            "current_lesson": None
        }
    
    u = user_progress[user_id]
    
    # 1. Takrorlanmaydigan so'z tanlash
    avail_words = [w for w in VOCABULARY_POOL if w not in u["history_words"]]
    if not avail_words: # Agar hamma hovuz tugasa, xotirani tozalaymiz
        u["history_words"] = []
        avail_words = VOCABULARY_POOL
    chosen_word = random.choice(avail_words)
    u["history_words"].append(chosen_word)
    
    # 2. Takrorlanmaydigan grammatika tanlash
    avail_grammar = [g for g in GRAMMAR_POOL if g not in u["history_grammar"]]
    if not avail_grammar:
        u["history_grammar"] = []
        avail_grammar = GRAMMAR_POOL
    chosen_grammar = random.choice(avail_grammar)
    u["history_grammar"].append(chosen_grammar)
    
    # 3. Takrorlanmaydigan test tanlash
    avail_tests = [t for t in TESTS_POOL if t["q"] not in u["history_tests"]]
    if not avail_tests:
        u["history_tests"] = []
        avail_tests = TESTS_POOL
    chosen_test = random.choice(avail_tests)
    u["history_tests"].append(chosen_test["q"])
    
    # Yangi yaxlit dars paketini yig'ish
    u["current_lesson"] = {
        "num": u["lesson_count"],
        "word_msg": f"📚 **{u['lesson_count']}-DARS: Yangi so'zlar**\n\n{chosen_word}",
        "grammar_msg": f"📝 **{u['lesson_count']}-DARS: Grammatika**\n\n{chosen_grammar}",
        "test": chosen_test
    }

def get_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_word = types.KeyboardButton("📖 Yangi so'z")
    btn_grammar = types.KeyboardButton("📝 Grammatika")
    btn_test = types.KeyboardButton("🧠 Test ishlash")
    keyboard.add(btn_word, btn_grammar)
    keyboard.add(btn_test)
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    # Foydalanuvchi ma'lumotlarini noldan ochamiz
    user_progress[user_id] = {
        "lesson_count": 1,
        "history_words": [],
        "history_grammar": [],
        "history_tests": [],
        "current_lesson": None
    }
    generate_next_lesson(user_id)
    
    welcome_text = (
        f"Salom, {message.from_user.first_name}! 👋\n\n"
        "Maksimal darslar tizimiga xush kelibsiz! Botda darslar generatsiyasi mutlaqo takrorlanmas "
        "qilib sozlangan. Har bitta testni yechganingizdan so'ng avtomatik ravishda mutlaqo yangi "
        "darsga o'tib boraverasiz. Qani boshladik! 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    
    if user_id not in user_progress or user_progress[user_id]["current_lesson"] is None:
        generate_next_lesson(user_id)
        
    current = user_progress[user_id]["current_lesson"]
    
    if message.text == "📖 Yangi so'z":
        bot.send_message(message.chat.id, current["word_msg"], parse_mode="Markdown")
        
    elif message.text == "📝 Grammatika":
        bot.send_message(message.chat.id, current["grammar_msg"], parse_mode="Markdown")
        
    elif message.text == "🧠 Test ishlash":
        test_data = current["test"]
        bot.send_poll(
            chat_id=message.chat.id,
            question=f"🧠 [{user_progress[user_id]['lesson_count']}-Dars Testi] {test_data['q']}",
            options=test_data["o"],
            type="quiz",
            correct_option_id=test_data["c"],
            is_anonymous=False
        )
        
        # KEYINGI DARSGA O'TKAZISH MANTIQI
        user_progress[user_id]["lesson_count"] += 1
        generate_next_lesson(user_id)
        
        bot.send_message(
            message.chat.id, 
            f"🎉 Zo'r! Tizim sizga {user_progress[user_id]['lesson_count']}-darsni tayyorladi. "
            "Tugmalarni bosib yangi darsni ko'rishingiz mumkin!"
        )

if __name__ == "__main__":
    import threading
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()
    
    print("Bot is starting polling...")
    bot.infinity_polling()
