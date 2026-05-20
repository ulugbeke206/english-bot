import telebot
import random
from telebot import types
import os
from threading import Thread
import random
from flask import Flask
import telebot
from telebot import types

# Render port xatosini to'g'rilash uchun kichik Web-Server yaratamiz
app = Flask('')
# Flask veb-server yaratamiz (Render port xatosi bermasligi uchun)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot muvaffaqiyatli ishlamoqda!"
    return "Bot is running live!"

def run():
    # Render avtomatik taqdim etadigan portni oladi, bo'lmasa 8080 da ishlaydi
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Botni sozlash
TOKEN = '8957612617:AAFomuLCeWizMIywQX_8UjK6IG0FopUsaQY'
# Telegram Bot Token (Sizning shaxsiy tokeningiz)
TOKEN = '8957612617:AAfomulCeWizMIywQX_8UjK6IG0FopUsaQY'
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
# Testlar bazasi (Siz xohlagancha test qo'shishingiz mumkin)
TESTS = [
    {
        "question": "Choose the correct form:\nShe ___ to school every day.",
        "options": ["go", "goes", "going", "gone"],
        "correct": "goes"
    },
    {
        "question": "1. 'Essential' so'zining to'g'ri tarjimasi nima?",
        "options": ["Foydali", "Juda muhim", "Rivojlanish", "Tahlil qilmoq"],
        "correct": "Juda muhim"
        "question": "What is the past tense of 'BUY'?",
        "options": ["bought", "buyed", "brought", "buying"],
        "correct": "bought"
    },
    {
        "question": "2. Choose the correct form: 'He ___ just arrived.'",
        "options": ["have", "has", "is", "was"],
        "correct": "has"
        "question": "Complete the sentence:\nI have ___ my homework.",
        "options": ["do", "did", "done", "doing"],
        "correct": "done"
    },
    {
        "question": "3. 'Analyze' so'zining o'zbekcha ma'nosini toping:",
        "options": ["Gapirmoq", "Tahlil qilmoq", "Tushunmoq", "Yozmoq"],
        "correct": "Tahlil qilmoq"
        "question": "Which one is a synonym for 'BEAUTIFUL'?",
        "options": ["ugly", "pretty", "sad", "angry"],
        "correct": "pretty"
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
# Har bir foydalanuvchining joriy javobini saqlab turish uchun lug'at
user_correct_answers = {}

# Bosh menyu tugmalari
def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_lexica = types.KeyboardButton("📖 Leksika (New Words)")
    btn_grammar = types.KeyboardButton("📝 Grammatika")
    btn_test = types.KeyboardButton("🧠 Testni boshlash")
    keyboard.add(btn_lexica, btn_grammar)
    keyboard.add(btn_test)
    return keyboard

# Tasodifiy test yuborish funksiyasi
def send_random_test(chat_id):
    test = random.choice(TESTS)
    
    # Foydalanuvchi qaysi javobni tanlashi kerakligini eslab qolamiz
    user_correct_answers[chat_id] = test["correct"]
    
    # Variantlar uchun tugmalar yaratamiz (Inline tugmalar)
    keyboard = types.InlineKeyboardMarkup()
    for option in test["options"]:
        keyboard.add(types.InlineKeyboardButton(text=option, callback_data=option))
        
    bot.send_message(chat_id, test["question"], reply_markup=keyboard)

# /start buyrug'i
@bot.message_handler(commands=['start'])
@@ -81,48 +74,64 @@ def send_welcome(message):
        "Ingliz tilini o'rganish botiga xush kelibsiz.\n"
        "Quyidagi tugmalardan birini tanlang va darsni boshlang 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard())
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

# Oddiy xabarlarni tutish
# Matnli xabarlarni tutish (Menyu tugmalari bosilganda)
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    if message.text == "📖 Leksika (New Words)":
        bot.send_message(message.chat.id, LESSONS["vocabulary"], parse_mode="Markdown")
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
        bot.send_message(message.chat.id, LESSONS["grammar"], parse_mode="Markdown")
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
        quiz = random.choice(QUIZ_DATA)
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for option in quiz["options"]:
            is_correct = "yes" if option == quiz["correct"] else "no"
            btn = types.InlineKeyboardButton(option, callback_data=f"quiz_{is_correct}_{quiz['correct']}")
            markup.add(btn)
            
        bot.send_message(message.chat.id, quiz["question"], reply_markup=markup)
        bot.send_message(message.chat.id, "🚀 Test rejimi faollashdi! Savollarga javob bering:")
        send_random_test(message.chat.id)

# Test javoblari bosilganda ishlaydigan qism (Callback query)
@bot.callback_query_handler(func=lambda call: True)
def handle_test_answer(call):
    chat_id = call.message.chat.id
    user_answer = call.data
    correct_answer = user_correct_answers.get(chat_id)

    # Eski inline tugmalarni o'chirib tashlaymiz (foydalanuvchi qayta bosa olmasligi uchun)
    bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)

    if correct_answer:
        if user_answer == correct_answer:
            bot.send_message(chat_id, "✅ To'g'ri topdingiz! Baranvallo! 🎉")
        else:
            bot.send_message(chat_id, f"❌ Xato! To'g'ri javob: **{correct_answer}** edi. 😔", parse_mode="Markdown")

        # SIZ AYTGAN ASOSIY JOYI: Javob bergandan keyin srazu keyingi testni yuboramiz!
        send_random_test(chat_id)
    else:
        bot.send_message(message.chat.id, "Iltimos, menyudagi tugmalardan birini bosing.", reply_markup=main_keyboard())
        bot.send_message(chat_id, "Bu test muddati o'tgan. Iltimos, menyudan yangi test boshlang.")

# Inline tugmalar uchun tekshirgich
@bot.callback_query_handler(func=lambda call: call.data.startswith('quiz_'))
def check_quiz_answer(call):
    data_parts = call.data.split('_')
    status = data_parts[1]
    correct_answer = data_parts[2]
# Serverni yuritish qismi
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    # Render'da orqada bot ishlab turishi uchun Flask'ni alohida torda emas, botni pooling rejimida yurgizamiz
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()

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
    print("Bot is starting polling...")
    bot.infinity_polling()
