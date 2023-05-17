import json
import logging
from random import randrange
import telegram
from environs import Env
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import redis


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def reply(update: Update, context: CallbackContext, redis_db) -> None:
    """Echo the user message."""
    user_question_number = redis_db.get(update.effective_user.id)
    with open('quiz_qna.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)

    if update.message.text == 'New question':
        question_number = randrange(len(questions))
        update.message.reply_text(questions[question_number]['Вопрос'])
        redis_db.set(update.effective_user.id, question_number)
        return
    elif update.message.text == 'Give up':
        redis_db.delete(update.effective_user.id)
        update.message.reply_text('Вы сдались :(')
        return
    elif update.message.text == 'My score':
        update.message.reply_text('Ваш счёт: ')
        return
    elif user_question_number:
        if str(questions[int(user_question_number)]['Ответ']).lower().strip('" .')\
                == update.message.text.lower().strip('" .'):
            update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
        else:
            update.message.reply_text('Неправильно… Попробуешь ещё раз?')


def main() -> None:
    env = Env()
    env.read_env()
    tg_bot_token = env('TG_BOT_TOKEN')

    updater = Updater(tg_bot_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command,
            callback=lambda update, context: reply(update, context, redis_db)
        )
    )

    custom_keyboard = [['New question', 'Give up'],
                       ['My score']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot = telegram.Bot(token=tg_bot_token)
    chat_id = 546682970
    bot.send_message(chat_id=chat_id, text="Custom Keyboard Test", reply_markup=reply_markup)

    redis_db = redis.Redis(
        host='redis-10947.c293.eu-central-1-1.ec2.cloud.redislabs.com', port=10947, username='default',
        password='wgR40SLRPtKqaCwSNSK3Uk8OY7IJ3I2g',
        decode_responses=True
    )

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    main()
