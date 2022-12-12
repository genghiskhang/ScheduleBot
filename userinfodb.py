import mysql.connector
import json
from pathlib import Path

with open(Path("assets/") / "dbcredentials.json") as file:
    login = json.load(file)

schedulebotdb = mysql.connector.connect(
    host = login["host"],
    user = login["user"],
    password = login["password"],
    database = login["database"]
)
cursor = schedulebotdb.cursor()

"""
is_duplicate_user

Checks if the user already exists
in the database
"""
def is_duplicate_user(discord_id):
    cursor.execute(f"SELECT * FROM users WHERE discord_id = {discord_id}")
    return len(cursor.fetchall()) > 0

"""
add_user

Adds a user and their info to the
database
"""
def add_user(user_info):
    if not is_duplicate_user(user_info["discord_id"]):
        cursor.execute(f"INSERT INTO users VALUES('{user_info['name']}', '{user_info['discriminator']}', {user_info['discord_id']}, {user_info['max_courses']})")
        schedulebotdb.commit()
        return True
    else:
        return False

"""
remove_user

Removes a user and their info from
the database
"""
def remove_user(discord_id):
    cursor.execute(f"DELETE FROM users WHERE discord_id = {discord_id}")
    schedulebotdb.commit()

"""
update_user

Updates a user and their info
"""
def update_user(user_info):
    cursor.execute(f"UPDATE users SET name = '{user_info['name']}' WHERE discord_id = {user_info['discord_id']}")
    schedulebotdb.commit()
    cursor.execute(f"UPDATE users SET discriminator = {user_info['discriminator']} WHERE discord_id = {user_info['discord_id']}")
    schedulebotdb.commit()

"""
course_exists

Checks if the course already exists
in the database
"""
def course_exists(discord_id, course_id):
    cursor.execute(f"SELECT * FROM schedules WHERE discord_id = {discord_id} AND course_id = '{course_id}'")
    return len(cursor.fetchall()) != 0

"""
add_course

Adds a course and its info to the
database
"""
def add_course(discord_id, course_info):
    if not course_exists(discord_id, course_info["course_id"]):
        cursor.execute(f"INSERT INTO schedules VALUES({discord_id}, '{course_info['course_id']}', '{course_info['course_name']}', '{course_info['days_of_week']}', '{course_info['time']}', '{course_info['location']}', '{course_info['professor']}')")
        schedulebotdb.commit()
        return True
    else:
        return False

"""
get_all_courses_info

Gets all the courses a user has
and its info
"""
def get_all_courses_info(discord_id):
    courses = []
    cursor.execute(f"SELECT course_id, course_name, days_of_week, time, location, professor FROM schedules WHERE discord_id IN (SELECT discord_id FROM users WHERE discord_id = {discord_id})")
    for course in cursor.fetchall():
        courses.append({
            "course_id":course[0],
            "course_name":course[1],
            "days_of_week":course[2],
            "time":course[3],
            "location":course[4],
            "professor":course[5]
        })
    return courses

"""
remove_course

Removes a course and its info from
the database
"""
def remove_course(discord_id, course_id):
    if course_exists(discord_id, course_id):
        cursor.execute(f"DELETE FROM schedules WHERE course_id = '{course_id}' AND discord_id = {discord_id}")
        schedulebotdb.commit()
        return True
    else:
        return False

"""
get_table_columns

Gets the name of a table's columns
"""
def get_table_columns(table_name):
    cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'schedulebot' AND TABLE_NAME = '{table_name}' ORDER BY ORDINAL_POSITION")
    return cursor.fetchall()[1:]

"""
update_course

Updates a single column in an existing
course
"""
def update_course(discord_id, course_id, column_name, column_value):
    cursor.execute(f"UPDATE schedules SET {column_name} = '{column_value}' WHERE discord_id = {discord_id} AND course_id = '{course_id}'")
    schedulebotdb.commit()

"""
get_max_courses

Get a user's max courses
"""
def get_max_courses(discord_id):
    cursor.execute(f"SELECT max_courses FROM users WHERE discord_id = {discord_id}")
    return cursor.fetchall()[0][0]

"""
update_max_courses

Updates a user's max courses
"""
def update_max_courses(discord_id, new_max):
    if new_max >= len(get_all_courses_info(discord_id)):
        cursor.execute(f"UPDATE users SET max_courses = {new_max} WHERE discord_id = {discord_id}")
        schedulebotdb.commit()
        return True
    else:
        return False

"""
get_boops

Gets the total number of times a
user has booped
"""
def get_boops(discord_id):
    cursor.execute(f"SELECT boops FROM users WHERE discord_id = {discord_id}")
    return cursor.fetchall()[0][0]

"""
increment_boops

Increments a user's boops
"""
def increment_boops(discord_id):
    boops = get_boops(discord_id) + 1
    cursor.execute(f"UPDATE users SET boops = {boops} WHERE discord_id = {discord_id}")
    schedulebotdb.commit()