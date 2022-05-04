# pip install pyTelegramBotAPI
import telebot, requests
from datetime import datetime
from telebot import types

TOKEN = "5332736580:AAFiURw-cu4wob6tG6drrOEAR0q80SLl4kA"
bot = telebot.TeleBot(token = TOKEN, threaded = False)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

bot.infinity_polling()