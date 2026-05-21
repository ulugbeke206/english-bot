import os
import random
from flask import Flask
import telebot
from telebot import types

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running live with Multi-Quiz feature!"

# Amaldagi bot tokeningiz
TOKEN = '8957612617:AAFaO6NPcZ69dbs7L53Jf2nv1zUdYcYV83Y'
bot = telebot.TeleBot(TOKEN)

# 📚 1. KATTA SO'ZLAR TO'PLAMI
VOCABULARY_POOL = [
    "1. **Analyze** - Tahlil qilmoq\n2. **Beneficial** - Foydali\n3. **Challenge** - Qiyinchilik\n4. **Develop** - Rivojlantirmoq\n5. **Essential** - Juda muhim",
    "1. **Achieve** - Erishmoq\n2. **Improve** - Yaxshilamoq\n3. **Success** - Muvaffaqiyat\n4. **Experience** - Tajriba\n5. **Support** - Qo'llab-quvvatlamoq",
    "1. **Accurate** - Aniq, xatosiz\n2. **Blame** - Ayblamoq\n3. **Consequences** - Oqibatlar\n4. **Delay** - Kechiktirmoq\n5. **Encourage** - Ruhlantirmoq",
    "1. **Frequent** - Tez-tez bo'ladigan\n2. **Generous** - Saxiy, qo'li ochiq\n3. **Hesitate** - Ikklanmoq\n4. **Influence** - Ta'sir ko'rsatmoq\n5. **Maintain** - Saqlamoq (holatni)",
    "1. **Predict** - Bashorat qilmoq\n2. **Reject** - Rad etmoq\n3. **Valuable** - Qadrli, qimmatli\n4. **Vast** - Ulkan, keng\n5. **Wealth** - Boylik, farovonlik"
]

# 📝 2. KATTA GRAMMATIKA TO'PLAMI
GRAMMAR_POOL = [
    "**Present Simple Tense**\n\nFormula: `Subject + V1 (s/es)`\n\n📌 Doimiy odatlar uchun.\n• _Ex:_ He plays football every Sunday.",
    "**Present Perfect Tense**\n\nFormula: `Subject + have/has + V3`\n\n📌 Natijasi hozir ko'ringan ishlar uchun.\n• _Ex:_ I have lost my keys.",
    "**Past Simple Tense**\n\nFormula: `Subject + V2 / V-ed`\n\n📌 O'tmishda tugagan ishlar uchun.\n• _Ex:_ They went to London last year.",
    "**Future Simple Tense**\n\nFormula: `Subject + will + V1`\n\n📌 Kelajakdagi qarorlar uchun.\n• _Ex:_ I will call you tomorrow.",
    "**Modal Verbs - Can / Could**\n\n📌 'Can' hozirgi, 'Could' o'tmishdagi qobiliyat.\n• _Ex:_ She can speak three languages."
]

# 🧠 3. KATTA TESTLAR TO'PLAMI (Buni istagancha ko'paytirishingiz mumkin)
TESTS_POOL = [
    {"q": "She ___ to school every day.", "o": ["go", "goes", "going", "gone"], "c": 1},
    {"q": "What is the past tense of the verb 'BUY'?", "o": ["Buyed", "Bought", "Brought", "Buying"], "c": 1},
    {"q": "'Encourage' so'zining to'g'ri tarjimasini toping:", "o": ["Ruhlantirmoq", "Kechikmoq", "Taqiqmoq", "Ayblash"], "c": 0},
    {"q": "Which word means 'Saxiy / Qo'li ochiq'?", "o": ["Greedy", "Generous", "Frequent", "Hesitate"], "c": 1},
    {"q": "Look! The birds ___ in the sky right now.", "o": ["flies", "are flying", "flew", "fly"], "c": 1},
    {"q": "Yesterday I ___ a very interesting book.", "o": ["readed", "read", "reads", "reading"], "c": 1},
    {"q": "If I have enough money, I ___ a new car next year.", "o": ["buy", "will buy", "bought", "buying"], "c": 1},
    {"q": "He is interested ___ learning new languages.", "o": ["in", "on", "at", "for"], "c": 0},
    {"q": "We ___ any plans for the weekend yet.", "o": ["don't make", "haven't made", "didn't made", "hasn't made"], "c": 1},
    {"q": "This is the ___ movie I have ever watched.", "o": ["good", "better", "best", "goodest"], "c": 2}
]

# FOYDALANUVCHILAR XOTIRASI
user_data = {}

def init_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "history_words": [],
            "history_grammar": [],
            "history_tests": [],  # Umuman takrorlanmasligi uchun ko'rgan testlari ID ro'yxati
            "test_queue": [],     # Hozir ishlashi kerak bo'lgan testlar navbati
            "total_requested": 0  # Nechta test so'ragani
        }

def get_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("📖 Yangi so'z"), types.KeyboardButton("📝 Grammatika"))
    keyboard.add(types.KeyboardButton("🧠 Test ishlash"))
    return keyboard

def get_quantity_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("5 ta"), types.KeyboardButton("10 ta"))
    keyboard.add(types.KeyboardButton("15 ta"), types.KeyboardButton("20 ta"))
    keyboard.add(types.KeyboardButton("⬅️ Orqaga"))
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    init_user(user_id)
    # Start bosilganda xotirani tozalash
    user_data[user_id]["history_words"] = []
    user_data[user_id]["history_grammar"] = []
    user_data[user_id]["history_tests"] = []
    user_data[user_id]["test_queue"] = []

    welcome_text = (
        f"Salom, {message.from_user.first_name}! 👋\n\n"
        "Yangi aqlli test tizimiga xush kelibsiz!\n"
        "Endi **'Test ishlash'** tugmasini bosganingizda, o'zingizga qulay miqdorni tanlaysiz. "
        "Testlar mutlaqo aralashgan holda keladi va asosiysi — **hech qachon qaytarilmaydi**!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    init_user(user_id)
    u = user_data[user_id]

    if message.text == "📖 Yangi so'z":
        avail = [w for w in VOCABULARY_POOL if w not in u["history_words"]]
        if not avail:
            u["history_words"] = []
            avail = VOCABULARY_POOL
        chosen = random.choice(avail)
        u["history_words"].append(chosen)
        bot.send_message(message.chat.id, f"📚 **Yangi so'zlar:**\n\n{chosen}", parse_mode="Markdown")

    elif message.text == "📝 Grammatika":
        avail = [g for g in GRAMMAR_POOL if g not in u["history_grammar"]]
        if not avail:
            u["history_grammar"] = []
            avail = GRAMMAR_POOL
        chosen = random.choice(avail)
        u["history_grammar"].append(chosen)
        bot.send_message(message.chat.id, f"📝 **Grammatika qoidasi:**\n\n{chosen}", parse_mode="Markdown")

    elif message.text == "🧠 Test ishlash":
        bot.send_message(message.chat.id, "Nechta test ishlamoqchisiz? Tanlang: 👇", reply_markup=get_quantity_menu())

    elif message.text in ["5 ta", "10 ta", "15 ta", "20 ta"]:
        quantity = int(message.text.split()[0])
        
        # Foydalanuvchi hali ko'rmagan testlarni ajratib olamiz
        # Har bir test bazadagi indeksi bilan tekshiriladi
        avail_tests = [i for i, t in enumerate(TESTS_POOL) if i not in u["history_tests"]]
        
        if len(avail_tests) < quantity:
            # Agar ko'rilmagan testlar so'ralgan miqdordan kam qolgan bo'lsa, tarixni tozalab yuboramiz (Aylanma tizim)
            u["history_tests"] = []
            avail_tests = list(range(len(TESTS_POOL)))
            
        # Testlarni to'liq aralashtirib tashlaymiz
        random.shuffle(avail_tests)
        
        # Foydalanuvchi so'ragan miqdorda navbat shakllantiramiz
        u["test_queue"] = avail_tests[:quantity]
        u["total_requested"] = quantity
        
        bot.send_message(
            message.chat.id, 
            f"🚀 {quantity} ta takrorlanmas test tayyorlandi! Birinchisi ketdi:", 
            reply_markup=get_main_menu()
        )
        send_next_queue_test(message.chat.id, user_id)

    elif message.text == "⬅️ Orqaga":
        bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=get_main_menu())

def send_next_queue_test(chat_id, user_id):
    u = user_data[user_id]
    
    if not u["test_queue"]:
        bot.send_message(chat_id, "🎉 Tabriklayman! Tanlangan barcha testlarni muvaffaqiyatli tugatdingiz. 🏁")
        return

    # Navbatdan birinchi test indeksini sug'urib olamiz
    current_test_index = u["test_queue"].pop(0)
    u["history_tests"].append(current_test_index) # Uni ko'rilganlar tarixiga qo'shamiz
    
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

# Foydalanuvchi poll (viktorina)ga javob berganini kuzatish
@bot.poll_answer_handler(func=lambda wrecked: True)
def handle_poll_answer(pollAnswer):
    user_id = pollAnswer.user.id
    init_user(user_id)
    
    # Foydalanuvchi joriy test guruhini ishlayotgan bo'lsa, keyingisini yuboramiz
    if user_data[user_id]["test_queue"]:
        # Foydalanuvchining chat_id'sini aniqlash uchun uning shaxsiy ID'sidan foydalanamiz
        send_next_queue_test(user_id, user_id)
    else:
        # Agar navbatdagi oxirgi test bo'lsa va yuqoridagi funksiyada pop bo'lib bo'lingan bo'lsa
        bot.send_message(user_id, "🎉 Ushbu paketdagi barcha testlarni yechib bo'ldingiz! Yangi darslar yoki testlarni tanlashingiz mumkin.")

if __name__ == "__main__":
    import threading
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()
    
    print("Bot is starting polling with Poll-Answer Handler...")
    bot.infinity_polling()
