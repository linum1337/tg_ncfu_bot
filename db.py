import sqlite3


class db:

    def __init__(self, db):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()

    def get_allowed_for_sending_users(self, status_sending=True):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `users_info` WHERE `status_sending` = ?",
                                       (status_sending,)).fetchall()

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `users_info` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id, registration_stage=True):
        with self.connection:
            return self.cursor.execute("INSERT INTO `users_info` (`user_id`, `registration_stage`) VALUES(?,?)",
                                       (user_id, registration_stage))

    # updating and getting institute_name
    def update_institute_name(self, user_id, institute_name):
        with self.connection:
            return self.cursor.execute("UPDATE `users_info` SET `institute_name` = ? WHERE `user_id` = ?",
                                       (institute_name, user_id))

    def get_institute_name(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT `institute_name` FROM `users_info` WHERE `user_id` = ?',
                                         (user_id,)).fetchall()
            for row in result:
                institute_name = str(row[0])
            return str(institute_name)

    # updating and getting speciality_name
    def update_speciality_name(self, user_id, speciality_name):
        with self.connection:
            return self.cursor.execute("UPDATE `users_info` SET `speciality_name` = ? WHERE `user_id` = ?",
                                       (speciality_name, user_id))

    def get_speciality_name(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT `speciality_name` FROM `users_info` WHERE `user_id` = ?',
                                         (user_id,)).fetchall()
            for row in result:
                speciality_name = str(row[0])
            return str(speciality_name)

    # updating and getting speciality_name
    def update_academic_group_name(self, user_id, institute_name):
        with self.connection:
            return self.cursor.execute("UPDATE `users_info` SET `group_name` = ? WHERE `user_id` = ?",
                                       (institute_name, user_id))

    def get_academic_group_name(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT `group_name` FROM `users_info` WHERE `user_id` = ?',
                                         (user_id,)).fetchall()
            for row in result:
                institute_name = str(row[0])
            return str(institute_name)

    # get - update sending_time
    def update_sending_time(self, user_id, time):
        with self.connection:
            return self.cursor.execute("UPDATE `users_info` SET `sending_time` = ? WHERE `user_id` = ?",
                                       (time, user_id))

    def get_sending_time(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT `sending_time` FROM `users_info` WHERE `user_id` = ?',
                                         (user_id,)).fetchall()
            for row in result:
                time = str(row[0])
            return str(time)

    # update - get sendind
    def update_sending_status(self, user_id, status):
        with self.connection:
            return self.cursor.execute("UPDATE `users_info` SET `status_sending` = ? WHERE `user_id` = ?",
                                       (status, user_id))

    def get_sending_status(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT `status_sending` FROM `users` WHERE `user_id` = ?',
                                         (user_id,)).fetchall()
            for row in result:
                status = str(row[0])
            return str(status)
    
    # get - update sending_mode 1-today 2-tomorrow
    def update_sending_mode(self, user_id, mode):
        with self.connection:
            return self.cursor.execute("UPDATE `users_info` SET `sending_mode` = ? WHERE `user_id` = ?",
                                       (mode, user_id))

    def get_sending_mode(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT `sending_mode` FROM `users_info` WHERE `user_id` = ?',
                                         (user_id,)).fetchall()
            for row in result:
                mode = str(row[0])
            return str(mode)
            
    # update - get last_send
    def update_last_send(self, user_id, time):
        with self.connection:
            return self.cursor.execute("UPDATE `users_info` SET `last_send` = ? WHERE `user_id` = ?",
                                       (time, user_id))

    def get_last_send(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT `last_send` FROM `users_info` WHERE `user_id` = ?',
                                         (user_id,)).fetchall()
            for row in result:
                time = str(row[0])
            return str(time)

    # update - get subgroup
    def update_subgroup(self, user_id, subgroup):
        with self.connection:
            return self.cursor.execute("UPDATE `users_info` SET `subgroup` = ? WHERE `user_id` = ?",
                                       (subgroup, user_id))

    def get_subgroup(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT `subgroup` FROM `users_info` WHERE `user_id` = ?',
                                         (user_id,)).fetchall()
            for row in result:
                time = str(row[0])
            return str(time)

    # update user_role(teacher(1) or student(2)
    def update_user_role(self, user_id, role):
        with self.connection:
            return self.cursor.execute("UPDATE `users_info` SET `user_role` = ? WHERE `user_id` = ?",
                                       (role, user_id))

    def get_user_role(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT `user_role` FROM `users_info` WHERE `user_id` = ?',
                                         (user_id,)).fetchall()
            for row in result:
                role = str(row[0])
            return str(role)

    # ///
    def update_registration_stage(self, user_id, registration_stage):
        with self.connection:
            return self.cursor.execute("UPDATE `users_info` SET `registration_stage` = ? WHERE `user_id` = ?",
                                       (registration_stage, user_id))

    # datetime from first start
    def set_using_began(self, user_id, time):
        with self.connection:
            return self.cursor.execute("UPDATE `users_info` SET `using_began` = ? WHERE `user_id` = ?", (time, user_id))

    # all id
    def get_all_id(self):
        result = self.cursor.execute('SELECT `user_id` FROM `users_info`').fetchall()
        return result

    # all sending_status
    def get_all_last_send(self):
        result = self.cursor.execute('SELECT `last_send` FROM `users_info`').fetchall()
        return result

    def close(self):
        self.connection.close()