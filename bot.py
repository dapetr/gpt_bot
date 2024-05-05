import telebot
import logging
from config import LOGS, COUNT_LAST_MSG
from creds import get_bot_token
from telebot import types
from gpt import *
from database import *
from limit import *
from stt import *
from tts import *


logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")


bot = telebot.TeleBot(get_bot_token())


def menu_keyboard(options: list) -> types.ReplyKeyboardMarkup:
    buttons = (types.KeyboardButton(text=option) for option in options)
    keyboard = types.ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    keyboard.add(*buttons)
    return keyboard


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    logging.debug(f"User {user_id} started the bot")
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id, f"Привет, {user_name}! Я бот озвучки текста с помощью SpeechKit. Отправь мне голосовое сообщение или текст, и я тебе отвечу!",
                     reply_markup=menu_keyboard(["/help"]))


@bot.message_handler(commands=["help"])
def help_message(message):
    logging.debug(f"User {message.from_user.id} asked the bot for help")
    bot.send_message(message.chat.id,
                     text=f"/tts - начать генерацию соо в аудио.\n"
                          f"/stt - начать генерацию аудио в соо."
                     )


@bot.message_handler(commands=['debug'])
def debug(message):
    with open("logs.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):
    user_id = message.from_user.id
    try:

        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return

        stt_blocks, error_message = is_stt_block_limit(user_id, message.voice.duration)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)

        status_stt, stt_text = speech_to_text(file)
        if not status_stt:
            bot.send_message(user_id, stt_text)
            return

        add_message(user_id=user_id, full_message=[stt_text, 'user', 0, 0, stt_blocks])

        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer

        tts_symbols, error_message = is_tts_symbol_limit(user_id, answer_gpt)
        add_message(user_id=user_id, full_message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])
        if error_message:
            bot.send_message(user_id, error_message)
            return

        status_tts, voice_response = text_to_speech(answer_gpt)
        if not status_tts:
            bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)
        else:
            bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)

    except Exception as e:
        logging.error(e)
        bot.send_message(user_id, "Не получилось ответить. Попробуй записать другое сообщение")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        user_id = message.from_user.id

        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return

        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id=user_id, full_message=full_user_message)

        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)

        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)

        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return

        total_gpt_tokens += tokens_in_answer

        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        add_message(user_id=user_id, full_message=full_gpt_message)

        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")


# обрабатываем все остальные типы сообщений
@bot.message_handler(func=lambda: True)
def handler(message):
    bot.send_message(message.from_user.id, "Отправь мне голосовое или текстовое сообщение, и я тебе отвечу")


if __name__ == "__main__":
    create_database()
    bot.infinity_polling()
