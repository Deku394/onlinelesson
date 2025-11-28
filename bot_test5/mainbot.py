from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import filters  # filters не используется, можно удалить
from config import *  # Убедитесь, что config.py содержит api
from keyboards import *  # Убедитесь, что keyboards.py содержит start_kb
from texst import *  # Убедитесь, что texst.py содержит start_text
import logging
import json
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bot_tests = Bot(token=api)
dp = Dispatcher(bot_tests, storage=MemoryStorage())

# ID администратора (ваш Telegram ID)
ADMIN_ID = 1060502535  # Замените на ваш ID

# Файл для хранения зарегистрированных пользователей
DB_FILE = 'registered_users.json'

# Список зарегистрированных пользователей (будет загружен из файла)
registered_users = {}

# Глобальная переменная для хранения ID последнего отправленного сообщения
last_message_id = None


# --- Функции для работы с базой данных пользователей ---
def load_registered_users():
    """Загружает зарегистрированных пользователей из файла."""
    global registered_users
    if os.path.exists(DB_FILE) and os.path.getsize(DB_FILE) > 0:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            try:
                registered_users = json.load(f)
                logging.info(f"Загружено {len(registered_users)} пользователей из {DB_FILE}")
            except json.JSONDecodeError:
                logging.error(
                    f"Ошибка декодирования JSON в файле {DB_FILE}. Файл может быть повреждён. База пользователей сброшена.")
                registered_users = {}  # Сбрасываем на пустой словарь, если ошибка
            except Exception as e:
                logging.error(f"Неизвестная ошибка при загрузке пользователей из {DB_FILE}: {e}")
                registered_users = {}
    else:
        logging.info(f"Файл {DB_FILE} не существует или пуст. Инициализация пустой базы пользователей.")
        registered_users = {}  # Убедимся, что словарь пуст, если файл не существует


def save_registered_users():
    """Сохраняет текущий список зарегистрированных пользователей в файл."""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(registered_users, f, ensure_ascii=False, indent=4)
        logging.info(f"Сохранено {len(registered_users)} пользователей в {DB_FILE}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении пользователей в {DB_FILE}: {e}")


# --- Вызов загрузки пользователей при старте бота ---
# Этот вызов должен быть выполнен один раз при запуске скрипта
load_registered_users()


# --- Состояния для FSM ---
class AdminStates(StatesGroup):
    waiting_for_users_selection = State()
    waiting_for_message = State()
    waiting_for_media = State()
    # waiting_for_user_ids_to_send_message = State() # Это состояние не используется, можно удалить
    waiting_for_user_id_to_delete = State()
    # waiting_for_new_name = State() # Это состояние не используется, можно удалить


# --- Обработчики команд и кнопок ---

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = str(message.from_user.id)  # Преобразуем ID в строку для ключей JSON
    name = message.from_user.full_name
    custom_name = message.from_user.username
    # phone_number = message.contact.phone_number if message.contact else "Не указано"
    # Если вы хотите хранить номер телефона, убедитесь, что он запрашивается у пользователя
    # и добавьте 'phone': phone_number в словарь.

    # Регистрируем пользователя, если его еще нет, или обновляем данные
    if user_id not in registered_users:
        registered_users[user_id] = {
            'name': name,
            'custom_name': custom_name,
            # 'phone': phone_number, # Если нужно хранить телефон
        }
        save_registered_users()  # Сохраняем базу данных после добавления нового пользователя
        logging.info(f"Новый пользователь зарегистрирован: ID {user_id}, Имя: {name}")
    else:
        # Обновляем данные существующего пользователя, если они изменились
        current_user_data = registered_users[user_id]
        if current_user_data.get('name') != name or current_user_data.get('custom_name') != custom_name:
            registered_users[user_id]['name'] = name
            registered_users[user_id]['custom_name'] = custom_name
            save_registered_users()
            logging.info(f"Данные пользователя ID {user_id} обновлены.")

    global last_message_id

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_1.jpg', 'rb') as img:
        new_message = await message.answer_photo(img,
                                                 f'Добро пожаловать, {message.from_user.full_name}!👋\n' + start_text,
                                                 parse_mode=types.ParseMode.HTML, reply_markup=start_kb)
        last_message_id = new_message.message_id


# Команда /admin
@dp.message_handler(commands=['admin'])
async def cmd_admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Отправить сообщение всем", "Отправить сообщение выбранным")
        keyboard.add("Список пользователей", "Удалить пользователя")
        keyboard.add("Главное меню")
        await message.answer(f"Добро пожаловать в панель администратора, {message.from_user.full_name}!",
                             reply_markup=keyboard)
    else:
        await message.answer("У вас нет доступа к админ-панели!")


# Обработка кнопки "Список пользователей"
@dp.message_handler(lambda message: message.text == "Список пользователей")
async def list_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет доступа к этой функции.")
        return

    if not registered_users:
        await message.reply("Нет зарегистрированных пользователей.")
        return

    user_list_str = "Список зарегистрированных пользователей:\n"
    for index, (user_id, user_data) in enumerate(registered_users.items()):
        user_list_str += f"{index + 1}. ID: {user_id}, Имя: {user_data.get('name', 'Не указано')}, Имя (через @): @{user_data.get('custom_name', 'Не указано')}\n"

    # Разбиваем список на части, если он слишком длинный для одного сообщения Telegram (4096 символов)
    if len(user_list_str) > 4000:
        parts = []
        current_part = ""
        for line in user_list_str.split('\n'):
            if len(current_part) + len(line) + 1 > 4000:
                parts.append(current_part)
                current_part = ""
            current_part += line + '\n'
        if current_part:
            parts.append(current_part)

        for part in parts:
            await message.reply(part)
    else:
        await message.reply(user_list_str)


# Обработка кнопки "Отправить сообщение выбранным"
@dp.message_handler(lambda message: message.text == "Отправить сообщение выбранным")
async def select_users_to_send_message(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет доступа к этой функции.")
        return

    await AdminStates.waiting_for_users_selection.set()

    if not registered_users:
        await message.reply("Нет зарегистрированных пользователей.")
        await state.finish()
        return

    user_list_str = "Выберите пользователя(ей) по ID (через запятую), которому(ым) хотите отправить сообщение:\n"
    for index, (user_id, user_data) in enumerate(registered_users.items()):
        user_list_str += f"{index + 1}. ID: {user_id}, Имя: {user_data.get('name', 'Не указано')}, Имя (через @): @{user_data.get('custom_name', 'Не указано')}\n"

    await message.reply(user_list_str)


@dp.message_handler(state=AdminStates.waiting_for_users_selection)
async def get_selected_users(message: types.Message, state: FSMContext):
    user_ids_input = message.text.split(",")  # Разделяем по запятой
    valid_user_ids = []

    for user_id_str in user_ids_input:
        user_id_str = user_id_str.strip()  # Удаляем пробелы
        # Проверяем, что ID состоит только из цифр и существует в нашей базе
        if user_id_str.isdigit() and user_id_str in registered_users:
            valid_user_ids.append(user_id_str)  # Добавляем строковый ID
        else:
            logging.warning(f"Невалидный или несуществующий ID пользователя в списке выбора: {user_id_str}")

    if valid_user_ids:
        await state.update_data(valid_user_ids=valid_user_ids)
        await AdminStates.waiting_for_media.set()
        await message.reply(
            "Введите сообщение для выбранного(ых) пользователя(ей) (текст, фото, видео, аудио, голосовое, стикер, видео-сообщение, документ):")
    else:
        await message.reply("Нет валидных ID пользователей. Попробуйте снова.")
        await state.finish()


@dp.message_handler(state=AdminStates.waiting_for_media, content_types=types.ContentTypes.ANY)
async def process_message_to_selected(message: types.Message, state: FSMContext):
    data = await state.get_data()
    valid_user_ids = data.get('valid_user_ids', [])

    if not valid_user_ids:
        await message.reply("Не было выбрано ни одного пользователя для отправки сообщения.")
        await state.finish()
        return

    sent_count = 0
    failed_users = []

    for user_id_str in valid_user_ids:
        try:
            # Преобразуем ID обратно в int для отправки сообщения через aiogram
            user_id_int = int(user_id_str)
            if message.content_type == 'text':
                await bot_tests.send_message(user_id_int, message.text)
            elif message.content_type == 'photo':
                await bot_tests.send_photo(user_id_int, message.photo[-1].file_id, caption=message.caption)
            elif message.content_type == 'video':
                await bot_tests.send_video(user_id_int, message.video.file_id, caption=message.caption)
            elif message.content_type == 'audio':
                await bot_tests.send_audio(user_id_int, message.audio.file_id, caption=message.caption)
            elif message.content_type == 'voice':
                await bot_tests.send_voice(user_id_int, message.voice.file_id, caption=message.caption)
            elif message.content_type == 'sticker':
                await bot_tests.send_sticker(user_id_int, message.sticker.file_id)
            elif message.content_type == 'video_note':
                await bot_tests.send_video_note(user_id_int, message.video_note.file_id)
            elif message.content_type == 'document':
                await bot_tests.send_document(user_id_int, message.document.file_id, caption=message.caption)
            sent_count += 1
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение пользователю(ям) {user_id_str}: {e}")
            failed_users.append(user_id_str)

    if sent_count > 0:
        await message.reply(f"Сообщение отправлено {sent_count} выбранному(ым) пользователю(ям).")
    if failed_users:
        await message.reply(f"Не удалось отправить сообщение следующему(им) пользователю(ям): {', '.join(failed_users)}")

    await state.finish()


# Обработка кнопки "Отправить сообщение всем"
@dp.message_handler(lambda message: message.text == "Отправить сообщение всем")
async def send_message_to_all(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет доступа к этой функции.")
        return

    await AdminStates.waiting_for_message.set()
    await message.reply(
        "Введите сообщение для всех зарегистрированных пользователей (текст, фото, видео, аудио, голосовое, стикер, видео-сообщение, документ):")


@dp.message_handler(state=AdminStates.waiting_for_message, content_types=types.ContentTypes.ANY)
async def process_message_to_all(message: types.Message, state: FSMContext):
    sent_count = 0
    failed_users = []

    for user_id_str in registered_users.keys():
        try:
            user_id_int = int(user_id_str)  # Преобразуем ID обратно в int для отправки сообщения
            if message.content_type == 'text':
                await bot_tests.send_message(user_id_int, message.text)
            elif message.content_type == 'photo':
                await bot_tests.send_photo(user_id_int, message.photo[-1].file_id, caption=message.caption)
            elif message.content_type == 'video':
                await bot_tests.send_video(user_id_int, message.video.file_id, caption=message.caption)
            elif message.content_type == 'audio':
                await bot_tests.send_audio(user_id_int, message.audio.file_id, caption=message.caption)
            elif message.content_type == 'voice':
                await bot_tests.send_voice(user_id_int, message.voice.file_id, caption=message.caption)
            elif message.content_type == 'sticker':
                await bot_tests.send_sticker(user_id_int, message.sticker.file_id)
            elif message.content_type == 'video_note':
                await bot_tests.send_video_note(user_id_int, message.video_note.file_id)
            elif message.content_type == 'document':
                await bot_tests.send_document(user_id_int, message.document.file_id, caption=message.caption)
            sent_count += 1
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение пользователям {user_id_str}: {e}")
            failed_users.append(user_id_str)

    if sent_count > 0:
        await message.reply(f"Сообщение отправлено {sent_count} зарегистрированным пользователям.")
    if failed_users:
        await message.reply(f"Не удалось отправить сообщение следующим пользователям: {', '.join(failed_users)}")

    await state.finish()


# Обработка кнопки "Удалить пользователя"
@dp.message_handler(lambda message: message.text == "Удалить пользователя")
async def delete_user(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет доступа к этой функции.")
        return

    await AdminStates.waiting_for_user_id_to_delete.set()
    if not registered_users:
        await message.reply("Нет зарегистрированных пользователей для удаления.")
        await message.finish()
        return

    user_list_str = "Введите ID пользователя, которого хотите удалить:\n"
    for index, (user_id, user_data) in enumerate(registered_users.items()):
        user_list_str += f"{index + 1}. ID: {user_id}, Имя: {user_data.get('name', 'Не указано')}, Имя (через @): @{user_data.get('custom_name', 'Не указано')}\n"

    await message.reply(user_list_str)


@dp.message_handler(state=AdminStates.waiting_for_user_id_to_delete)
async def remove_user(message: types.Message, state: FSMContext):
    user_id_to_delete = message.text.strip()  # Получаем ID как строку

    if user_id_to_delete in registered_users:
        del registered_users[user_id_to_delete]
        save_registered_users()  # Сохраняем изменения после удаления
        await message.reply(f"Пользователь с ID {user_id_to_delete} был удален.")
        logging.info(f"Пользователь ID {user_id_to_delete} удален.")
    else:
        await message.reply("Пользователь с таким ID не найден.")

    await state.finish()


# Добавьте обработчик для кнопки "Главное меню"
@dp.message_handler(lambda message: message.text == "Главное меню", state="*")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await state.finish()  # Завершаем любое текущее состояние FSM
    # Отправляем пользователя в главное меню бота
    # Используем ту же логику, что и в /start, но без регистрации/обновления пользователя
    global last_message_id
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_1.jpg', 'rb') as img:
        new_message = await message.answer_photo(img,
                                                 f'Добро пожаловать, {message.from_user.full_name}!👋\n' + start_text,
                                                 parse_mode=types.ParseMode.HTML, reply_markup=start_kb)
        last_message_id = new_message.message_id

# Обрабатываем нажатие на кнопку "Главное меню"
@dp.message_handler(lambda message: message.text == "Главное меню")
async def back_to_main_menu(message: types.Message):
    await start(message)  # Вызываем функцию start для возврата в главное меню

@dp.callback_query_handler(text='consultation')
async def consultation(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_consultation.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, consultation_text, reply_markup=consultation_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
        await call.answer()

# Обработчик текстовых сообщений от пользователей
@dp.message_handler(lambda message: message.text and message.chat.type == 'private')
async def handle_user_message(message):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    user_id = message.from_user.id  # ID пользователя
    user_message = message.text  # Текст сообщения от пользователя

    # Отправка сообщения вам
    await bot_tests.send_message(ADMIN_ID, f"Пользователь {message.from_user.username} ({user_id}) написал(а):⬇️\n\n{user_message}")

    # Ответ пользователю (по желанию)
    new_message = await message.reply("Ваше сообщение отправлено администратору!", reply_markup=consultation_back_menu_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения

@dp.callback_query_handler(text='action')
async def action(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_action.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, action_text, parse_mode=types.ParseMode.HTML, reply_markup=action_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='about_promotion')
async def about_promotion(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_promotion.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, about_promotion_text, parse_mode=types.ParseMode.HTML, reply_markup=about_promotion_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='rules')
async def rules(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_rules.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, rules_text, parse_mode=types.ParseMode.HTML, reply_markup=rules_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='mailing')
async def mailing(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_mailing_.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, mailing_text, parse_mode=types.ParseMode.HTML, reply_markup=mailing_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='subscription')
async def subscription(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_subscription_.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, subscription_text, parse_mode=types.ParseMode.HTML, reply_markup=subscription_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing')
async def auto_mailing(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_automailing_.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, auto_mailing_text, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='commenting')
async def commenting(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_commenting_.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, commenting_text, parse_mode=types.ParseMode.HTML, reply_markup=commenting_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='tg_bot')
async def tg_bot(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_tg_bots_.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, tg_bot_text, parse_mode=types.ParseMode.HTML, reply_markup=tg_bot_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='price_list')
async def price_list(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_price.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, price_list_text, parse_mode=types.ParseMode.HTML, reply_markup=price_list_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='price_list_back_list_1')
async def price_list_back_list_1(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_promotion.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, about_promotion_text, parse_mode=types.ParseMode.HTML, reply_markup=about_promotion_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='back_menu')
async def back_menu(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_1.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, f'Добро пожаловать, {call.from_user.full_name}!👋\n' + start_text, parse_mode=types.ParseMode.HTML, reply_markup=start_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='mailing_next_block_1')
async def mailing_next_block_1(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_ts_mailing.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_mailing_text, parse_mode=types.ParseMode.HTML, reply_markup=mailing_next_block_kb_1)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='mailing_back_list_1')
async def mailing_back_list_1(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_promotion.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, about_promotion_text, parse_mode=types.ParseMode.HTML, reply_markup=about_promotion_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='mailing_next_block_2')
async def mailing_next_block_2(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_text_1, parse_mode=types.ParseMode.HTML, reply_markup=mailing_next_block_kb_2)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='mailing_back_list_2')
async def mailing_back_list_2(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_mailing_.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, mailing_text, parse_mode=types.ParseMode.HTML, reply_markup=mailing_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='mailing_next_block_3')
async def mailing_next_block_3(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_text_2, parse_mode=types.ParseMode.HTML, reply_markup=mailing_next_block_kb_3)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='mailing_back_list_3')
async def mailing_back_list_3(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_ts_mailing.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_mailing_text, parse_mode=types.ParseMode.HTML, reply_markup=mailing_next_block_kb_1)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='mailing_next_block_4')
async def mailing_next_block_4(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_text_3, parse_mode=types.ParseMode.HTML, reply_markup=mailing_next_block_kb_4)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='mailing_back_list_4')
async def mailing_back_list_4(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_text_1, parse_mode=types.ParseMode.HTML, reply_markup=mailing_next_block_kb_2)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='mailing_next_block_5')
async def mailing_next_block_5(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_text_4, parse_mode=types.ParseMode.HTML, reply_markup=mailing_next_block_kb_5)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='mailing_back_list_5')
async def mailing_back_list_5(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_text_2, parse_mode=types.ParseMode.HTML, reply_markup=mailing_next_block_kb_3)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='mailing_next_block_6')
async def mailing_next_block_6(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_text_5, parse_mode=types.ParseMode.HTML, reply_markup=mailing_next_block_kb_6)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='mailing_back_list_6')
async def mailing_back_list_6(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_text_3, parse_mode=types.ParseMode.HTML, reply_markup=mailing_next_block_kb_4)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='mailing_back_list_7')
async def mailing_back_list_7(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_text_4, parse_mode=types.ParseMode.HTML, reply_markup=mailing_next_block_kb_5)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='subscription_next_block_1')
async def subscription_next_block_1(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_ts_subscription.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_mailing_subscription_text, parse_mode=types.ParseMode.HTML, reply_markup=subscription_next_block_kb_1)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='subscription_back_list_1')
async def subscription_back_list_1(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_promotion.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, about_promotion_text, parse_mode=types.ParseMode.HTML, reply_markup=about_promotion_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='subscription_next_block_2')
async def subscription_next_block_2(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_subscription_text_1, parse_mode=types.ParseMode.HTML, reply_markup=subscription_next_block_kb_2)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='subscription_back_list_2')
async def subscription_back_list_2(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_subscription_.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, subscription_text, parse_mode=types.ParseMode.HTML, reply_markup=subscription_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='subscription_next_block_3')
async def subscription_next_block_3(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_subscription_text_2, parse_mode=types.ParseMode.HTML, reply_markup=subscription_next_block_kb_3)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='subscription_back_list_3')
async def subscription_back_list_3(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_ts_subscription.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_mailing_subscription_text, parse_mode=types.ParseMode.HTML, reply_markup=subscription_next_block_kb_1)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='subscription_next_block_4')
async def subscription_next_block_4(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_subscription_text_3, parse_mode=types.ParseMode.HTML, reply_markup=subscription_next_block_kb_4)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='subscription_back_list_4')
async def subscription_back_list_4(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_subscription_text_1, parse_mode=types.ParseMode.HTML, reply_markup=subscription_next_block_kb_2)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='subscription_next_block_5')
async def subscription_next_block_5(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_subscription_text_4, parse_mode=types.ParseMode.HTML, reply_markup=subscription_next_block_kb_5)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='subscription_back_list_5')
async def subscription_back_list_5(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_subscription_text_2, parse_mode=types.ParseMode.HTML, reply_markup=subscription_next_block_kb_3)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='subscription_back_list_6')
async def subscription_back_list_6(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_mailing_subscription_text_3, parse_mode=types.ParseMode.HTML, reply_markup=subscription_next_block_kb_4)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_next_block_1')
async def auto_mailing_next_block_1(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_ts_automailing.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_auto_mailing_text, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_1)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_back_list_1')
async def auto_mailing_back_list_1(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_promotion.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, about_promotion_text, parse_mode=types.ParseMode.HTML, reply_markup=about_promotion_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_next_block_2')
async def auto_mailing_next_block_2(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_au_mail_1.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_auto_mailing_text_1, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_2)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_back_list_2')
async def auto_mailing_back_list_2(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_automailing_.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, auto_mailing_text, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_next_block_3')
async def auto_mailing_next_block_3(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_auto_mailing_text_2, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_3)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_back_list_3')
async def auto_mailing_back_list_3(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_ts_automailing.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_auto_mailing_text, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_1)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_next_block_4')
async def auto_mailing_next_block_4(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_au_mail_3.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_auto_mailing_text_3, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_4)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_back_list_4')
async def auto_mailing_back_list_4(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_au_mail_1.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_auto_mailing_text_1, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_2)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_next_block_5')
async def auto_mailing_next_block_5(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_auto_mailing_text_4, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_5)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_back_list_5')
async def auto_mailing_back_list_5(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_auto_mailing_text_2, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_3)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_next_block_6')
async def auto_mailing_next_block_6(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_auto_mailing_text_5, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_6)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_back_list_6')
async def auto_mailing_back_list_6(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_au_mail_3.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_auto_mailing_text_3, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_4)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_next_block_7')
async def auto_mailing_next_block_7(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_auto_mailing_text_6, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_7)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_back_list_7')
async def auto_mailing_back_list_7(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_auto_mailing_text_4, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_5)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_next_block_8')
async def auto_mailing_next_block_8(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_auto_mailing_text_7, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_8)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_back_list_8')
async def auto_mailing_back_list_8(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_auto_mailing_text_5, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_6)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_next_block_9')
async def auto_mailing_next_block_9(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_auto_mailing_text_8, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_9)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_back_list_9')
async def auto_mailing_back_list_9(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_auto_mailing_text_6, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_7)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='auto_mailing_back_list_10')
async def auto_mailing_back_list_10(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_auto_mailing_text_7, parse_mode=types.ParseMode.HTML, reply_markup=auto_mailing_next_block_kb_8)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='commenting_next_block_1')
async def commenting_next_block_1(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_ts_commenting.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_commenting_text, parse_mode=types.ParseMode.HTML, reply_markup=commenting_next_block_kb_1)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='commenting_back_list_1')
async def commenting_back_list_1(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_promotion.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, about_promotion_text, parse_mode=types.ParseMode.HTML, reply_markup=about_promotion_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='commenting_next_block_2')
async def commenting_next_block_2(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_com_1.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_commenting_text_1, parse_mode=types.ParseMode.HTML, reply_markup=commenting_next_block_kb_2)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='commenting_back_list_2')
async def commenting_back_list_2(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_commenting_.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, commenting_text, parse_mode=types.ParseMode.HTML, reply_markup=commenting_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='commenting_next_block_3')
async def commenting_next_block_3(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_commenting_text_2, parse_mode=types.ParseMode.HTML, reply_markup=commenting_next_block_kb_3)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='commenting_back_list_3')
async def commenting_back_list_3(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_ts_commenting.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_commenting_text, parse_mode=types.ParseMode.HTML, reply_markup=commenting_next_block_kb_1)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='commenting_next_block_4')
async def commenting_next_block_4(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_commenting_text_3, parse_mode=types.ParseMode.HTML, reply_markup=commenting_next_block_kb_4)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='commenting_back_list_4')
async def commenting_back_list_4(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_com_1.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_commenting_text_1, parse_mode=types.ParseMode.HTML, reply_markup=commenting_next_block_kb_2)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='commenting_back_list_5')
async def commenting_back_list_5(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_commenting_text_2, parse_mode=types.ParseMode.HTML, reply_markup=commenting_next_block_kb_3)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='tg_bot_next_block_1')
async def tg_bot_next_block_1(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_ts_tg_bot.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_bot_text, parse_mode=types.ParseMode.HTML, reply_markup=tg_bot_next_block_kb_1)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='tg_bot_back_list_1')
async def tg_bot_back_list_1(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_promotion.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, about_promotion_text, parse_mode=types.ParseMode.HTML, reply_markup=about_promotion_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='tg_bot_next_block_2')
async def tg_bot_next_block_2(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_tgb_1_2.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_bot_text_1, parse_mode=types.ParseMode.HTML, reply_markup=tg_bot_next_block_kb_2)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='tg_bot_back_list_2')
async def tg_bot_back_list_2(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_tg_bots_.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, tg_bot_text, parse_mode=types.ParseMode.HTML, reply_markup=tg_bot_kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='tg_bot_next_block_3')
async def tg_bot_next_block_3(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_bot_text_2, parse_mode=types.ParseMode.HTML, reply_markup=tg_bot_next_block_kb_3)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='tg_bot_back_list_3')
async def tg_bot_back_list_3(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_ts_tg_bot.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_bot_text, parse_mode=types.ParseMode.HTML, reply_markup=tg_bot_next_block_kb_1)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='tg_bot_next_block_4')
async def tg_bot_next_block_4(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_bot_text_3, parse_mode=types.ParseMode.HTML, reply_markup=tg_bot_next_block_kb_4)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='tg_bot_back_list_4')
async def tg_bot_back_list_4(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_tgb_1_2.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, ts_bot_text_1, parse_mode=types.ParseMode.HTML, reply_markup=tg_bot_next_block_kb_2)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

@dp.callback_query_handler(text='tg_bot_back_list_5')
async def tg_bot_back_list_5(call):
    global last_message_id  # Объявляем переменную как глобальную

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    new_message = await call.message.answer(ts_bot_text_2, parse_mode=types.ParseMode.HTML, reply_markup=tg_bot_next_block_kb_3)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
