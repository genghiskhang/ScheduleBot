import mysql.connector
import json
from pathlib import Path
from assets import botexceptions as be

with open(Path("assets/") / "dbcredentials.json") as file:
    login = json.load(file)

"""
is_duplicate_user

Checks if the user already exists
in the database
"""
def is_duplicate_user(discord_id):
    schedulebotdb = mysql.connector.connect(host=login["host"], user=login["user"], password=login["password"], database=login["database"])
    cursor = schedulebotdb.cursor()
    cursor.execute(f"SELECT * FROM users WHERE discord_id = {discord_id}")
    if len(cursor.fetchall()) != 0:
        schedulebotdb.close()
        cursor.close()
        raise be.UserExistsException()
    schedulebotdb.close()
    cursor.close()

"""
add_user

Adds a user and their info to the
database
"""
def add_user(user_info):
    schedulebotdb = mysql.connector.connect(host=login["host"], user=login["user"], password=login["password"], database=login["database"])
    cursor = schedulebotdb.cursor()
    is_duplicate_user(user_info["discord_id"])
    cursor.execute(f"INSERT INTO users VALUES('{user_info['name']}', '{user_info['discriminator']}', {user_info['discord_id']}, {user_info['max_courses']}, 0)")
    schedulebotdb.commit()
    schedulebotdb.close()
    cursor.close()

"""
remove_user

Removes a user and their info from
the database
"""
def remove_user(discord_id):
    schedulebotdb = mysql.connector.connect(host=login["host"], user=login["user"], password=login["password"], database=login["database"])
    cursor = schedulebotdb.cursor()
    cursor.execute(f"DELETE FROM users WHERE discord_id = {discord_id}")
    schedulebotdb.commit()
    schedulebotdb.close()
    cursor.close()

"""
update_user

Updates a user and their info
"""
def update_user(user_info):
    schedulebotdb = mysql.connector.connect(host=login["host"], user=login["user"], password=login["password"], database=login["database"])
    cursor = schedulebotdb.cursor()
    cursor.execute(f"UPDATE users SET name = '{user_info['name']}', discriminator = '{user_info['discriminator']}' WHERE discord_id = {user_info['discord_id']}")
    schedulebotdb.commit()
    schedulebotdb.close()
    cursor.close()

"""
course_exists

Checks if the course already exists
in the database
"""
def course_exists(discord_id, course_id):
    schedulebotdb = mysql.connector.connect(host=login["host"], user=login["user"], password=login["password"], database=login["database"])
    cursor = schedulebotdb.cursor()
    cursor.execute(f"SELECT * FROM schedules WHERE discord_id = {discord_id} AND course_id = '{course_id}'")
    if len(cursor.fetchall()) != 0:
        schedulebotdb.close()
        cursor.close()
        raise be.CourseExistsException()
    schedulebotdb.close()
    cursor.close()

"""
add_course

Adds a course and its info to the
database
"""
def add_course(discord_id, course_info):
    schedulebotdb = mysql.connector.connect(host=login["host"], user=login["user"], password=login["password"], database=login["database"])
    cursor = schedulebotdb.cursor()
    course_exists(discord_id, course_info["course_id"])
    cursor.execute(f"INSERT INTO schedules VALUES({discord_id}, '{course_info['course_id']}', '{course_info['course_name']}', {course_info['section_id']}, '{course_info['days_of_week']}', '{course_info['time']}', '{course_info['location']}', '{course_info['professor']}')")
    schedulebotdb.commit()
    schedulebotdb.close()
    cursor.close()

"""
get_all_courses_info

Gets all the courses a user has
and its info
"""
def get_all_courses_info(discord_id):
    schedulebotdb = mysql.connector.connect(host=login["host"], user=login["user"], password=login["password"], database=login["database"])
    cursor = schedulebotdb.cursor()
    courses = []
    cursor.execute(f"SELECT course_id, course_name, section_id, days_of_week, time, location, professor FROM schedules WHERE discord_id IN (SELECT discord_id FROM users WHERE discord_id = {discord_id})")
    for course in cursor.fetchall():
        courses.append({
            "course_id":course[0],
            "course_name":course[1],
            "section_id":course[2],
            "days_of_week":course[3],
            "time":course[4],
            "location":course[5],
            "professor":course[6]
        })
    schedulebotdb.close()
    cursor.close()
    return courses

"""
remove_course

Removes a course and its info from
the database
"""
def remove_course(discord_id, course_id):
    schedulebotdb = mysql.connector.connect(host=login["host"], user=login["user"], password=login["password"], database=login["database"])
    cursor = schedulebotdb.cursor()
    cursor.execute(f"DELETE FROM schedules WHERE course_id = '{course_id}' AND discord_id = {discord_id}")
    schedulebotdb.commit()
    schedulebotdb.close()
    cursor.close()

"""
get_table_columns

Gets the name of a table's columns
"""
def get_table_columns(table_name):
    schedulebotdb = mysql.connector.connect(host=login["host"], user=login["user"], password=login["password"], database=login["database"])
    cursor = schedulebotdb.cursor()
    cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'schedulebot' AND TABLE_NAME = '{table_name}' ORDER BY ORDINAL_POSITION")
    columns = cursor.fetchall()[1:]
    schedulebotdb.close()
    cursor.close()
    return columns

"""
update_course

Updates a single column in an existing
course
"""
def update_course(discord_id, course_id, column_name, column_value):
    schedulebotdb = mysql.connector.connect(host=login["host"], user=login["user"], password=login["password"], database=login["database"])
    cursor = schedulebotdb.cursor()
    cursor.execute(f"UPDATE schedules SET {column_name} = '{column_value}' WHERE discord_id = {discord_id} AND course_id = '{course_id}'")
    schedulebotdb.commit()
    schedulebotdb.close()
    cursor.close()

"""
get_max_courses

Get a user's max courses
"""
def get_max_courses(discord_id):
    schedulebotdb = mysql.connector.connect(host=login["host"], user=login["user"], password=login["password"], database=login["database"])
    cursor = schedulebotdb.cursor()
    cursor.execute(f"SELECT max_courses FROM users WHERE discord_id = {discord_id}")
    max_courses = cursor.fetchall()[0][0]
    schedulebotdb.close()
    cursor.close()
    return max_courses

"""
update_max_courses

Updates a user's max courses
"""
def update_max_courses(discord_id, new_max):
    schedulebotdb = mysql.connector.connect(host=login["host"], user=login["user"], password=login["password"], database=login["database"])
    cursor = schedulebotdb.cursor()
    if new_max < len(get_all_courses_info(discord_id)):
        schedulebotdb.close()
        cursor.close()
        raise be.InvalidMaxCoursesException()
    cursor.execute(f"UPDATE users SET max_courses = {new_max} WHERE discord_id = {discord_id}")
    schedulebotdb.commit()
    schedulebotdb.close()
    cursor.close()

"""
get_boops

Gets the total number of times a
user has booped
"""
def get_boops(discord_id):
    schedulebotdb = mysql.connector.connect(host=login["host"], user=login["user"], password=login["password"], database=login["database"])
    cursor = schedulebotdb.cursor()
    cursor.execute(f"SELECT boops FROM users WHERE discord_id = {discord_id}")
    boops = cursor.fetchall()[0][0]
    schedulebotdb.close()
    cursor.close()
    return boops

"""
increment_boops

Increments a user's boops
"""
def increment_boops(discord_id):
    schedulebotdb = mysql.connector.connect(host=login["host"], user=login["user"], password=login["password"], database=login["database"])
    cursor = schedulebotdb.cursor()
    boops = get_boops(discord_id) + 1
    cursor.execute(f"UPDATE users SET boops = {boops} WHERE discord_id = {discord_id}")
    schedulebotdb.commit()
    schedulebotdb.close()
    cursor.close()