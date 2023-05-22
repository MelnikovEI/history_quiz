import json
import logging
from random import randrange, randint
import redis
import vk_api as vk
from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from tg_bot import extract_short_answer

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

NEW_QUESTION_REQUEST, ANSWER, GIVE_UP, END = range(4)


def echo(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=randint(1, 1000)
    )


def main() -> None:
    env = Env()
    env.read_env()
    vk_session = vk.VkApi(token=env('VK_GROUP_TOKEN'))
    vk_api = vk_session.get_api()

    with open(env('QUESTIONS_FILE'), 'r', encoding='utf-8') as questions_file:
        questions = json.load(questions_file)

    redis_db = redis.Redis(
        host=env('REDIS_HOST'), port=env('REDIS_PORT'), username=env('REDIS_USERNAME'),
        password=env('REDIS_PASSWORD'),
        decode_responses=True
    )

    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    status = NEW_QUESTION_REQUEST
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            vk_api.messages.send(
                peer_id=event.peer_id,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
                message='Нажмите кнопку меню или введите ответ'
            )
            if event.text == "Новый вопрос":
                question_number = randrange(len(questions))
                redis_db.set(event.user_id, question_number)
                vk_api.messages.send(
                    peer_id=event.peer_id,
                    random_id=get_random_id(),
                    message=questions[question_number]['Вопрос']
                )
                status = ANSWER
                logger.info("Question for %s: %s", event.user_id, question_number)
                continue

            if status == ANSWER:
                user_question_number = redis_db.get(event.user_id)
                right_answer = extract_short_answer(questions[int(user_question_number)]['Ответ'])
                if event.text == "Сдаться":
                    vk_api.messages.send(
                        peer_id=event.peer_id,
                        random_id=get_random_id(),
                        message='Вы сдались. Вот правильный ответ:'
                    )
                    status = GIVE_UP
                    vk_api.messages.send(
                        peer_id=event.peer_id,
                        random_id=get_random_id(),
                        message=questions[int(user_question_number)]['Ответ']
                    )
                    logger.info("User %s gave up", event.user_id)
                    continue
                if str(right_answer).lower().strip('" .') == event.text.lower().strip('" .'):
                    vk_api.messages.send(
                        peer_id=event.peer_id,
                        random_id=get_random_id(),
                        message='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
                    )
                    status = NEW_QUESTION_REQUEST
                else:
                    vk_api.messages.send(
                        peer_id=event.peer_id,
                        random_id=get_random_id(),
                        message='Неправильно… Попробуешь ещё раз?'
                    )
                continue


if __name__ == "__main__":
    main()
