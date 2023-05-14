import json
import logging
from random import randrange
import telegram
from environs import Env
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


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


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    if update.message.text == 'New question':
        with open('quiz_qna.json', 'r', encoding='utf-8') as f:
            questions = json.load(f)
        update.message.reply_text(questions[randrange(len(questions))]['Вопрос'])
    else:
        update.message.reply_text(update.message.text)


def main() -> None:
    env = Env()
    env.read_env()
    tg_bot_token = env('TG_BOT_TOKEN')

    updater = Updater(tg_bot_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    custom_keyboard = [['New question', 'Give up'],
                       ['My score']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot = telegram.Bot(token=tg_bot_token)
    chat_id = 546682970
    bot.send_message(chat_id=chat_id, text="Custom Keyboard Test", reply_markup=reply_markup)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    main()
