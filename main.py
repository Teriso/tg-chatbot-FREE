import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import g4f
from g4f.client import Client
from deep_translator import GoogleTranslator

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен телеграмм-бота
TOKEN = ''

# Выбор модели
model = "gpt-4"  # выберите модель, которую вы хотите использовать
provider = g4f.Provider.Yqcloud

# Инициализация истории сообщений
conversation_history = []

# Создание экземпляра класса Client
client = Client()

# Функция для обработки команды /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Привет! Я телеграмм-бот для общения с Чат ГПТ.')







# Функция для генерации изображений
def generate_image(prompt_en):
    response = client.images.generate(
        model="flux",
        prompt=prompt_en,

        response_format="url"

    )
    return response.data[0].url


# Функция для отправки изображений
def send_image(update, context, image_url):
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)


# Функция для обработки сообщений
def handle_message(update, context):


    message = context.bot.send_message(chat_id=update.effective_chat.id, text='⏳')
    message_id = message.message_id
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")




    global conversation_history
    user_message = update.message.text
    conversation_history.append({"role": "user", "content": user_message})
    response = g4f.ChatCompletion.create(
        model=model,
        provider=provider,
        messages=conversation_history,

    )

    if user_message.startswith("/image") or user_message.startswith("нарисуй"):

        prompt = user_message.replace("/image", "").strip()
        prompt = user_message.replace("нарисуй", "").strip()
        
        translator = GoogleTranslator(source='auto', target='en')
        prompt_en = translator.translate(prompt)


        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message_id, text='Вот ваше изображение '+ prompt)
        image_url = generate_image(prompt_en)
        send_image(update, context, image_url)


    else:

        conversation_history.append({"role": "assistant", "content": response})
        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message_id, text=response)


        






# Функция для обработки ошибок
def error(update, context):
    logging.warning('Ошибка: "%s"', context.error)

# Основная функция
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()