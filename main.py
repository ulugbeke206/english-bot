import telebot
import random
from telebot import types
import os
from threading import Thread
from flask import Flask

# Render port xatosini to'g'rilash uchun kichik Web-Server yaratamiz
app = Flask('')

@app.route('/')
def home():
    return "Bot muvaffaqiyatli ishlamoqda!"

def run():
    # Render avtomatik taqdim etadigan portni oladi, bo'lmasa 8080 da ishlaydi
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Botni sozlash
TOKEN = '8957612617:AAFomuLCeWizMIywQX_8UjK6IG0FopUsaQY'
bot = telebot.TeleBot(TOKEN)

# Ma'lumotlar bazasi (Darslar va testlar)
LESSONS = {
    "vocabulary": (
        "📚 **Bugungi yangi so'zlar:**\n\n"
        "1. **Analyze** - Tahlil qilmoq\n"
        "2. **Beneficial** - Foydali\n"
        "3. **Challenge** - Qiyinchilik/Chaqiriq\n"
        "4. **Develop** - Rivojlantirmoq\n"
        "5. **Essential** - Juda muhim\n\n"
        "💡 *Ushbu so'zlarni yodlang va gaplar tuzishga harakat qiling!*"
    ),
    "grammar": (
        "✍️ **Present Perfect Tense (Yaqinda tugagan zamon):**\n\n"
        "Formula: `Subject + have/has + V3 (past participle)`\n\n"
        "📌 **Misollar:**\n"
        "• I **have lost** my keys. (Kalitlarimni yo'qotib qo'ydim).\n"
        "• She **has already finished** her homework. (U vazifasini bajarib bo'ldi).\n\n"
        "⚠️ *Eslatma: 'Has' faqat He, She, It uchun ishlatiladi.*"
    )
}

QUIZ_DATA = [
    {
        "question": "1. 'Essential' so'zining to'g'ri tarjimasi nima?",
        "options": ["Foydali", "Juda muhim", "Rivojlanish", "Tahlil qilmoq"],
        "correct": "Juda muhim"
    },
    {
        "question": "2. Choose the correct form: 'He ___ just arrived.'",
        "options": ["have", "has", "is", "was"],
        "correct": "has"
    },
    {
        "question": "3. 'Analyze' so'zining o'zbekcha ma'nosini toping:",
        "options": ["Gapirmoq", "Tahlil qilmoq", "Tushunmoq", "Yozmoq"],
        "correct": "Tahlil qilmoq"
    }
]

# Asosiy menyu tugmalari
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📖 Leksika (New Words)")
    btn2 = types.KeyboardButton("📝 Grammatika")
    btn3 = types.KeyboardButton("🧠 Testni boshlash")
    markup.add(btn1, btn2, btn3)
    return markup

# /start buyrug'i
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"Salom, {message.from_user.first_name}! 👋\n"
        "Ingliz tilini o'rganish botiga xush kelibsiz.\n"
        "Quyidagi tugmalardan birini tanlang va darsni boshlang 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard())

# Oddiy xabarlarni tutish
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    if message.text == "📖 Leksika (New Words)":
        bot.send_message(message.chat.id, LESSONS["vocabulary"], parse_mode="Markdown")
        
    elif message.text == "📝 Grammatika":
        bot.send_message(message.chat.id, LESSONS["grammar"], parse_mode="Markdown")
        
    elif message.text == "🧠 Testni boshlash":
        quiz = random.choice(QUIZ_DATA)
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for option in quiz["options"]:
            is_correct = "yes" if option == quiz["correct"] else "no"
            btn = types.InlineKeyboardButton(option, callback_data=f"quiz_{is_correct}_{quiz['correct']}")
            markup.add(btn)
            
        bot.send_message(message.chat.id, quiz["question"], reply_markup=markup)
        
    else:
        bot.send_message(message.chat.id, "Iltimos, menyudagi tugmalardan birini bosing.", reply_markup=main_keyboard())

# Inline tugmalar uchun tekshirgich
@bot.callback_query_handler(func=lambda call: call.data.startswith('quiz_'))
def check_quiz_answer(call):
    data_parts = call.data.split('_')
    status = data_parts[1]
    correct_answer = data_parts[2]
    
    if status == "yes":
        bot.answer_callback_query(call.id, "To'g'ri! Barakalla! 🎉", show_alert=True)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=f"{call.message.text}\n\n✅ **Siz to'g'ri javob berdingiz!**", parse_mode="Markdown")
    else:
        bot.answer_callback_query(call.id, f"Noto'g'ri! ❌ To'g'ri javob: {correct_answer}", show_alert=True)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=f"{call.message.text}\n\n❌ **Xato javob berdingiz.**\nTo'g'ri javob: *{correct_answer}*", parse_mode="Markdown")

# Botni uzluksiz va veb-server bilan birga ishlatish
if __name__ == '__main__':
    keep_alive()  # Kichik veb-serverni parallel ravishda ishga tushiradi
    bot.infinity_polling()
