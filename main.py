import config
import login_parser
from db import db
import keyboard as kb
import profile

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import logging
import asyncio
from datetime import datetime, timedelta

import ecampusapi as ec

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# db connection
db = db(config.DB_PATH)


class RegStages(StatesGroup):
    choosing_institute = State()
    choosing_speciality = State()
    choosing_academic_group = State()
    choosing_subgroup = State()
    changing_time = State()
    choosing_role = State()
    typing_name = State()
    choosing_teacher = State()
    choosing_mode = State()

class EcampusLogin(StatesGroup):
    typing_login = State()
    typing_password = State()
    typing_captcha = State()



@dp.message_handler(commands=['captcha'], content_types=['text'], state=EcampusLogin.typing_login) #captcha output
async def captha_test(message: types.Message):
    await bot.send_message(message.from_user.id, text='Введите логин')
    await EcampusLogin.typing_login.set()
    await bot.send_message(message.from_user.id, text='Введите пароль')
    await EcampusLogin.typing_login.set()
    await bot.send_message(message.from_user.id, text='Введите капчу')
    photo = open('Captcha.jpeg', 'rb')
    await bot.send_photo(message.from_user.id, photo)
    await EcampusLogin.typing_login.set()

@dp.message_handler(commands=['cancel'], state='*')
async def cancel_command(message: types.Message, state: FSMContext):
    await message.answer('Состояние сброшено до начального')
    await state.finish()


@dp.message_handler(commands=['help'], state='*')
async def help_command(message: types.Message):
    await bot.send_message(message.from_user.id, f'/profile - Настройки профиля\n'
                                                 f'/stop - Прекратить ежедневную рассылку\n'
                                                 f'/continue - Начать ежедневную рассылку\n'
                                                 f'/cancel - Сбрасывает состояние до начального\n'
                                                 f'Остались вопросы? tg - @Etern1ty666, tg - @Maria_Lapina')


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
        db.set_using_began(message.from_user.id, (datetime.now()).strftime('%Y-%m-%d %H:%M:%S'))
        await message.answer(f'Привет, {message.from_user.first_name}!\n'
                             f'Для кого будем получать расписание??', reply_markup=kb.student_or_teacher_keyboard)
        await RegStages.choosing_role.set()
    else:
        await bot.send_message(message.from_user.id, f'{message.from_user.first_name}, вы уже зарегистрированы.\n/help',
                               reply_markup=kb.main_keyboard)  # добавить меню действий и имя пользоватееля


@dp.callback_query_handler(state=RegStages.choosing_role)
async def choosing_role(call: types.CallbackQuery):
    try:
        if call.data == '2':
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

            db.update_user_role(call.from_user.id, call.data)
            await bot.send_message(call.from_user.id, f'Выберите институт',
                                   reply_markup=kb.creating_keyboard_institutes())
            await RegStages.choosing_institute.set()
        if call.data == '1':
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            db.update_user_role(call.from_user.id, call.data)
            await bot.send_message(call.from_user.id, f'Введите фамилию: ')
            await RegStages.typing_name.set()
    except:
        await bot.send_message(call.from_user.id, f'Неизвестная ошибка. Попробуйте снова.',
                               reply_markup=kb.student_or_teacher_keyboard())


@dp.message_handler(state=RegStages.typing_name)
async def typing_name(message: types.Message, state: FSMContext):
    schedule_mode = ''
    if db.get_sending_mode(message.from_user.id) == '1':
        schedule_mode = 'На текущий день'
    elif db.get_sending_mode(message.from_user.id) == '2':
        schedule_mode = 'На следующий день'
    try:
        await bot.send_message(message.from_user.id, 'Вот что удалось найти: ',
                               reply_markup=kb.creating_teachers_list(message.text))
        await RegStages.choosing_teacher.set()
    except:
        await bot.send_message(message.from_user.id, 'Ищем...')
        full_page = requests.get(f'{config.SEARCH_URL}{message.text}')
        soup = BeautifulSoup(full_page.text, "lxml")
        teacher_id = str(soup.find(class_="login text-right").find('a'))
        teacher_id = teacher_id.replace('">Войти</a>', '')
        teacher_id = teacher_id.replace('<a href="/account/login?returnUrl=%2Fschedule%2Fteacher%2F', '')
        if teacher_id.isnumeric():
            db.update_academic_group_name(message.from_user.id, str(teacher_id))
            await bot.send_message(message.from_user.id,
                                   f'Сохранено!\nВаше ФИО: {profile.pretty_teacher_name(message.from_user.id)}\n'
                                   f'Время рассылки: {db.get_sending_time(message.from_user.id)}:00\n'
                                   f'Тип рассылки: {schedule_mode}', reply_markup=kb.main_keyboard
                                   )
            await state.finish()
        else:
            await bot.send_message(message.from_user.id, 'По такому запросу ничего не найдено, попробуйте снова')


@dp.callback_query_handler(state=RegStages.choosing_teacher)
async def choosing_name(call: types.CallbackQuery, state: FSMContext):
    schedule_mode = ''
    if db.get_sending_mode(call.from_user.id) == '1':
        schedule_mode = 'На текущий день'
    elif db.get_sending_mode(call.from_user.id) == '2':
        schedule_mode = 'На следующий день'
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    db.update_academic_group_name(call.from_user.id, call.data)
    await bot.send_message(call.from_user.id, f'Сохранено!\nВаше ФИО: {profile.pretty_teacher_name(call.from_user.id)}\n'
                                   f'Время рассылки: {db.get_sending_time(call.from_user.id)}:00\n'
                                   f'Тип рассылки: {schedule_mode}', reply_markup=kb.main_keyboard)
    await state.finish()


@dp.callback_query_handler(state=RegStages.choosing_institute)
async def choosing_institute(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data.isnumeric():
            db.update_institute_name(call.from_user.id, call.data)
        else:
            raise Exception
        await bot.send_message(call.from_user.id, f'Теперь выберите специальность',
                               reply_markup=kb.creating_keyboard_specialities(call.from_user.id))
        await RegStages.choosing_speciality.set()
    except:
        await bot.send_message(call.from_user.id, f'Неизвестная ошибка. Попробуйте снова.',
                               reply_markup=kb.creating_keyboard_institutes())


@dp.callback_query_handler(state=RegStages.choosing_speciality)
async def choosing_speciality(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data.isnumeric():
            db.update_speciality_name(call.from_user.id, call.data)
        else:
            raise Exception
        await bot.send_message(call.from_user.id, f'Теперь выберите свою группу',
                               reply_markup=kb.creating_keyboard_groups(call.from_user.id))
        await RegStages.choosing_academic_group.set()
    except:
        await bot.send_message(call.from_user.id, f'Неизвестная ошибка. Попробуйте снова.',
                               reply_markup=kb.creating_keyboard_specialities(call.from_user.id))


@dp.callback_query_handler(state=RegStages.choosing_academic_group)
async def choosing_group(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data.isnumeric():
            db.update_academic_group_name(call.from_user.id, call.data)
        else:
            raise Exception
        await bot.send_message(call.from_user.id, f'Теперь выберите свою подгруппу',
                               reply_markup=kb.subgroup_keyboard)
        await RegStages.choosing_subgroup.set()
    except:
        await bot.send_message(call.from_user.id, f'Неизвестная ошибка. Попробуйте снова.',
                               reply_markup=kb.creating_keyboard_specialities(call.from_user.id))


@dp.callback_query_handler(state=RegStages.choosing_subgroup)
async def choosing_subgroup(call: types.CallbackQuery, state: FSMContext):
    try:
        schedule_mode = ''
        if db.get_sending_mode(call.from_user.id) == '1':
            schedule_mode = 'На текущий день'
        elif db.get_sending_mode(call.from_user.id) == '2':
            schedule_mode = 'На следующий день'
        if call.data.isnumeric():
            db.update_subgroup(call.from_user.id, call.data)
        else:
            raise Exception
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        subgroup = int(db.get_subgroup(call.from_user.id))
        if subgroup == 1 or subgroup == 2:
            subgroup = f"({db.get_subgroup(call.from_user.id)})"
        else:
            subgroup = ''
        await bot.send_message(call.from_user.id, f'Сохранено\n'
        # f'Ваш институт: {profile.pretty_institute_name(call.from_user.id)}\n'
        # f'Ваша специальность: {profile.pretty_speciality_name(call.from_user.id)}\n'
                                                  f'Ваша группа: {profile.pretty_academic_group_name(call.from_user.id)}{subgroup}\n'
                                                  f'Время рассылки: {db.get_sending_time(call.from_user.id)}:00\n'
                                                  f'Тип рассылки: {schedule_mode}',
                               reply_markup=kb.main_keyboard
                               )
        await state.finish()
    except:
        await bot.send_message(call.from_user.id, f'Неизвестная ошибка. Попробуйте снова.',
                               reply_markup=kb.subgroup_keyboard)


@dp.message_handler(commands=['version'])
async def version(message: types.Message):
    await bot.send_message(message.from_user.id, '0.3.0 beta')


@dp.message_handler(commands=['profile'])
async def version(message: types.Message):
    schedule_mode = ''
    if db.get_sending_mode(message.from_user.id) == '1':
        schedule_mode = 'На текущий день'
    elif db.get_sending_mode(message.from_user.id) == '2':
        schedule_mode = 'На следующий день'
    subgroup = int(db.get_subgroup(message.from_user.id))
    if db.get_user_role(message.from_user.id) == '2':
        if subgroup == 1 or subgroup == 2:
            subgroup = f"({db.get_subgroup(message.from_user.id)})"
        else:
            subgroup = ''
        await bot.send_message(message.from_user.id,
                               # f'Ваш институт: {profile.pretty_institute_name(message.from_user.id)}\n'
                               # f'Ваша специальность: {profile.pretty_speciality_name(message.from_user.id)}\n'
                               f'Ваша группа: {profile.pretty_academic_group_name(message.from_user.id)}{subgroup}\n'
                               f'Время рассылки: {db.get_sending_time(message.from_user.id)}:00\n'
                               f'Тип рассылки: {schedule_mode}',
                               reply_markup=kb.profile_keyboard)
    elif db.get_user_role(message.from_user.id) == '1':
        await bot.send_message(message.from_user.id,
                               # f'Ваш институт: {profile.pretty_institute_name(message.from_user.id)}\n'
                               # f'Ваша специальность: {profile.pretty_speciality_name(message.from_user.id)}\n'
                               f'Ваше ФИО: {profile.pretty_teacher_name(message.from_user.id)}\n'
                               f'Время рассылки: {db.get_sending_time(message.from_user.id)}:00\n'
                               f'Тип рассылки: {schedule_mode}',
                               reply_markup=kb.profile_keyboard)


@dp.callback_query_handler(state=RegStages.changing_time)
async def changing_time(call: types.callback_query, state: FSMContext):
    try:
        if call.data.isnumeric():
            db.update_sending_time(call.from_user.id, call.data)
        else:
            raise Exception
        await state.finish()
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await bot.send_message(call.from_user.id,
                               f'Время для рассылки установлено: {db.get_sending_time(call.from_user.id)}:00')
    except:
        await bot.send_message(call.from_user.id, f'Неизвестная ошибка. Попробуйте снова.',
                               reply_markup=kb.creating_hours_keyboard())


@dp.callback_query_handler(state=RegStages.choosing_mode)
async def changing_time(call: types.callback_query, state: FSMContext):
    try:
        if call.data.isnumeric():
            db.update_sending_mode(call.from_user.id, call.data)
        else:
            raise Exception
        await state.finish()
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if db.get_sending_mode(call.from_user.id) == '2':
            await bot.send_message(call.from_user.id,
                                f'Теперь вы получаете рассылку на завтрашний день')
        elif db.get_sending_mode(call.from_user.id) == '1':
            await bot.send_message(call.from_user.id,
                                   f'Теперь вы получаете рассылку на текущий день')

    except:
        await bot.send_message(call.from_user.id, f'Неизвестная ошибка. Попробуйте снова.',
                               reply_markup=kb.schedule_mode)


@dp.message_handler(commands=['stop'])
async def changing_group1(message: types.Message):
    await bot.send_message(message.from_user.id, 'sendind stopped')
    db.update_sending_status(message.from_user.id, False)


@dp.message_handler(commands=['continue'])
async def changing_group1(message: types.Message):
    await bot.send_message(message.from_user.id, 'sendind startred')
    db.update_sending_status(message.from_user.id, True)


@dp.message_handler(commands=['status'])
async def changing_group1(message: types.Message):
    last_send = db.get_all_last_send()
    cnt_succes = 0
    cnt_unsucces = 0
    for i in range(len(last_send)):
        if str(last_send[i][0]) == str(datetime.now().day):
            cnt_succes += 1
        else:
            cnt_unsucces += 1
    await bot.send_message(987073797, f'Успешно получили расписание сегодня: {cnt_succes} пользователей\n'
                                      f'Не получили расписание: {cnt_unsucces} пользователей')


async def get_user_allowed_ids():
    return db.get_allowed_for_sending_users(True)


async def sending():
    while True:
        all_id = await(get_user_allowed_ids())
        try:
            for i in range(len(all_id)):
                user_id = (all_id[i][1])
                day_now = int(datetime.now().date().day)
                hour_now = int(datetime.now().time().hour)
                user_hour = int(db.get_sending_time(user_id))
                try:
                    last_send = int(db.get_last_send(user_id))
                    if user_hour == hour_now and last_send != day_now:
                        try:
                            if db.get_user_role(user_id) == '2':
                                days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота',
                                                'Воскресенье', 'Понедельник']
                                today = datetime.today().weekday()
                                date = datetime.now()
                                if db.get_sending_mode(user_id) == '2':
                                    date = date + timedelta(days=1)
                                    today += 1
                                date = str(date.date())
                                data = ec.api_get_schedule(db.get_academic_group_name(user_id), date)
                                if days_of_week[today] == data[0]['WeekDay']:
                                    await bot.send_message(user_id,
                                                           f'{profile.pretty_schedule_message(user_id)}',
                                                           parse_mode=types.ParseMode.HTML)
                                    db.update_last_send(user_id, day_now)


                                else:
                                    if db.get_sending_mode(user_id) == '1':
                                        await bot.send_message(user_id, 'Сегодня пар нет')
                                    elif db.get_sending_mode(user_id) == '2':
                                        await bot.send_message(user_id, 'Завтра пар нет')
                                    db.update_last_send(user_id, day_now)

                            elif db.get_user_role(user_id) == '1':
                                days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота',
                                                'Воскресенье', 'Понедельник']
                                today = datetime.today().weekday()
                                date = datetime.now()
                                if db.get_sending_mode(user_id) == '2':
                                    date = date + timedelta(days=1)
                                    today += 1
                                date = str(date.date())
                                data = ec.api_get_teacher_schedule(db.get_academic_group_name(user_id), date)
                                if days_of_week[today] == data[0]['WeekDay']:
                                    await bot.send_message(user_id,
                                                           f'{profile.pretty_schedule_message_teacher(user_id)}',
                                                           parse_mode=types.ParseMode.HTML)
                                    db.update_last_send(user_id, day_now)

                                else:
                                    if db.get_sending_mode(user_id) == '1':
                                        await bot.send_message(user_id, 'Сегодня пар нет')
                                    elif db.get_sending_mode(user_id) == '2':
                                        await bot.send_message(user_id, 'Завтра пар нет')
                                    db.update_last_send(user_id, day_now)
                        except Exception as e:
                            await bot.send_message(user_id, 'Простите, не удалось отправить расписание :(')
                            print(e)
                            db.update_last_send(user_id, datetime.now().day)
                    await asyncio.sleep(0.1)
                except:
                    pass
        except:
            # invalid id or 0 allowed users
            pass


async def start_sending():
    task = loop.create_task(sending())
    await asyncio.wait(task)


@dp.callback_query_handler()
async def choosing_speciality(call: types.CallbackQuery):
    if call.data == 'changegroup':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await RegStages.choosing_role.set()
        await bot.send_message(call.from_user.id, 'Для кого будем получать расписание?', reply_markup=kb.student_or_teacher_keyboard)
    elif call.data == 'changetime':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await RegStages.changing_time.set()
        await bot.send_message(call.from_user.id, 'Выберите время для рассылки',
                               reply_markup=kb.creating_hours_keyboard())
    elif call.data == 'changemode':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await RegStages.choosing_mode.set()
        await bot.send_message(call.from_user.id, 'Выберите тип рассылки:', reply_markup=kb.schedule_mode)


@dp.message_handler(state='*')
async def cancel_command(message: types.Message):
    if message.text == 'Изменить данные' or message.text == 'Профиль':
        try:
            schedule_mode = ''
            if db.get_sending_mode(message.from_user.id) == '1':
                schedule_mode = 'На текущий день'
            elif db.get_sending_mode(message.from_user.id) == '2':
                schedule_mode = 'На следующий день'
            subgroup = int(db.get_subgroup(message.from_user.id))
            if db.get_user_role(message.from_user.id) == '2':
                if subgroup == 1 or subgroup == 2:
                    subgroup = f"({db.get_subgroup(message.from_user.id)})"
                else:
                    subgroup = ''
                await bot.send_message(message.from_user.id,
                                       # f'Ваш институт: {profile.pretty_institute_name(message.from_user.id)}\n'
                                       # f'Ваша специальность: {profile.pretty_speciality_name(message.from_user.id)}\n'
                                       f'Ваша группа: {profile.pretty_academic_group_name(message.from_user.id)}{subgroup}\n'
                                       f'Время рассылки: {db.get_sending_time(message.from_user.id)}:00\n'
                                       f'Тип рассылки: {schedule_mode}',
                                       reply_markup=kb.profile_keyboard)
            elif db.get_user_role(message.from_user.id) == '1':
                await bot.send_message(message.from_user.id,
                                       # f'Ваш институт: {profile.pretty_institute_name(message.from_user.id)}\n'
                                       # f'Ваша специальность: {profile.pretty_speciality_name(message.from_user.id)}\n'
                                       f'Ваше ФИО: {profile.pretty_teacher_name(message.from_user.id)}\n'
                                       f'Время рассылки: {db.get_sending_time(message.from_user.id)}:00\n'
                                       f'Тип рассылки: {schedule_mode}',
                                       reply_markup=kb.profile_keyboard)
        except:
            await bot.send_message(message.from_user.id,
                                   f'Не удалось получить данные о пользователе. Попробуйте выбрать группу снова.',
                                   reply_markup=kb.creating_keyboard_institutes())
            await RegStages.choosing_institute.set()
    elif message.text == 'Получить расписание':
        try:
            if db.get_user_role(message.from_user.id) == '2':
                days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье', 'Понедельник']
                today = datetime.today().weekday()
                date = datetime.now()
                if db.get_sending_mode(message.from_user.id) == '2':
                    date = date + timedelta(days=1)
                    today += 1
                date = str(date.date())
                data = ec.api_get_schedule(db.get_academic_group_name(message.from_user.id), date)
                if days_of_week[today] == data[0]['WeekDay']:
                    await bot.send_message(message.from_user.id,
                                           f'{profile.pretty_schedule_message(message.from_user.id)}',
                                           parse_mode=types.ParseMode.HTML)
                else:
                    if db.get_sending_mode(message.from_user.id) == '1':
                        await bot.send_message(message.from_user.id, 'Сегодня пар нет')
                    elif db.get_sending_mode(message.from_user.id) == '2':
                        await bot.send_message(message.from_user.id, 'Завтра пар нет')
            elif db.get_user_role(message.from_user.id) == '1':
                days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье', 'Понедельник']
                today = datetime.today().weekday()
                date = datetime.now()
                if db.get_sending_mode(message.from_user.id) == '2':
                    date = date + timedelta(days=1)
                    today += 1
                date = str(date.date())
                data = ec.api_get_teacher_schedule(db.get_academic_group_name(message.from_user.id), date)
                if days_of_week[today] == data[0]['WeekDay']:
                    await bot.send_message(message.from_user.id,
                                           f'{profile.pretty_schedule_message_teacher(message.from_user.id)}',
                                           parse_mode=types.ParseMode.HTML)
                else:
                    if db.get_sending_mode(message.from_user.id) == '1':
                        await bot.send_message(message.from_user.id, 'Сегодня пар нет')
                    elif db.get_sending_mode(message.from_user.id) == '2':
                        await bot.send_message(message.from_user.id, 'Завтра пар нет')
        except Exception as e:
            if db.get_sending_mode(message.from_user.id) == '1':
                await bot.send_message(message.from_user.id, 'Сегодня пар нет')
            elif db.get_sending_mode(message.from_user.id) == '2':
                await bot.send_message(message.from_user.id, 'Завтра пар нет')
    else:
        await bot.send_message(message.from_user.id, f'type /help')


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_sending())
    except:
        pass

    executor.start_polling(dp, skip_updates=True)

