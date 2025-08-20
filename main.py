import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import g4f
from g4f.client import Client
from deep_translator import GoogleTranslator
import json
import os


# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен телеграмм-бота
TOKEN = ''

# Выбор модели
model = "gpt-4"  # выберите модель, которую вы хотите использовать
provider = g4f.Provider.Yqcloud

# Инициализация истории сообщений
conversation_history_file = 'conversation_history.json'
conversation_history = {}

# Загрузка истории сообщений из файла 
if os.path.exists(conversation_history_file):
    with open(conversation_history_file, 'r', encoding='utf-8') as f:
        conversation_history = json.load(f)



# Создание экземпляра класса Client
client = Client()

# Функция для обработки команды /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Привет! Я телеграмм-бот для общения с Чат ГПТ.')









# Функция для обработки текстовых сообщений
def handle_text_message(update, context):

    # пока пользователь ждет сообщение
    message = context.bot.send_message(chat_id=update.effective_chat.id, text='⏳')
    message_id = message.message_id
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")


    user_id = update.effective_user.id
    if user_id not in conversation_history:
        conversation_history[user_id] = []


    user_message = update.message.text

    conversation_history[user_id].append({"role": "user", "content": user_message})

    response = g4f.ChatCompletion.create(
        model=model,
        provider=provider,
        messages=conversation_history[user_id],
    )

    conversation_history[user_id].append({"role": "assistant", "content": response})

    context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message_id, text=response)

    #Записывает ответ бота в историю диалога
    with open(conversation_history_file, 'w', encoding='utf-8') as f:
        json.dump(conversation_history, f, ensure_ascii=False)







# Функция для обработки которая выводится после /image
def handle_image_message(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Что нарисовать?')
    context.user_data['waiting_for_image_prompt'] = True

    #запись в историю
    user_id = update.effective_user.id
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    user_message = update.message.text
    conversation_history[user_id].append({"role": "user", "content": user_message})


    with open(conversation_history_file, 'w', encoding='utf-8') as f:
        json.dump(conversation_history, f, ensure_ascii=False)
    
#функция после того как пользователь ввел промпт
def handle_image_prompt(update, context):
    if 'waiting_for_image_prompt' in context.user_data:
        if update.message.text != "/image":

            # пока пользователь ждет сообщение
            message = context.bot.send_message(chat_id=update.effective_chat.id, text='⏳')
            message_id = message.message_id
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

            # перевод текста
            prompt = update.message.text.strip()
            translator = GoogleTranslator(source='auto', target='en')
            prompt_en = translator.translate(prompt)

            image_url = generate_image(prompt_en)
            context.bot.edit_message_text(chat_id=update.effective_chat.id,message_id=message_id, text='Вот ваше изображение ' + prompt)
            send_image(update, context, image_url)
                
            #запись в историю
            user_id = update.effective_user.id
            if user_id not in conversation_history:
                conversation_history[user_id] = []
            conversation_history[user_id].append({"role": "user", "content": prompt})
            conversation_history[user_id].append({"role": "assistant", "content": "Изображение", "image_url": image_url})
            with open(conversation_history_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_history, f, ensure_ascii=False)
            
            del context.user_data['waiting_for_image_prompt']
        else:
            print("Пользователь отправил команду /image")

# Функция для генерации изображений
def generate_image(prompt_en):

    #if len(prompt_en) < 15:  # если промт слишком корткий(возникает ошибка)
        #prompt_en += "in the style of realism"

    response = client.images.generate(
        model="flux-pro",
        prompt=prompt_en,
        response_format="url"

    )
    return response.data[0].url

# Функция для отправки изображений
def send_image(update, context, image_url):
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)




#общая функция для всех видов диалога 
def handle_message(update, context):
    if update.message.text.startswith("/image"):
        handle_image_message(update, context)
    elif 'waiting_for_image_prompt' in context.user_data:
        handle_image_prompt(update, context)
    else:
        handle_text_message(update, context)








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













