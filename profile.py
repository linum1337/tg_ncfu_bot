from db import db
import ecampusapi as ec
import config
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

db = db(config.DB_PATH)


def pretty_institute_name(user_id):
    institutes_list = ec.get_institutes_list()
    for i in range(len(institutes_list)):
        if (str(institutes_list[i]['Id'])) == db.get_institute_name(user_id):
            return str(institutes_list[i]['Name'])


def pretty_speciality_name(user_id):
    specialities_list = ec.get_specialities_list(db.get_institute_name(user_id))
    return specialities_list[int(db.get_speciality_name(user_id))]['Name']


def pretty_academic_group_name(user_id):
    academic_group_list = ec.get_academic_group_list(db.get_institute_name(user_id), pretty_speciality_name(user_id))
    for i in range(len(academic_group_list[0]['Value'])):
        if (str(academic_group_list[0]['Value'][i]['Id'])) == db.get_academic_group_name(user_id):
            return str(academic_group_list[0]['Value'][i]['Name'])


def pretty_teacher_name(user_id):
    url = config.SCHEDULETEACHER_URL
    full_page = requests.get(f'{url}{db.get_academic_group_name(user_id)}')
    soup = BeautifulSoup(full_page.text, "lxml")
    return soup.find(class_="caption").text


def pretty_schedule_message(user_id):
    group_id = db.get_academic_group_name(user_id)
    date = datetime.now()
    if db.get_sending_mode(user_id) == '2':
        date = date + timedelta(days=1)
    date = str(date.date())
    try:
        schedule_message = ''
        schedule_data = ec.api_get_schedule(group_id, date)
        for i in range(len(schedule_data[0]['Lessons'])):
            lesson_subgroup = schedule_data[0]['Lessons'][i]['Groups'][0]['Subgroup']
            if len(str(lesson_subgroup)) > 3:
                lesson_subgroup = None
            if lesson_subgroup:
                if str(lesson_subgroup) == f'({str(db.get_subgroup(user_id))})':
                    data_begin = str(schedule_data[0]['Lessons'][i]['TimeBegin'])
                    data_end = str(schedule_data[0]['Lessons'][i]['TimeEnd'])
                    time_begin = datetime.strptime(data_begin, '%Y-%m-%dT%H:%M:%S').time()
                    time_end = datetime.strptime(data_end, '%Y-%m-%dT%H:%M:%S').time()
                    time_begin = time_begin.strftime('%H:%M')
                    time_end = time_end.strftime('%H:%M')
                    pair_number = str(schedule_data[0]['Lessons'][i]['PairNumberStart'])
                    lesson_type = str(schedule_data[0]['Lessons'][i]['LessonType'])
                    pair_name = str(schedule_data[0]['Lessons'][i]['Discipline'])
                    teacher_name = str(schedule_data[0]['Lessons'][i]['Teacher']['Name'])
                    aud = str(schedule_data[0]['Lessons'][i]['Aud']['Name'])
                    schedule_message += f"<b>{pair_number}</b>" + '. ' + aud + ' ' + lesson_type + '\n' + \
                                        f"<b>{pair_name}</b>" + '\n' + teacher_name + '\n' + time_begin + '-' + \
                                        time_end + '\n\n'
                else:
                    pass
            else:
                data_begin = str(schedule_data[0]['Lessons'][i]['TimeBegin'])
                data_end = str(schedule_data[0]['Lessons'][i]['TimeEnd'])
                time_begin = datetime.strptime(data_begin, '%Y-%m-%dT%H:%M:%S').time()
                time_end = datetime.strptime(data_end, '%Y-%m-%dT%H:%M:%S').time()
                time_begin = time_begin.strftime('%H:%M')
                time_end = time_end.strftime('%H:%M')
                pair_number = str(schedule_data[0]['Lessons'][i]['PairNumberStart'])
                lesson_type = str(schedule_data[0]['Lessons'][i]['LessonType'])
                pair_name = str(schedule_data[0]['Lessons'][i]['Discipline'])
                teacher_name = str(schedule_data[0]['Lessons'][i]['Teacher']['Name'])
                aud = str(schedule_data[0]['Lessons'][i]['Aud']['Name'])
                schedule_message += f"<b>{pair_number}</b>" + '. ' + aud + ' ' + lesson_type + '\n' + \
                                    f"<b>{pair_name}</b>" + '\n' + teacher_name + '\n' + time_begin + '-' + \
                                    time_end + '\n\n'
        subgroup = ''
        if db.get_subgroup(user_id) == 1 or 2:
            subgroup = f"({db.get_subgroup(user_id)})"
        return f"Расписание для {schedule_data[0]['Lessons'][0]['Groups'][0]['Name']}{subgroup} на {date}\n\n" + schedule_message
    except:
        return('Не удалось получить расписание')


def pretty_schedule_message_teacher(user_id):
    group_id = db.get_academic_group_name(user_id)
    date = datetime.now()
    if db.get_sending_mode(user_id) == '2':
        date = date + timedelta(days=1)
    date = str(date.date())
    try:
        schedule_message = ''
        schedule_data = ec.api_get_teacher_schedule(group_id, date)
        for i in range(len(schedule_data[0]['Lessons'])):
            data_begin = str(schedule_data[0]['Lessons'][i]['TimeBegin'])
            data_end = str(schedule_data[0]['Lessons'][i]['TimeEnd'])
            time_begin = datetime.strptime(data_begin, '%Y-%m-%dT%H:%M:%S').time()
            time_end = datetime.strptime(data_end, '%Y-%m-%dT%H:%M:%S').time()
            time_begin = time_begin.strftime('%H:%M')
            time_end = time_end.strftime('%H:%M')
            pair_number = str(schedule_data[0]['Lessons'][i]['PairNumberStart'])
            group_name = ''
            subgroup = ''
            if len(schedule_data[0]['Lessons'][i]['Groups']) > 1:
                for j in range(len(schedule_data[0]['Lessons'][i]['Groups'])-1):
                    subgroup = str(schedule_data[0]['Lessons'][i]['Groups'][j]['Subgroup'])
                    group_name += str(schedule_data[0]['Lessons'][i]['Groups'][j]['Name'])+subgroup+', '
                group_name += str(schedule_data[0]['Lessons'][i]['Groups'][len(schedule_data[0]['Lessons'][i]['Groups'])-1]['Name']) + subgroup
            else:
                subgroup = str(schedule_data[0]['Lessons'][i]['Groups'][0]['Subgroup'])
                group_name = str(schedule_data[0]['Lessons'][i]['Groups'][0]['Name']) + subgroup
            lesson_type = str(schedule_data[0]['Lessons'][i]['LessonType'])
            pair_name = str(schedule_data[0]['Lessons'][i]['Discipline'])
            teacher_name = str(schedule_data[0]['Lessons'][i]['Teacher']['Name'])
            aud = str(schedule_data[0]['Lessons'][i]['Aud']['Name'])
            schedule_message += f"<b>{pair_number}</b>" + '. ' + aud + ' ' + lesson_type + f"<b>{group_name}</b>" + '\n'\
                                f"<b>{pair_name}</b>" + '\n' + time_begin + '-' + \
                                time_end + '\n\n'
        return f"{pretty_teacher_name(user_id)}\nРасписание на {date}\n\n" + schedule_message
    except Exception as e:
        return(e)