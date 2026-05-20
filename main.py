import os
import random
from flask import Flask
import telebot
from telebot import types

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running live!"

TOKEN = '8957612617:AAFaO6NPcZ69dbs7L53Jf2nv1zUdYcYV83Y'
bot = telebot.TeleBot(TOKEN)

# 1. KO'P VA XILMA-XIL SO'ZLAR BAZASI (Har safar 5 tadan har xil chiqadi)
WORDS_DATABASE = [
    "📚 **Yangi so'zlar (Vocabulary - Set 1):**\n\n1. **Analyze** - Tahlil qilmoq\n2. **Beneficial** - Foydali\n3. **Challenge** - Qiyinchilik\n4. **Develop** - Rivojlantirmoq\n5. **Essential** - Juda muhim",
    "📚 **Yangi so'zlar (Vocabulary - Set 2):**\n\n1. **Achieve** - Erishmoq\n2. **Improve** - Yaxshilamoq\n3. **Success** - Muvaffaqiyat\n4. **Experience** - Tajriba\n5. **Support** - Qo'llab-quvvatlamoq",
    "📚 **Yangi so'zlar (Vocabulary - Set 3):**\n\n1. **Accurate** - Aniq, xatosiz\n2. **Blame** - Ayblamoq\n3. **Consequences** - Oqibatlar\n4. **Delay** - Kechiktirmoq\n5. **Encourage** - Ruhlantirmoq",
    "📚 **Yangi so'zlar (Vocabulary - Set 4):**\n\n1. **Frequent** - Tez-tez bo'lib turadigan\n2. **Generous** - Saxiy, qo'li ochiq\n3. **Hesitate** - Ikklanmoq\n4. **Influence** - Ta'sir ko'rsatmoq\n5. **Maintain** - Bir xil holatda saqlamoq",
    "📚 **Yangi so'zlar (Vocabulary - Set 5):**\n\n1. **Predict** - Bashorat qilmoq\n2. **Reject** - Rad etmoq\n3. **Valuable** - Qadrli, qimmatli\n4. **Vast** - Ulkan, juda keng\n5. **Wealth** - Boylik, farovonlik"
]

# 2. CHUQQURLASHTIRILGAN GRAMMATIKA MATNLARI BAZASI
GRAMMAR_DATABASE = [
    "📝 **Grammatika (Present Simple Tense):**\n\nFormula: `Subject + V1 (s/es)`\n\n📌 We use it for daily habits and general truths.\n• _Example:_ He plays football every Sunday. (U har yakshanba futbol o'ynaydi).",
    "📝 **Grammatika (Present Perfect Tense):**\n\nFormula: `Subject + have/has + V3`\n\n📌 We use it for recent actions with a result now.\n• _Example:_ I have lost my keys. (Kalitlarimni yo'qotib qo'ydim, hozir ham yo'q).",
    "📝 **Grammatika (Past Simple Tense):**\n\nFormula: `Subject + V2 / V-ed`\n\n📌 We use it for finished actions in the past.\n• _Example:_ They went to London last year. (Ular o'tgan yili Londonga ketishdi).",
    "📝 **Grammatika (Future Simple Tense):**\n\nFormula: `Subject + will + V1`\n\n📌 We use it for future promises or instant decisions.\n• _Example:_ I will call you tomorrow. (Sizga ertaga telefon qilaman).",
    "📝 **Grammatika (Modal Verbs - Can / Could):**\n\n📌 'Can' is for present ability, 'Could' is for past ability.\n• _Example:_ She can speak three languages. (U uchta tilda gapira oladi)."
]

# 3. OSON VA TUGMALI (POLL) TESTLAR BAZASI
TESTS_DATABASE = [
    {
        "question": "🧠 [Test] She ___ to school every day. (Oson)",
        "options": ["go", "goes", "going", "gone"],
        "correct_index": 1
    },
    {
        "question": "🧠 [Test] What is the past tense of the verb 'BUY'?",
        "options": ["Buyed", "Bought", "Brought", "Buying"],
        "correct_index": 1
    },
    {
        "question": "🧠 [Test] 'Encourage' so'zining to'g'ri tarjimasini toping:",
        "options": ["Ruhlantirmoq", "Kechikmoq", "Taqiqmoq", "Ayblash"],
        "correct_index": 0
    },
    {
        "question": "🧠 [Test] Which word means 'Saxiy / Qo'li ochiq'?",
        "options": ["Greedy", "Generous", "Frequent", "Hesitate"],
        "correct_index": 1
    },
    {
        "question": "🧠 [Test] Look! The birds ___ in the sky right now.",
        "options": ["flies", "are flying", "flew", "fly"],
        "correct_index": 1
    }
]

# Siz aytgandek toza va aniq 3 ta tugmali menyu
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
    welcome_text = (
        f"Salom, {message.from_user.first_name}! 👋\n\n"
        "Ingliz tili botiga xush kelibsiz.\n"
        "Pastdagi menyudan o'zingizga kerakli bo'limni tanlang. "
        "Har safar bosganingizda mutlaqo yangi ma'lumotlar beriladi! 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    if message.text == "📖 Yangi so'z":
        # Ro'yxatdan ixtiyoriy bitta yangi to'plamni tanlaydi (hech qachon doim bir xil bo'lmaydi)
        random_word = random.choice(WORDS_DATABASE)
        bot.send_message(message.chat.id, random_word, parse_mode="Markdown")
        
    elif message.text == "📝 Grammatika":
        # Ixtiyoriy grammatik qoidani yuboradi
        random_grammar = random.choice(GRAMMAR_DATABASE)
        bot.send_message(message.chat.id, random_grammar, parse_mode="Markdown")
        
    elif message.text == "🧠 Test ishlash":
        # Ixtiyoriy oson tugmali testni (Poll) yuboradi
        test = random.choice(TESTS_DATABASE)
        bot.send_poll(
            chat_id=message.chat.id,
            question=test["question"],
            options=test["options"],
            type="quiz",
            correct_option_id=test["correct_index"],
            is_anonymous=False
        )

if __name__ == "__main__":
    import threading
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()
    
    print("Bot is starting polling...")
    bot.infinity_polling()
