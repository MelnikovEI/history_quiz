import json
import logging
from random import randrange
from environs import Env
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import redis

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

NEW_QUESTION_REQUEST, ANSWER, GIVE_UP, END = range(4)


def extract_short_answer(full_answer) -> str:
    str_before_point = full_answer.split('.', maxsplit=1)[0]
    str_before_bracket = str_before_point.split('(', maxsplit=1)[0]
    return str_before_bracket


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['New question']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        'Hi, this is a history quiz. Press "New question" to start',
        reply_markup=markup,
    )
    return NEW_QUESTION_REQUEST


def handle_new_question_request(update: Update, context: CallbackContext, redis_db, questions) -> int:
    reply_keyboard = [['Give up']]
    markup = ReplyKeyboardMarkup(reply_keyboard)

    question_number = randrange(len(questions))
    redis_db.set(update.effective_user.id, question_number)

    update.message.reply_text(questions[question_number]['Вопрос'], reply_markup=markup)

    user = update.message.from_user
    logger.info("Question for %s: %s", user.first_name, question_number)
    return ANSWER


def handle_solution_attempt(update: Update, context: CallbackContext, redis_db, questions):
    user_question_number = redis_db.get(update.effective_user.id)
    right_answer = extract_short_answer(questions[int(user_question_number)]['Ответ'])
    if str(right_answer).lower().strip('" .') == update.message.text.lower().strip('" .'):
        reply_keyboard = [['New question'], ['My score']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»', reply_markup=markup)
        return NEW_QUESTION_REQUEST
    else:
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')


def give_up(update: Update, context: CallbackContext, redis_db, questions) -> int:
    user = update.message.from_user
    logger.info("User %s gave up", user.first_name)

    user_question_number = redis_db.get(update.effective_user.id)

    reply_keyboard = [['New question']]
    markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text('Full right answer:')
    update.message.reply_text(questions[int(user_question_number)]['Ответ'], reply_markup=markup)
    return NEW_QUESTION_REQUEST


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main() -> None:
    env = Env()
    env.read_env()
    updater = Updater(env('TG_BOT_TOKEN'))

    with open(env('QUESTIONS_FILE'), 'r', encoding='utf-8') as questions_file:
        questions = json.load(questions_file)

    redis_db = redis.Redis(
        host=env('REDIS_HOST'), port=env('REDIS_PORT'), username=env('REDIS_USERNAME'),
        password=env('REDIS_PASSWORD'),
        decode_responses=True
    )
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NEW_QUESTION_REQUEST: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    callback=lambda update, context: handle_new_question_request(update, context, redis_db, questions)
                )
            ],
            ANSWER: [
                MessageHandler(
                    Filters.regex('^Give up$'),
                    callback=lambda update, context: give_up(update, context, redis_db, questions)
                ),
                MessageHandler(
                    Filters.text & ~Filters.command,
                    callback=lambda update, context: handle_solution_attempt(update, context, redis_db, questions)
                ),
            ],
            GIVE_UP: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    callback=lambda update, context: give_up(update, context, redis_db, questions),
                ),
            ],

        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
