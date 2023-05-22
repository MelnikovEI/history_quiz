# History quiz bot
Бот-викторина по истории  
[VK bot](https://vk.com/club220747682)  
[Telegram bot](https://t.me/h_quiz_bot) - для страта послать боту сообщение `/start`
## Установка
[Установите Python](https://www.python.org/), если этого ещё не сделали. Требуется Python 3.8 и старше. Код может запуститься на других версиях питона от 3.1 и старше, но на них не тестировался.

Проверьте, что `python` установлен и корректно настроен. Запустите его в командной строке:
```sh
python --version
```
Возможно, вместо команды `python` здесь и в остальных инструкциях этого README придётся использовать `python3`. Зависит это от операционной системы и от того, установлен ли у вас Python старой второй версии.

Скачайте код:
```sh
git clone https://github.com/MelnikovEI/history_quiz
```

Перейдите в каталог проекта:
```sh
cd history_quiz
```

В каталоге проекта создайте виртуальное окружение:
```sh
python -m venv venv
```
Активируйте его. На разных операционных системах это делается разными командами:

- Windows: `.\venv\Scripts\activate`
- MacOS/Linux: `source venv/bin/activate`

Установите зависимости в виртуальное окружение:
```sh
pip install -r requirements.txt
```
### Настройка базы данных

[Создайте базу данных и запишите параметры доступа](https://redislabs.com/)

### Определите переменные окружения.
Создайте файл `.env` в каталоге `history_quiz/` и положите туда такой код:
```sh
TG_BOT_TOKEN=580108...eWQ
REDIS_HOST=redis-10947.c....com
REDIS_PORT=1...7
REDIS_USERNAME=default
REDIS_PASSWORD=wgR40...I2g
QUESTIONS_FILE=quiz_qna.json
```
Данные выше приведены для примера.
- `TG_BOT_TOKEN` замените на токен он чатбота в Telegram. Вот [туториал](https://spark.ru/startup/it-agenstvo-index/blog/47364/kak-poluchit-tokeni-dlya-sozdaniya-chat-bota-v-telegrame-vajbere-i-v-vkontakte), как это сделать.
- `REDIS...` параметры доступа к БД Redis
- `QUESTIONS_FILE` имя файла в формате json, содержащий вопросы и ответы
- `TG_ADMIN_BOT_TOKEN` токен бота для администрирования проекта, пришлёт ошибку скрипта администратору
- `ADMIN_CHAT_ID` id учетной записи администратора в телеграм можно узнать https://telegram.me/userinfobot
## Запуск
Телеграм бот
```sh
python tg_bot.py
```
VK бот
```sh
python vk_bot.py
```
Скрипт будет работать до тех пор, пока не будет закрыт.
