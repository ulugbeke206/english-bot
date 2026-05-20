import os
from flask import Flask
import telebot
from telebot import types

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running live!"

# Amaldagi bot tokeningiz
TOKEN = '8957612617:AAFaO6NPcZ69dbs7L53Jf2nv1zUdYcYV83Y'
bot = telebot.TeleBot(TOKEN)

# 📚 TARTIBLI DARSLAR RO'YXATI
LESSONS_DATABASE = [
    {
        "lesson_num": 1,
        "word": "📚 **1-DARS: Yangi so'zlar (Vocabulary):**\n\n1. **Analyze** - Tahlil qilmoq\n2. **Beneficial** - Foydali\n3. **Challenge** - Qiyinchilik\n4. **Develop** - Rivojlantirmoq\n5. **Essential** - Juda muhim",
        "grammar": "📝 **1-DARS: Grammatika (Present Simple Tense):**\n\nFormula: `Subject + V1 (s/es)`\n\n📌 Doimiy odatlar va umumiy haqiqatlar uchun.\n• _Example:_ He plays football every Sunday. (U har yakshanba futbol o'ynaydi).",
        "test_question": "🧠 [1-Dars Testi] She ___ to school every day.",
        "test_options": ["go", "goes", "going", "gone"],
        "correct_index": 1
    },
    {
        "lesson_num": 2,
        "word": "📚 **2-DARS: Yangi so'zlar (Vocabulary):**\n\n1. **Achieve** - Erishmoq\n2. **Improve** - Yaxshilamoq\n3. **Success** - Muvaffaqiyat\n4. **Experience** - Tajriba\n5. **Support** - Qo'llab-quvvatlamoq",
        "grammar": "📝 **2-DARS: Grammatika (Present Perfect Tense):**\n\nFormula: `Subject + have/has + V3`\n\n📌 Yaqinda tugagan va natijasi hozir ko'rinib turgan ishlar uchun.\n• _Example:_ I have lost my keys. (Kalitlarimni yo'qotib qo'ydim).",
        "test_question": "🧠 [2-Dars Testi] What is the past tense of the verb 'BUY'?",
        "test_options": ["Buyed", "Bought", "Brought", "Buying"],
        "correct_index": 1
    },
    {
        "lesson_num": 3,
        "word": "📚 **3-DARS: Yangi so'zlar (Vocabulary):**\n\n1. **Accurate** - Aniq, xatosiz\n2. **Blame** - Ayblamoq\n3. **Consequences** - Oqibatlar\n4. **Delay** - Kechiktirmoq\n5. **Encourage** - Ruhlantirmoq",
        "grammar": "📝 **3-DARS: Grammatika (Past Simple Tense):**\n\nFormula: `Subject + V2 / V-ed`\n\n📌 O'tmishda tugagan aniq harakatlar uchun.\n• _Example:_ They went to London last year. (Ular o'tgan yili Londonga ketishdi).",
        "test_question": "🧠 [3-Dars Testi] 'Encourage' so'zining to'g'ri tarjimasini toping:",
        "test_options": ["Ruhlantirmoq", "Kechikmoq", "Taqiqmoq", "Ayblash"],
        "correct_index": 0
    },
    {
        "lesson_num": 4,
        "word": "📚 **4-DARS: Yangi so'zlar (Vocabulary):**\n\n1. **Frequent** - Tez-tez bo'ladigan\n2. **Generous** - Saxiy, qo'li ochiq\n3. **Hesitate** - Ikklanmoq\n4. **Influence** - Ta'sir ko'rsatmoq\n5. **Maintain** - Saqlamoq (holatni)",
        "grammar": "📝 **4-DARS: Grammatika (Future Simple Tense):**\n\nFormula: `Subject + will + V1`\n\n📌 Kelajakdagi va'dalar yoki qarorlar uchun.\n• _Example:_ I will call you tomorrow. (Sizga ertaga telefon qilaman).",
        "test_question": "🧠 [4-Dars Testi] Which word means 'Saxiy / Qo'li ochiq'?",
        "test_options": ["Greedy", "Generous", "Frequent", "Hesitate"],
        "correct_index": 1
    },
    {
        "lesson_num": 5,
        "word": "📚 **5-DARS: Yangi so'zlar (Vocabulary):**\n\n1. **Predict** - Bashorat qilmoq\n2. **Reject** - Rad etmoq\n3. **Valuable** - Qadrli, qimmatli\n4. **Vast** - Ulkan, keng\n5. **Wealth** - Boylik, farovonlik",
        "grammar": "📝 **5-DARS: Grammatika (Present Continuous Tense):**\n\nFormula: `Subject + am/is/are + V-ing`\n\n📌 Ayni damda sodir bo'layotgan jarayonlar uchun.\n• _Example:_ I am studying English right now. (Men hozir ingliz tilini o'rganyapman).",
        "test_question": "🧠 [5-Dars Testi] Look! The birds ___ in the sky right now.",
        "test_options": ["flies", "are flying", "flew", "fly"],
        "correct_index": 1
    }
]

# FOYDALANUVCHINING JORIY DARSI VA TARIXINI SAQLASH
user_lessons = {}

def get_current_lesson(user_id):
    # Agar foydalanuvchi yangi bo'lsa, uni 1-darsga biriktiramiz (indeks: 0)
    if user_id not in user_lessons:
        user_lessons[user_id] = 0
    
    current_index = user_lessons[user_id]
    
    # Agar barcha darslar tugagan bo'lsa, qaytadan 1-darsga qaytaramiz (aylanma tizim)
    if current_index >= len(LESSONS_DATABASE):
        user_lessons[user_id] = 0
        current_index = 0
        
    return LESSONS_DATABASE[current_index]

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
    user_lessons[user_id] = 0 # 1-darsdan boshlash
    
    welcome_text = (
        f"Salom, {message.from_user.first_name}! 👋\n\n"
        "Bot mutlaqo yangilandi! Endi tizim tartibli darslik formatida ishlaydi.\n"
        "Siz joriy darsning so'zlari va grammatikasini o'rganib, **Test ishlash** tugmasini "
        "bossangizgina, tizim sizni keyingi darsga o'tkazadi. Eskilari umuman qaytarilmaydi! 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    current_lesson = get_current_lesson(user_id)
    
    if message.text == "📖 Yangi so'z":
        bot.send_message(message.chat.id, current_lesson["word"], parse_mode="Markdown")
        
    elif message.text == "📝 Grammatika":
        bot.send_message(message.chat.id, current_lesson["grammar"], parse_mode="Markdown")
        
    elif message.text == "🧠 Test ishlash":
        # Viktorina (Poll) yuboramiz
        bot.send_poll(
            chat_id=message.chat.id,
            question=current_lesson["test_question"],
            options=current_lesson["test_options"],
            type="quiz",
            correct_option_id=current_lesson["correct_index"],
            is_anonymous=False
        )
        
        # 🔥 TESTGA JAVOB BERILGANI UCHUN FOYDALANUVCHINI KEYINGI DARSGA O'TKAZAMIZ
        user_lessons[user_id] += 1
        
        # Keyingi dars yuklanganini bildirish uchun kichik xabar
        next_lesson = get_current_lesson(user_id)
        bot.send_message(
            message.chat.id, 
            f"✅ Test yuborildi! Siz muvaffaqiyatli keyingi darsga o'tdingiz. "
            f"Endi menyu tugmalarini bossangiz, yangi dars ma'lumotlari chiqadi."
        )

if __name__ == "__main__":
    import threading
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()
    
    print("Bot is starting polling...")
    bot.infinity_polling()
