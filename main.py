import os
import random
from flask import Flask
import telebot
from types import MethodType

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running live!"

TOKEN = '8957612617:AAFaO6NPcZ69dbs7L53Jf2nv1zUdYcYV83Y'
bot = telebot.TeleBot(TOKEN)

# Har bir dars (kun) uchun alohida ma'lumotlar bazasi
DAILY_LESSONS = [
    {
        "lexica": "📚 **Bugungi yangi so'zlar:**\n\n1. **Analyze** - Tahlil qilmoq\n2. **Beneficial** - Foydali\n3. **Challenge** - Qiyinchilik/Chaqiriq\n4. **Develop** - Rivojlantirmoq\n5. **Essential** - Juda muhim\n\n💡 _Ushbu so'zlarni yodlang va gaplar tuzishga harakat qiling!_",
        "grammar": "✍️ **Present Perfect Tense (Yaqinda tugagan zamon):**\n\nFormula: `Subject + have/has + V3 (past participle)`\n\n📌 **Misollar:**\n• I have lost my keys. (Kalitlarimni yo'qotib qo'ydim).\n• She has already finished her homework. (U vazifasini bajarib bo'ldi).\n\n⚠️ Eslatma: 'Has' faqat He, She, It uchun ishlatiladi.",
        "question": "3. 'Analyze' so'zining o'zbekcha ma'nosini toping:",
        "options": ["Gapirmoq", "Tahlil qilmoq", "Tushunmoq", "Yozmoq"],
        "correct_index": 1  # "Tahlil qilmoq" indeks raqami (0 dan boshlanadi)
    },
    {
        "lexica": "📚 **Bugungi yangi so'zlar:**\n\n1. **Achieve** - Erishmoq\n2. **Improve** - Yaxshilamoq\n3. **Success** - Muvaffaqiyat\n4. **Experience** - Tajriba\n5. **Support** - Qo'llab-quvvatlamoq\n\n💡 _Ushbu so'zlarni yodlang va gaplar tuzishga harakat qiling!_",
        "grammar": "✍️ **Past Simple Tense (O'tgan oddiy zamon):**\n\nFormula: `Subject + V2 / V-ed`\n\n📌 **Misollar:**\n• I watched a movie yesterday. (Kechaga kino ko'rdim).\n• They went to London last year. (Ular o'tgan yili Londonga ketishdi).",
        "question": "3. What is the past tense of the verb 'BUY'?",
        "options": ["Buyed", "Bought", "Brought", "Buying"],
        "correct_index": 1  # "Bought"
    }
]

# /start yuborilganda foydalanuvchiga srazu dars va test ketma-ket boradi
@bot.message_handler(commands=['start'])
def send_lesson(message):
    # Tasodifiy bitta dars to'plamini tanlaymiz
    lesson = random.choice(DAILY_LESSONS)
    
    # 1. Leksika qismini yuboramiz
    bot.send_message(message.chat.id, lesson["lexica"], parse_mode="Markdown")
    
    # 2. Grammatika qismini yuboramiz
    bot.send_message(message.chat.id, lesson["grammar"], parse_mode="Markdown")
    
    # 3. Haqiqiy Telegram testini (Poll) yuboramiz
    bot.send_poll(
        chat_id=message.chat.id,
        question=lesson["question"],
        options=lesson["options"],
        type="quiz",                  # Viktorina rejimi
        correct_option_id=lesson["correct_index"], # To'g'ri javob indeksi
        is_anonymous=False            # Kim nima belgilaganini ko'rish uchun
    )

if __name__ == "__main__":
    import threading
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()
    
    print("Bot is starting polling...")
    bot.infinity_polling()
