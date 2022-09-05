from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

import config
import ecampusapi as ec
from db import db
import requests
from bs4 import BeautifulSoup
db = db(config.DB_PATH)


def creating_keyboard_institutes():
    institutes_keyboard = InlineKeyboardMarkup(row_width=2)
    institutes_list = ec.get_institutes_list()
    for i in range(0, len(institutes_list)-2, 2):
        institute_name = str(institutes_list[i]['ShortName'])
        institute_name2 = str(institutes_list[i+1]['ShortName'])
        button = InlineKeyboardButton(text=f'{institute_name.replace(" ", "")}', callback_data=str(institutes_list[i]['Id']))
        button2 = InlineKeyboardButton(text=f'{institute_name2.replace(" ", "")}', callback_data=str(institutes_list[i+1]['Id']))
        institutes_keyboard.row(button, button2)
    return institutes_keyboard


def creating_keyboard_specialities(user_id):
    specialities_keyboard = InlineKeyboardMarkup(row_width=2)
    specialities_list = ec.get_specialities_list(db.get_institute_name(user_id))
    for i in range(len(specialities_list)):
        spec_name = str(specialities_list[i]['Name'])
        button = InlineKeyboardButton(text=f'{spec_name}', callback_data=f'{i}')
        specialities_keyboard.add(button)
    return specialities_keyboard


def creating_keyboard_groups(user_id):
    specialities_keyboard = InlineKeyboardMarkup(row_width=2)
    institute_id = db.get_institute_name(user_id)
    speciality_number = int(db.get_speciality_name(user_id))
    specialities_list = ec.get_specialities_list(institute_id)
    speciality_name = str(specialities_list[speciality_number]['Name'])
    academic_group_list = ec.get_academic_group_list(institute_id, speciality_name)
    for i in range(len(academic_group_list[0]['Value'])):
        group_name = str(academic_group_list[0]['Value'][i]['Name'])
        button = InlineKeyboardButton(text=group_name, callback_data=f"{str(academic_group_list[0]['Value'][i]['Id'])}")
        specialities_keyboard.add(button)
    return specialities_keyboard


def creating_hours_keyboard():
    hours_keyboard = InlineKeyboardMarkup(row_width=4)
    for i in range(0, 24, 4):
        button = InlineKeyboardButton(text=f'{i}:00', callback_data=str(i))
        button2 = InlineKeyboardButton(text=f'{i+1}:00', callback_data=str(i+1))
        button3 = InlineKeyboardButton(text=f'{i+2}:00', callback_data=str(i+2))
        button4 = InlineKeyboardButton(text=f'{i+3}:00', callback_data=str(i+3))
        hours_keyboard.row(button, button2, button3, button4)
    return hours_keyboard


def creating_teachers_list(search_name):
    full_page = requests.get(f'{config.SEARCH_URL}{search_name}')

    soup = BeautifulSoup(full_page.text, "lxml")

    teachers_info = soup.find('ul', class_="loose").findAll('a')
    teachers_keyboard = InlineKeyboardMarkup(row_width=4)
    for i in teachers_info:
        id = i.get('href').replace('/schedule/teacher/', '')
        name = i.text
        buttont = InlineKeyboardButton(text=str(name), callback_data=str(id))
        teachers_keyboard.add(buttont)
    return teachers_keyboard


main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_profile = KeyboardButton('Изменить данные')
button_getschedule = KeyboardButton('Получить расписание')
main_keyboard.insert(button_profile)
main_keyboard.insert(button_getschedule)


profile_keyboard = InlineKeyboardMarkup(row_width=1)
button_changegroup = InlineKeyboardButton(text='Изменить академические данные', callback_data='changegroup')
button_changetime = InlineKeyboardButton(text='Изменить заданное время', callback_data='changetime')
button_changemode = InlineKeyboardButton(text='Изменить тип рассылки', callback_data='changemode')
profile_keyboard.insert(button_changegroup)
profile_keyboard.insert(button_changetime)
profile_keyboard.insert(button_changemode)


subgroup_keyboard = InlineKeyboardMarkup()
button_1sg = InlineKeyboardButton(text='1', callback_data='1')
button_2sg = InlineKeyboardButton(text='2', callback_data='2')
button_nosg = InlineKeyboardButton(text='Нет', callback_data='0')
subgroup_keyboard.row(button_1sg, button_2sg)
subgroup_keyboard.add(button_nosg)


schedule_mode = InlineKeyboardMarkup(row_width=1)
button_1mode = InlineKeyboardButton(text='Присылать расписание на сегодня', callback_data='1')
button_2mode = InlineKeyboardButton(text='Присылать расписание на завтра', callback_data='2')
schedule_mode.insert(button_1mode)
schedule_mode.insert(button_2mode)


student_or_teacher_keyboard = InlineKeyboardMarkup(row_width=1)
button_teacher = InlineKeyboardButton(text='Преподаватель', callback_data='1')
button_student = InlineKeyboardButton(text='Студент', callback_data='2')
student_or_teacher_keyboard.insert(button_teacher)
student_or_teacher_keyboard.insert(button_student)