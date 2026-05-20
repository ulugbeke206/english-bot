import os
import random
from flask import Flask
import telebot
from telebot import types

# Flask veb-server yaratamiz
app = Flask(__name__)

# Telegram Bot Token (O'zingiznikini qo'ying)
TOKEN = 'BU_YERGA_O_Z_TOKENINGIZNI_QO_YING'
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
    },
    {
        "question": "Complete the sentence:\nI have ___ my homework.",
        "options": ["do", "did", "done", "doing"],
        "correct": "done"
    },
    {
        "question": "Which one is a synonym for 'BEAUTIFUL'?",
        "options": ["ugly", "pretty", "sad", "angry"],
        "correct": "pretty"
    }
]

user_correct_answers = {}

def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_lexica = types.KeyboardButton("📖 Leksika (New Words)")
    btn_grammar = types.KeyboardButton("📝 Grammatika")
    btn_test = types.KeyboardButton("🧠 Testni boshlash")
    keyboard.add(btn_lexica, btn_grammar)
    keyboard.add(btn_test)
    return keyboard

def send_random_test(chat_id):
    test = random.choice(TESTS)
    user_correct_answers[chat_id] = test["correct"]
    
    keyboard = types.InlineKeyboardMarkup()
    for option in test["options"]:
        keyboard.add(types.InlineKeyboardButton(text=option, callback_data=option))
        
    bot.send_message(chat_id, test["question"], reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"Salom, {message.from_user.first_name}! 👋\n"
        "Ingliz tilini o'rganish botiga xush kelibsiz.\n"
        "Quyidagi tugmalardan birini tanlang va darsni boshlang 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    if message.text == "📖 Leksika (New Words)":
        lexica_text = (
            "📚 **Bugungi yangi so'zlar:**\n\n"
            "1. **Achieve** - Erishmoq (yutuqqa)\n"
            "2. **Challenge** - Qiyinchilik, chaqiriq\n"
            "3. **Improve** - Rivojlantirmoq, yaxshilamoq\n"
            "4. **Success** - Muvaffaqiyat\n"
            "5. **Experience** - Tajriba"
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
        bot.send_message(message.chat.id, "🚀 Test rejimi faollashdi! Savollarga javob bering:")
        send_random_test(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def handle_test_answer(call):
    chat_id = call.message.chat.id
    user_answer = call.data
    correct_answer = user_correct_answers.get(chat_id)

    try:
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
    except:
        pass

    if correct_answer:
        if user_answer == correct_answer:
            bot.send_message(chat_id, "✅ To'g'ri topdingiz! Baranvallo! 🎉")
        else:
            bot.send_message(chat_id, f"❌ Xato! To'g'ri javob: **{correct_answer}** edi. 😔", parse_mode="Markdown")
        
        send_random_test(chat_id)
    else:
        bot.send_message(chat_id, "Bu test muddati o'tgan. Iltimos, menyudan yangi test boshlang.")

# Render birinchi bo'lib tekshiradigan asosiy sahifa
@app.route('/')
def home():
    return "Bot muvaffaqiyatli ishlayapti!"

# Bot orqa fonda xabarlarni doimiy eshitib turishi uchun funksiya
def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(none_stop=True)

# Loyiha ishga tushganda bot alohida oqimda srazu yoqiladi
import threading
threading.Thread(target=run_bot, daemon=True).start()
