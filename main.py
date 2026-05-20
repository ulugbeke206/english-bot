import os
import random
from flask import Flask
import telebot
from telebot import types

# Flask veb-server yaratamiz (Render port xatosi bermasligi uchun)
app = Flask(__main__)

@app.route('/')
def home():
    return "Bot is running live!"

# 👇 DIQQAT: O'sha nusxalab olgan tokeningizni aynan mana shu qo'shtirnoq ichiga joylashtiring!
TOKEN = '8957612617:AAFaO6NPcZ69dbs7L53Jf2nv1zUdYcYV83Y'
bot = telebot.TeleBot(TOKEN)

# Testlar bazasi
TESTS = [
    {
        "question": "Choose the correct form:\nShe ___ to school every day.",
        "options": ["go", "goes", "going", "gone"],
        "correct": "goes"
    },
    {
        "question": "What is the past tense of 'BUY'?",
        "options": ["bought", "buyed", "brought", "buying"],
        "correct": "bought"
    }
]

# Bosh menyu tugmalari
def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_lexica = types.KeyboardButton("📖 Leksika (New Words)")
    btn_grammar = types.KeyboardButton("📝 Grammatika")
    btn_test = types.KeyboardButton("🧠 Testni boshlash")
    keyboard.add(btn_lexica, btn_grammar)
    keyboard.add(btn_test)
    return keyboard

# /start buyrug'i
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"Salom, {message.from_user.first_name}! 👋\n"
        "Ingliz tilini o'rganish botiga xush kelibsiz.\n"
        "Quyidagi tugmalardan birini tanlang va darsni boshlang 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

# Matnli xabarlarni va tugmalarni tutish
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    if message.text == "📖 Leksika (New Words)":
        lexica_text = (
            "📚 Bugungi yangi so'zlar:**\n\n"
            "1. **Achieve - Erishmoq (yutuqqa)\n"
            "2. Challenge - Qiyinchilik, chaqiriq\n"
            "3. Improve - Rivojlantirmoq, yaxshilamoq\n"
            "4. Success - Muvaffaqiyat\n"
            "5. Experience - Tajriba"
        )
        bot.send_message(message.chat.id, lexica_text, parse_mode="Markdown")
        
    elif message.text == "📝 Grammatika":
        grammar_text = (
            "✍️ **Present Perfect Tense (Yaqinda tugagan zamon):**\n\n"
            "Formula: Subject + have/has + V3 (past participle)\n\n"
            "📌 **Misollar:**\n"
            "• I have lost my keys. (Kalitlarimni yo'qotib qo'ydim).\n"
            "• She has already finished her homework. (U vazifasini bajarib bo'ldi).\n\n"
            "⚠️ Eslatma: 'Has' faqat He, She, It uchun ishlatiladi."
        )
        bot.send_message(message.chat.id, grammar_text)
        
    elif message.text == "🧠 Testni boshlash":
        test = random.choice(TESTS)
        options_text = "\n".join([f"- {opt}" for opt in test["options"]])
        test_text = f"🧠 **Savol:**\n{test['question']}\n\n**Variantlar:**\n{options_text}\n\n*To'g'ri javobni o'zingiz tekshiring: {test['correct']}*"
        bot.send_message(message.chat.id, test_text)

# Serverni va botni orqa fonda birga yurgizish qismi
if name == "main":
    import threading
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()
    
    print("Bot is starting polling...")
    bot.infinity_polling()
