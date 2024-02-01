import os
import time
import telebot
import nltk
import ResponseGenerator
import properties
# import yt_dlp
# from pydub import AudioSegment
import YouTubeDownloader
from Transcriber import Transcriber
import Resources
import AudioCreater

nltk.download('punkt')

audio_segments = []
API_BOT = properties.telegram_bot_api
bot = telebot.TeleBot(API_BOT)
processing_states = {}
generating_states = {}
global_generated_text = {}


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, Resources.welcome_text)


@bot.message_handler(func=lambda message: True)
def send_link(message):
    chat_id = message.chat.id
    if chat_id in processing_states and processing_states[chat_id]:
        bot.send_message(chat_id, Resources.wait_before_start_again)
    else:
        processing_states[chat_id] = True
        link = message.text
        generate_answer(message, link)


def split_text(text, max_length):
    chunks = []
    while len(text) > max_length:
        chunk = text[:max_length]
        chunks.append(chunk)
        text = text[max_length:]
    chunks.append(text)
    return chunks


def send_text(message, list_of_transcribed_text):
    for chunk in list_of_transcribed_text:
        bot.send_message(message.chat.id, chunk)


def processing_text(list_of_transcribed_text):
    if len(list_of_transcribed_text) == 1:
        text = list_of_transcribed_text.pop()
        response = ResponseGenerator.ResponseGenerator.generate_response(text)
        return response
    else:
        count_response = 0
        content = 'Write a brief summary of the content of this video.'
        max_tokens = int(4096 / len(list_of_transcribed_text))
        summarize_text = ''
        exit_loop = False

        while not exit_loop:
            while list_of_transcribed_text:
                chunk = list_of_transcribed_text.pop(0)
                if len(chunk) > 0:
                    if count_response == 3:
                        count_response = 0
                        time.sleep(60)  # Free version GPT not allowed many request per min
                    response = ResponseGenerator.ResponseGenerator.generate_response(chunk, max_tokens, content)
                    print(response)
                    summarize_text += response + ' '
                    count_response += 1

                if len(nltk.word_tokenize(summarize_text)) <= 4096 and not list_of_transcribed_text:
                    exit_loop = True
                    break

                if len(nltk.word_tokenize(summarize_text)) > 4096 and not list_of_transcribed_text:
                    list_of_transcribed_text = split_text(summarize_text, max_length=4096)
                    break
        return summarize_text


@bot.callback_query_handler(func=lambda call: True)
def handle_button_press(call):
    if call.data == 'gen_bot_answer':
        bot.answer_callback_query(call.id, Resources.generation_started)
        generate_short_answer(call.message)
        bot.delete_message(call.message.chat.id, call.message.message_id)


def generate_short_answer(message):
    chat_id = message.chat.id
    if chat_id in generating_states and generating_states[chat_id]:
        bot.send_message(chat_id, Resources.wait_for_the_previous_text_to_be_processed)
    else:
        generating_states[chat_id] = True
        bot.send_message(chat_id, Resources.processed_GPT_text)
        list_of_transcribed_text = global_generated_text[chat_id]
        response = processing_text(list_of_transcribed_text)
        send_text(message, split_text(response, max_length=4096))
        generating_states[chat_id] = False


def generate_answer(message, video_url):
    chat_id = message.chat.id
    bot.send_message(message.chat.id, Resources.processing_text_from_video_has_started)
    audio_path = YouTubeDownloader.download_audio_from_youtube(video_url)

    if audio_path:
        # Create audio chunks
        audio_chunks = AudioCreater.create_audio_chunks(audio_path, chunk_duration=10)

        transcriber = Transcriber()
        transcribed_text = ""

        for chunk_path in audio_chunks:
            chunk_text = transcriber.transcribe(chunk_path)
            if chunk_text == '400':
                bot.send_message(chat_id, Resources.an_error_occurred_while_reading_the_text_please_try_again)
                os.remove(chunk_path)
                return

            transcribed_text += chunk_text + " "

            os.remove(chunk_path)

        bot.send_message(chat_id, Resources.video_content_on_youtube)
        list_of_transcribed_text = split_text(transcribed_text, max_length=4096)
        send_text(message, list_of_transcribed_text)
        global_generated_text[chat_id] = list_of_transcribed_text

        if chat_id in generating_states and generating_states[chat_id]:
            bot.send_message(chat_id, Resources.wait_for_the_previous_text_to_be_processed)
        else:
            keyboard = telebot.types.InlineKeyboardMarkup()
            button_gen_bot_answer = telebot.types.InlineKeyboardButton(text='Generate',
                                                                       callback_data='gen_bot_answer')
            keyboard.add(button_gen_bot_answer)
            bot.send_message(message.chat.id, Resources.click_the_button_to_generate_a_video_summary,
                             reply_markup=keyboard)

    processing_states[chat_id] = False


bot.polling()
