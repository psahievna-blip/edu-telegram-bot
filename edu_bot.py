import telebot
from telebot import types
from openpyxl import Workbook
import datetime
import time
import traceback

# ==================== Настройки ====================
TOKEN = "8227522229:AAGYUqDWk5YbiJoc1Jw6XEk5pj-x8FkWxRM"
bot = telebot.TeleBot(TOKEN)

# ==================== Профили ====================
user_profiles = {}
user_test_state = {}

def get_user_profile(chat_id):
    if chat_id not in user_profiles:
        user_profiles[chat_id] = {
            "name": None,
            "tests_passed": 0,
            "total_score": 0,
            "level": "Новичок 🟢",
            "current_section": "main",
            "current_topic": None
        }
    return user_profiles[chat_id]

def update_level(profile):
    score = profile["total_score"]
    if score < 3:
        profile["level"] = "Новичок 🟢"
    elif 3 <= score < 7:
        profile["level"] = "Продвинутый 🟡"
    else:
        profile["level"] = "Эксперт 🔴"

# ==================== Excel ====================
wb = Workbook()
ws = wb.active
ws.append(["ФИО", "Дата", "Тема/Тест", "Баллы"])

def save_to_excel(name, topic, score):
    ws.append([name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), topic, score])
    wb.save("edu_bot_report.xlsx")

# ==================== Лекции ====================
math_lectures = {
    "Тригонометрия": {"text": "📘 Тригонометрия: синус, косинус, тангенс, единичная окружность.", "video": "https://drive.google.com/file/d/1qoHy19c6xPzSXzQSDgbpUT0eJRwY9Eeo/view?usp=drive_link", "presentation": "https://drive.google.com/file/d/1fiKS5nOdHBx_QNllQnD1DmBtstsI13fc/view?usp=drive_link"},
    "Логарифмы": {"text": "📘 Логарифмы: определение, свойства, примеры.", "video": "https://youtu.be/example_log", "presentation": "https://drive.google.com/example_log"},
    "Показательная функция": {"text": "📘 Показательная функция: f(x)=a^x, графики, свойства.", "video": "https://youtu.be/example_exp", "presentation": "https://drive.google.com/example_exp"},
    "Производная": {"text": "📘 Производная: физический и геометрический смысл, формулы.", "video": "https://youtu.be/example_der", "presentation": "https://drive.google.com/example_der"},
    "Неопределённый интеграл": {"text": "📘 Неопределённый интеграл: первообразная функции.", "video": "https://youtu.be/example_int", "presentation": "https://drive.google.com/example_int"},
    "Определённый интеграл": {"text": "📘 Определённый интеграл: площадь под графиком функции.", "video": "https://youtu.be/example_defint", "presentation": "https://drive.google.com/example_defint"}
}

info_lectures = {
    "Антивирусная безопасность": {"text": "💻 Антивирус: виды, принципы работы, примеры.", "video": "https://share.google/CBVPlkkZiYgbzFQed", "presentation": "https://drive.google.com/drive/folders/1jYs9qzFcJGo704DBDFzL34NZV2eSvMES"},
    "Аппаратное обеспечение": {"text": "💻 CPU, RAM, HDD/SSD, ввод/вывод.", "video": "https://youtu.be/example_hw", "presentation": "https://drive.google.com/example_hw"},
    "Мобильные устройства": {"text": "💻 Смартфоны, планшеты, ОС, характеристики.", "video": "https://youtu.be/example_mobile", "presentation": "https://drive.google.com/example_mobile"},
    "Программное обеспечение": {"text": "💻 Системное и прикладное ПО, примеры.", "video": "https://youtu.be/example_software", "presentation": "https://drive.google.com/example_software"},
    "Виртуальные машины": {"text": "💻 Назначение, примеры, использование.", "video": "https://youtu.be/example_vm", "presentation": "https://drive.google.com/example_vm"},
    "Системы счисления": {"text": "💻 Двоичная, восьмеричная, шестнадцатеричная системы.", "video": "https://youtu.be/example_numsys", "presentation": "https://drive.google.com/example_numsys"}
}

# ==================== Задания ====================
assignments = {
    "Математика": {
        "Тригонометрия": "📄 Задание: решите 5 примеров на sin, cos, tan.",
        "Логарифмы": "📄 Задание: вычислите логарифмы по 5 примеров.",
        "Показательная функция": "📄 Задание: составьте таблицу значений функции f(x)=2^x.",
        "Производная": "📄 Задание: найдите производные 5 функций.",
        "Неопределённый интеграл": "📄 Задание: найдите первообразную для 5 функций.",
        "Определённый интеграл": "📄 Задание: найдите площадь под графиком функций."
    },
    "Информатика": {
        "Антивирусная безопасность": "📄 Задание: составьте таблицу видов антивирусов.",
        "Аппаратное обеспечение": "📄 Задание: определите компоненты ПК в своём устройстве.",
        "Мобильные устройства": "📄 Задание: опишите характеристики своего смартфона.",
        "Программное обеспечение": "📄 Задание: перечислите системное и прикладное ПО.",
        "Виртуальные машины": "📄 Задание: создайте заметку о назначении VM.",
        "Системы счисления": "📄 Задание: переведите числа из десятичной в двоичную систему."
    }
}

# ==================== Тест (10 вопросов) ====================
test_questions = [
    {"q": "Чему равен sin 30°?", "a": "1/2"},
    {"q": "Основное тригонометрическое тождество:", "a": "sin²x + cos²x = 1"},
    {"q": "RAM это оперативная или постоянная?", "a": "оперативная"},
    {"q": "Чему равен cos 0°?", "a": "1"},
    {"q": "log₂8 = ?", "a": "3"},
    {"q": "f(x) = 2^x, найдите f(3)", "a": "8"},
    {"q": "Производная x² равна?", "a": "2x"},
    {"q": "Неопределённый интеграл ∫2x dx равен?", "a": "x² + C"},
    {"q": "Определённый интеграл ∫₀¹ x dx равен?", "a": "0.5"},
    {"q": "CPU расшифровывается как?", "a": "центральный процессор"}
]

# ==================== Меню ====================
def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📐 Математика", "💻 Информатика")
    markup.add("📝 Онлайн тест", "📄 Задания", "📞 Обращение к преподавателю")
    markup.add("🏅 Мой уровень")
    bot.send_message(chat_id, "👋 Главное меню:", reply_markup=markup)
    get_user_profile(chat_id)["current_section"] = "main"

# ==================== Тестовые функции ====================
def send_next_question(chat_id):
    state = user_test_state[chat_id]
    if state["current"] < len(test_questions):
        question = test_questions[state["current"]]["q"]
        bot.send_message(chat_id, question)
    else:
        score = state["score"]
        profile = get_user_profile(chat_id)
        profile["tests_passed"] += 1
        profile["total_score"] += score
        update_level(profile)
        save_to_excel(profile["name"], "Онлайн тест", score)
        bot.send_message(chat_id, f"🎉 Тест завершён! Результат: {score}/{len(test_questions)}")
        del user_test_state[chat_id]

# ==================== Обработчики ====================
@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        profile = get_user_profile(message.chat.id)
        if not profile["name"]:
            msg = bot.send_message(message.chat.id, "Введите ФИО:")
            bot.register_next_step_handler(msg, get_name)
        else:
            main_menu(message.chat.id)
    except Exception as e:
        log_error(e)

def get_name(message):
    try:
        profile = get_user_profile(message.chat.id)
        profile["name"] = message.text
        bot.send_message(message.chat.id, f"Приятно познакомиться, {profile['name']}!")
        main_menu(message.chat.id)
    except Exception as e:
        log_error(e)

@bot.message_handler(func=lambda m: True)
def all_messages(message):
    try:
        chat_id = message.chat.id
        text = message.text.strip()
        profile = get_user_profile(chat_id)

        # Главное меню
        if text == "📐 Математика":
            profile["current_section"] = "Математика"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for t in math_lectures.keys():
                markup.add(t)
            markup.add("⬅️ Назад")
            bot.send_message(chat_id, "Выберите тему:", reply_markup=markup)
            return

        if text == "💻 Информатика":
            profile["current_section"] = "Информатика"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for t in info_lectures.keys():
                markup.add(t)
            markup.add("⬅️ Назад")
            bot.send_message(chat_id, "Выберите тему:", reply_markup=markup)
            return

        if text == "📝 Онлайн тест":
            user_test_state[chat_id] = {"current": 0, "score": 0}
            bot.send_message(chat_id, "📝 Онлайн тест начат!")
            send_next_question(chat_id)
            return

        if text == "📄 Задания":
            profile["current_section"] = "Задания"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("📐 Математика", "💻 Информатика")
            markup.add("⬅️ Назад")
            bot.send_message(chat_id, "Выберите направление, чтобы получить задания:", reply_markup=markup)
            return

        if text == "🏅 Мой уровень":
            bot.send_message(chat_id, f"🏅 Ваш уровень: {profile['level']}\nБаллы: {profile['total_score']}")
            return

        if text == "📞 Обращение к преподавателю":
            bot.send_message(chat_id, "Связь с преподавателем:", reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("Написать WhatsApp", url="https://wa.me/77051495296")
            ))
            return

        if text == "⬅️ Назад":
            main_menu(chat_id)
            return

        # Лекции
        lectures_dict = math_lectures if profile["current_section"] == "Математика" else info_lectures
        if text in lectures_dict:
            lecture = lectures_dict[text]
            msg = f"{lecture['text']}\n🎥 Видео: {lecture['video']}\n📄 Презентация: {lecture['presentation']}"
            bot.send_message(chat_id, msg)
            return

        # Задания
        if profile["current_section"] in ["Математика", "Информатика", "Задания"]:
            # Выбор темы для заданий
            if text in ["📐 Математика", "💻 Информатика"]:
                direction = "Математика" if text == "📐 Математика" else "Информатика"
                profile["current_section"] = direction
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for t in assignments[direction].keys():
                    markup.add(t)
                markup.add("⬅️ Назад")
                bot.send_message(chat_id, f"Выберите тему {direction} для задания:", reply_markup=markup)
                return

            # Отправка задания
            if text in assignments.get("Математика", {}) and profile["current_section"] == "Математика":
                bot.send_message(chat_id, assignments["Математика"][text])
                return
            if text in assignments.get("Информатика", {}) and profile["current_section"] == "Информатика":
                bot.send_message(chat_id, assignments["Информатика"][text])
                return

        # Тест
        if chat_id in user_test_state:
            state = user_test_state[chat_id]
            correct = test_questions[state["current"]]["a"]
            if text.lower() == correct.lower():
                state["score"] += 1
                bot.send_message(chat_id, "✅ Верно!")
            else:
                bot.send_message(chat_id, f"❌ Неверно. Правильный ответ: {correct}")
            state["current"] += 1
            send_next_question(chat_id)
            return

        bot.send_message(chat_id, "Выберите пункт меню.")
    except Exception as e:
        log_error(e)

# ==================== Логирование ошибок ====================
def log_error(e):
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {traceback.format_exc()}\n")
    print(f"Ошибка зафиксирована: {e}")

# ==================== Запуск бота с автоперезапуском ====================
def run_bot():
    while True:
        try:
            print("Бот запущен...")
            bot.infinity_polling()
        except Exception as e:
            log_error(e)
            print("Бот перезапустится через 5 секунд...")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
