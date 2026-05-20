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

# JUDAYAM KO'P VA XILMA-XIL DARSLAR BAZASI
DAILY_LESSONS = [
    {
        "lexica": "📚 **Yangi so'zlar (Vocabulary - Set 1):**\n\n1. **Analyze** - Tahlil qilmoq\n2. **Beneficial** - Foydali\n3. **Challenge** - Qiyinchilik\n4. **Develop** - Rivojlantirmoq\n5. **Essential** - Juda muhim",
        "grammar": "✍️ **Grammatika (Present Perfect Tense):**\n\nFormula: `Subject + have/has + V3`\n\n📌 **Misol:** I have lost my keys. (Kalitlarimni yo'qotib qo'ydim).",
        "question": "📝 'Analyze' so'zining o'zbekcha ma'nosini toping:",
        "options": ["Gapirmoq", "Tahlil qilmoq", "Tushunmoq", "Yozmoq"],
        "correct_index": 1
    },
    {
        "lexica": "📚 **Yangi so'zlar (Vocabulary - Set 2):**\n\n1. **Achieve** - Erishmoq\n2. **Improve** - Yaxshilamoq\n3. **Success** - Muvaffaqiyat\n4. **Experience** - Tajriba\n5. **Support** - Qo'llab-quvvatlamoq",
        "grammar": "✍️ **Grammatika (Past Simple Tense):**\n\nFormula: `Subject + V2 / V-ed`\n\n📌 **Misol:** They went to London last year. (Ular o'tgan yili Londonga ketishdi).",
        "question": "📝 What is the past tense of the verb 'BUY'?",
        "options": ["Buyed", "Bought", "Brought", "Buying"],
        "correct_index": 1
    },
    {
        "lexica": "📚 **Yangi so'zlar (Vocabulary - Set 3):**\n\n1. **Accurate** - Aniq, xatosiz\n2. **Blame** - Ayblamoq\n3. **Consequences** - Oqibatlar\n4. **Delay** - Kechiktirmoq\n5. **Encourage** - Ruhlantirmoq",
        "grammar": "✍️ **Grammatika (Future Simple Tense):**\n\nFormula: `Subject + will + V1`\n\n📌 **Misol:** I will call you tomorrow. (Sizga ertaga telefon qilaman).",
        "question": "📝 'Encourage' so'zining to'g'ri tarjimasini toping:",
        "options": ["Ruhlantirmoq", "Kechikmoq", "Taqiqmoq", "Ayblash"],
        "correct_index": 0
    },
    {
        "lexica": "📚 **Yangi so'zlar (Vocabulary - Set 4):**\n\n1. **Frequent** - Tez-tez bo'lib turadigan\n2. **Generous** - Saxiy, qo'li ochiq\n3. **Hesitate** - Ikklanmoq\n4. **Influence** - Ta'sir ko'rsatmoq\n5. **Maintain** - Bir xil holatda saqlamoq",
        "grammar": "✍️ **Grammatika (Passive Voice - Majhul nisbat):**\n\nFormula: `Subject + am/is/are + V3`\n\n📌 **Misol:** The car is washed every day. (Mashina har kuni yuviladi).",
        "question": "📝 Which word means 'Saxiy / Qo'li ochiq'?",
        "options": ["Greedy", "Generous", "Frequent", "Hesitate"],
        "correct_index": 1
    },
    {
        "lexica": "📚 **Yangi so'zlar (Vocabulary - Set 5):**\n\n1. **Predict** - Bashorat qilmoq\n2. **Reject** - Rad etmoq\n3. **Valuable** - Qadrli, qimmatli\n4. **Vast** - Ulkan, juda keng\n5. **Wealth** - Boylik, farovonlik",
        "grammar": "✍️ **Grammatika (Modal Verbs - Must vs Have to):**\n\n📌 **Qoida:** 'Must' shaxsiy majburiyat, 'Have to' esa tashqi qonun-qoidalardan kelib chiqqan majburiyat uchun ishlatiladi.",
        "question": "📝 Complete the sentence: You ___ wear a seatbelt while driving. (Law)",
        "options": ["must", "have to", "should", "might"],
        "correct_index": 1
    }
]

# Doimiy pastki menyu tugmasi
def get_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_random_lesson = types.KeyboardButton("🎲 Tasodifiy yangi dars")
    keyboard.add(btn_random_lesson)
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"Salom, {message.from_user.first_name}! 👋\n\n"
        "Ingliz tili botiga xush kelibsiz! Bu yerda so'zlar va testlar judayam ko'p.\n"
        "Har safar tugmani bosganingizda sizga mutlaqo yangi so'zlar va testlar keladi.\n\n"
        "Pastdagi tugmani bosing va o'rganishni boshlang 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

@bot.message_handler(func=lambda message: message.text == "🎲 Tasodifiy yangi dars")
def handle_random_lesson(message):
    # Har safar ro'yxat ichidan tasodifiy bittasini tanlaydi
    lesson = random.choice(DAILY_LESSONS)
    
    # 1. Leksika yuborish
    bot.send_message(message.chat.id, lesson["lexica"], parse_mode="Markdown")
    
    # 2. Grammatika yuborish
    bot.send_message(message.chat.id, lesson["grammar"], parse_mode="Markdown")
    
    # 3. Viktorina testi (Telegram Poll)
    bot.send_poll(
        chat_id=message.chat.id,
        question=lesson["question"],
        options=lesson["options"],
        type="quiz",
        correct_option_id=lesson["correct_index"],
        is_anonymous=False
    )

if __name__ == "__main__":
    import threading
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()
    
    print("Bot is starting polling...")
    bot.infinity_polling()
