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

# check existing user in users table
def is_duplicate_user(discord_id):
    cursor.execute(f"SELECT * FROM users WHERE discord_id = {discord_id}")
    return len(cursor.fetchall()) > 0

# add user info to users table
def add_user(user_info):
    if not is_duplicate_user(user_info["discord_id"]):
        cursor.execute(f"INSERT INTO users VALUES('{user_info['name']}', {user_info['discriminator']}, {user_info['discord_id']})")
        schedulebotdb.commit()
        return True
    else:
        return False

# check existing class in schedules table
def class_exists(discord_id, course_id):
    cursor.execute(f"SELECT * FROM schedules WHERE discord_id = {discord_id} AND course_id = '{course_id}'")
    return len(cursor.fetchall()) != 0

# add class info to schedules table
def add_class(discord_id, class_info):
    if not class_exists(discord_id, class_info["course_id"]):
        cursor.execute(f"INSERT INTO schedules VALUES({discord_id}, '{class_info['course_id']}', '{class_info['course_name']}', '{class_info['days_of_week']}', '{class_info['time']}', '{class_info['location']}', '{class_info['professor']}')")
        schedulebotdb.commit()
        return True
    else:
        return False

# gets all classes a user has
def get_all_classes(discord_id):
    cursor.execute(f"SELECT * FROM schedules WHERE discord_id IN (SELECT discord_id FROM users WHERE discord_id = {discord_id})")
    return cursor.fetchall()

# remove a class from schedules table
def remove_class(discord_id, course_id):
    if class_exists(discord_id, course_id):
        cursor.execute(f"DELETE FROM schedules WHERE course_id = '{course_id}' AND discord_id = {discord_id}")
        schedulebotdb.commit()
        return True
    else:
        return False

# get schedules table columns
def get_table_columns(table_name):
    cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'schedulebot' AND TABLE_NAME = '{table_name}' ORDER BY ORDINAL_POSITION")
    return cursor.fetchall()

# update a class entry already existing in schedules table
def update_class(discord_id, course_id, column_name, column_value):
    cursor.execute(f"UPDATE schedules SET {column_name} = '{column_value}' WHERE discord_id = {discord_id} AND course_id = '{course_id}'")
    schedulebotdb.commit()