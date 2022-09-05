import config

import requests

def get_institutes_list():
    response = requests.post(config.GETINSTITUTES_URL)
    data = response.json()
    return data


def get_specialities_list(institute_id):
    params = {'instituteId': institute_id, 'branchId': '1'}
    response = requests.post(config.GETSPECIALITIES_URL, params=params)
    data = response.json()
    return data


def get_academic_group_list(institute_id, speciality):
    params = {'instituteId': institute_id, 'branchId': '1', 'specialty': speciality}
    response = requests.post(config.GETACADEMICGROUPS_URL, params=params)
    data = response.json()
    return data


def api_get_schedule(group_id, date):
    #group_id = '16147'
    #target_type = '2'
    #date = '2022-02-16'
    params = {'id': group_id, 'targetType': '2', 'date': date}
    response = requests.post(config.GETSCHEDULE_URL, params=params)
    data = response.json()
    return data


def api_get_teacher_schedule(teacher_id, date):
    #group_id = '16147'
    #target_type = '1'
    #date = '2022-02-16'
    params = {'id': teacher_id, 'targetType': '1', 'date': date}
    response = requests.post(config.GETSCHEDULE_URL, params=params)
    data = response.json()
    return data
