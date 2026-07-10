import os
import telebot
from telebot import types
from dotenv import load_dotenv
from ai import ask_gemini
import threading
from flask import Flask

# Pulsuz serverin botu sönülü qəbul etməməsi üçün kiçik veb-server qururuq
app = Flask('')

@app.route('/')
def home():
    return "UNEC Smart Library AI Aktivdir! 🚀"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Lokal testlər üçün .env yükləyirik
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Əgər .env yoxdursa (serverdə olduqda), birbaşa sistemdən oxu
if not BOT_TOKEN:
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📚 Kitab Tövsiyəsi")
    btn2 = types.KeyboardButton("😊 Mood-a Uyğun Kitab")
    btn3 = types.KeyboardButton("🔎 Kitab Axtar")
    btn4 = types.KeyboardButton("📖 Məqalə üçün Mənbə")
    btn5 = types.KeyboardButton("ℹ️ Kitabxana Haqqında")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "📚 **UNEC Smart Library AI**-a xoş gəlmisiniz! 👋\n\n"
        "Mən UNEC 24/7 Kitabxanasının süni intellekt köməkçisiyəm. "
        "Sizə kitab tövsiyə edə, araşdırmalarınız üçün elmi mənbələr tapa və "
        "kitabxana xidmətləri haqqında məlumat verə bilərəm.\n\n"
        "Zəhmət olmasa, aşağıdakı menyudan bir xidmət seçin və ya birbaşa sualınızı yazın:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    user_text = message.text

    if user_text == "📚 Kitab Tövsiyəsi":
        msg = "Oxumaq istədiyiniz janrı yazın. Məsələn: *'Mənə biznes sahəsində 3 kitab təklif et.'*"
        bot.send_message(chat_id, msg, parse_mode="Markdown")
    elif user_text == "😊 Mood-a Uyğun Kitab":
        msg = "Hazırda özünüzü necə hiss edirsiniz? Məsələn: *'Son vaxtlar motivasiyam yoxdur'*."
        bot.send_message(chat_id, msg, parse_mode="Markdown")
    elif user_text == "🔎 Kitab Axtar":
        msg = "Axtardığınız kitabın adını və ya müəllifini yazın."
        bot.send_message(chat_id, msg)
    elif user_text == "📖 Məqalə üçün Mənbə":
        msg = "Yazdığınız məqalənin mövzusunu qeyd edin."
        bot.send_message(chat_id, msg, parse_mode="Markdown")
    elif user_text == "ℹ️ Kitabxana Haqqında":
        about_text = (
            "🏢 **UNEC 24/7 Kitabxanası**\n\n"
            "• **İş rejimi:** Günün 24 saatı, həftənin 7 günü kəsintisiz xidmət.\n"
            "• **Resurslar:** Minlərlə yerli və xarici kitablar."
        )
        bot.send_message(chat_id, about_text, parse_mode="Markdown")
    else:
        bot.send_chat_action(chat_id, 'typing')
        try:
            ai_response = ask_gemini(user_text)
            bot.send_message(chat_id, ai_response)
        except Exception as e:
            bot.send_message(chat_id, "Bağışlayın, kiçik bir xəta baş verdi.")
            print(f"AI Error: {e}")

if __name__ == "__main__":
    # Veb-serveri arxa planda başladırıq
    threading.Thread(target=run_server).start()
    print("🚀 UNEC Smart Library AI başladıldı...")
    bot.polling(none_stop=True)