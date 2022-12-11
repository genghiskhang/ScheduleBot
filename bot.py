import discord
from discord.ext import commands
import re
import asyncio
from pathlib import Path
import time
import userinfodb as db

prefix = "-"
token = open(Path("assets/") / "token.txt", "r").readline().strip()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.remove_command("help")

STARTING_MAX_COURSES = 5

"""
Event
on_ready

Bot initialization
"""
@bot.event
async def on_ready():
    print(" ____                        __              \n"+
        "/\  _`\                     /\ \               \n"+
        "\ \ \L\ \     __     __     \_\ \  __  __      \n"+
        " \ \ ,  /   /\"__`\ /\"__`\   /\"_` \/\ \/\ \  \n"+
        "  \ \ \ \  /\  __//\ \L\.\_/\ \L\ \ \ \_\ \    \n"+
        "   \ \_\ \_\ \____\ \__/.\_\ \___,_\/`____ \   \n"+
        "    \/_/\/ /\/____/\/__/\/_/\/__,_ /`/___/> \\ \n"+
        "                                       /\___/  \n"+
        "                                       \/__/   \n")

"""
Event
on_member_join

Adds the info of the user that
joined to the database
"""
@bot.event
async def on_member_join(member):
    user_info = {
        "name":member.name,
        "discriminator":member.discriminator,
        "discord_id":member.id,
        "max_courses":STARTING_MAX_COURSES
    }
    db.add_user(user_info)

"""
Event
on_member_update
"""
@bot.event
async def on_member_update(member):
    pass

"""
Event
on_member_remove
"""
@bot.event
async def on_member_remove(member):
    db.remove_user(member.id)

"""
Command
wipe_user_messages_from

Wipes all the messages sent by a user in
a specific channel up to a certain amount
"""
@bot.command()
async def wipe_user_messages_from(ctx, user_id, channel_id, limit):
    if ctx.author.guild_permissions.administrator:
        try:
            await ctx.send("Start processing...")
            start_time = int(time.time())
            channel_name = ""
            for channel in ctx.guild.channels:
                if channel.id == int(channel_id):
                    channel_name = channel.name

            user_message_id = []
            channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
            async for message in channel.history(limit=int(limit)):
                if message.author.id == int(user_id):
                    user_message_id.append(message.id)
            processing_time = int(time.time() - start_time)
            await ctx.send(f"Finished processing {len(user_message_id)} of user's messages (Time: {int(processing_time / (60 * 60))}h {int((processing_time % (60 * 60)) / 60)}m {(processing_time % (60 * 60)) % 60}s)\nStart deletion...")

            for message_id in user_message_id:
                try:
                    msg = await channel.fetch_message(message_id)
                    await msg.delete()
                except:
                    pass
            end_time = int(time.time() - start_time)
            await ctx.send(f"Finished deletion (Time: {int(end_time / (60 * 60))}h {int((end_time % (60 * 60)) / 60)}m {(end_time % (60 * 60)) % 60}s)")
            await ctx.send(f"{len(user_message_id)} Messages Deleted ")
        except Exception as e:
            await ctx.send("Something went wrong...")
            await ctx.send(f"Error: {e}")
    else:
        await ctx.send("You do not have permissions to use this command")

"""
Command
help

Overrided help function
"""
@bot.command()
async def help(ctx):
    file = discord.File(Path("assets") / "thumbnail.png")
    embed = discord.Embed(
        title = "ScheduleBot Commands",
        color = discord.Color.green()
    )
    embed.set_thumbnail(url="attachment://thumbnail.png")
    embed.add_field(name="All Users", value="boop\nshow_courses\nadd_course\nremove_course\nupdatae_course\n", inline=False)
    embed.add_field(name="Admin", value="show_all_members\nadd_all_users\nwipe_user_messages_from\ncheck_api_calls\n", inline=False)
    await ctx.send(file=file, embed=embed)

"""
Command
boop

Boop!
"""
@bot.command()
async def boop(ctx):
    db.increment_boops(ctx.author.id)
    await ctx.send("Boop!")
    await ctx.send(f"You have booped a total of {db.get_boops(ctx.author.id)}")

"""
Command [ADMIN]
show_all_members

Displays the name and user id
of every member in the server
"""
@bot.command()
async def show_all_members(ctx):
    if ctx.author.guild_permissions.administrator:
        members = "\n".join([f"{member.name}#{member.discriminator} - {member.id} - is_bot:{member.bot}" for member in ctx.channel.guild.members])
        embed = discord.Embed(
            title = "Members List",
            description = members,
            color = discord.Color.fuchsia()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("You do not have permissions to use this command")

"""
Command [ADMIN]
add_all_users

Adds the info of all the current
members to the database if not
already in there
"""
@bot.command()
async def add_all_users(ctx):
    if ctx.author.guild_permissions.administrator:
        for member in ctx.channel.guild.members:
            if not member.bot:
                user_info = {
                    "name":member.name,
                    "discriminator":member.discriminator,
                    "discord_id":member.id,
                    "max_courses":STARTING_MAX_COURSES
                }
                db.add_user(user_info)
        await ctx.send("All users added successfully")
    else:
        await ctx.send("You do not have permissions to use this command")

"""
Command [ADMIN]
update_max_courses

Updates a user's max courses
"""
@bot.command()
async def update_max_courses(ctx, user:discord.Member):
    def user_check(m):
        return ctx.author == m.author

    try:
        await ctx.send(f"What do you want to set the new max courses to (>= {len(db.get_all_courses_info(user.id))})")
        msg = await bot.wait_for("message", check=user_check, timeout=30)

        if db.update_max_courses(user.id, int(msg.content)):
            await ctx.send(f"{user.name}'s max courses set to {msg.content}")
        else:
            await ctx.send("Please enter a valid max courses")
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you did not reply in time")

"""
Command
show_courses

Displays the all the courses
a user has
"""
@bot.command()
async def show_courses(ctx):
    courses = [course_info["course_id"] for course_info in db.get_all_courses_info(ctx.author.id)]

    if not courses:
        await ctx.send("You have no courses in your schedule")
        return

    embed = discord.Embed(
        title = f"{ctx.author.name}'s Schedule",
        color = discord.Color.blue()
    )
    for course_info in db.get_all_courses_info(ctx.author.id):
        embed.add_field(
            name = f"{course_info['course_id']} - {course_info['course_name']} with {course_info['professor']}",
            value = f"{course_info['days_of_week']}\n{course_info['time']} in {course_info['location']}",
            inline = False
        )
    await ctx.author.send(embed = embed)

"""
Command
add_course

Prompts the user for inputs
about course info and adds the
course to the database
"""
@bot.command()
async def add_course(ctx):
    if len(db.get_all_courses_info(ctx.author.id)) == db.get_max_courses(ctx.author.id):
        await ctx.send("You have reached the max amount of courses you can add\nContact vietcoffee#9511 if you need to increase your max courses")
        return

    course_info = {
        "course_id":"",
        "course_name":"",
        "days_of_week":"",
        "time":"",
        "location":"",
        "professor":""
    }

    def user_check(m):
        return ctx.author == m.author

    def course_id_check(m):
        return re.search("^[A-Z]{2,4}\d{3}$", m.content) is not None

    def days_of_week_check(m):
        return re.search("^(MON)?(TUE)?(WED)?(THU)?(FRI)?$", m.content) is not None

    def time_check(m):
        return re.search("^(0?[1-9]|1[0-2]):[0-5][0-9][Aa|Pp][Mm]$", m.content) is not None

    try:
        # course_id
        await ctx.send("What is the course ID?\nXXXXNNN (i.e. CMSC202)")
        msg = await bot.wait_for("message", check=lambda m:course_id_check(m) and user_check(m), timeout=30)
        course_info["course_id"] = msg.content

        # course_name
        await ctx.send("What is the name of the course?")
        msg = await bot.wait_for("message", check=user_check, timeout=30)
        course_info["course_name"] = msg.content
        
        # days_of_week
        full_day = {
            "MON":"Monday",
            "TUE":"Tuesday",
            "WED":"Wednesday",
            "THU":"Thursday",
            "FRI":"Friday"
        }
        await ctx.send("What days of the week do you have the course?\nEnter from [MON,TUE,WED,THU,FRI] no duplicates or spaces, in-order (i.e. MONWEDFRI)")
        msg = await bot.wait_for("message", check=lambda m:days_of_week_check(m) and user_check(m), timeout=30)
        course_info["days_of_week"] = ' '.join([full_day[j] for j in [msg.content[i:i + 3] for i in range(0, len(msg.content), 3)]])

        # time
        time = ""
        await ctx.send("What is the start time of the course?\nHH:MM(AM/PM) (i.e. 11:30AM)")
        msg = await bot.wait_for("message", check=lambda m:time_check(m) and user_check(m), timeout=30)
        time += msg.content + "-"
        await ctx.send("What is the end time of the course?\nHH:MM(AM/PM) (i.e. 11:30AM)")
        msg = await bot.wait_for("message", check=lambda m:time_check(m) and user_check(m), timeout=30)
        time += msg.content
        course_info["time"] = time.upper()

        # location
        await ctx.send("Where is the course located?")
        msg = await bot.wait_for("message", check=user_check, timeout=30)
        course_info["location"] = msg.content

        # professor
        await ctx.send("What is the name of the professor?")
        msg = await bot.wait_for("message", check=user_check, timeout=30)
        course_info["professor"] = msg.content

        if db.add_course(ctx.author.id, course_info):
            await ctx.send("Course added successfully")
        else:
            await ctx.send("Failed to add course")
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you did not reply in time")

"""
Command
remove_course

Prompts the user to select
the course they would like 
to remove
"""
@bot.command()
async def remove_course(ctx):
    courses = [course_info["course_id"] for course_info in db.get_all_courses_info(ctx.author.id)]

    if not courses:
        await ctx.send("You have no courses in your schedule")
        return

    embed = discord.Embed(
        color = discord.Color.fuchsia()
    )
    embed.title = f"{ctx.author.name}, enter the course ID you want to remove"
    embed.description = "\n".join(courses)
    await ctx.send(embed = embed)

    def check(m):
        return m.content in courses and m.author == ctx.author

    try:
        msg = await bot.wait_for("message", check=check, timeout=30)
        if db.remove_course(ctx.author.id, msg.content):
            await ctx.send(f"{msg.content} has been removed")
        else:
            await ctx.send(f"Failed to remove {msg.content}")
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you did not reply in time")

"""
Command
update_course

Prompts the user to select a course
to update and what column of info
they would like to update
"""
@bot.command()
async def update_course(ctx):
    courses = [course_info["course_id"] for course_info in db.get_all_courses_info(ctx.author.id)]
    schedule_columns = [column[0] for column in db.get_table_columns("schedules")]

    if not courses:
        await ctx.send("You have no courses in your schedule")
        return

    def user_check(m):
        return m.author == ctx.author

    def course_id_check(m):
        return m.content in courses

    def column_check(m):
        return m.content in schedule_columns

    def column_value_check(m, column_name):
        if column_name == "course_id":
            return re.search("^[A-Z]{2,4}\d{3}$", m.content) is not None
        elif column_name == "days_of_week":
            return re.search("^(MON)?(TUE)?(WED)?(THU)?(FRI)?$", m.content) is not None
        elif column_name == "time":
            return re.search("^(0?[1-9]|1[0-2]):[0-5][0-9][Aa|Pp][Mm]-(0?[1-9]|1[0-2]):[0-5][0-9][Aa|Pp][Mm]$", m.content) is not None
        else:
            return True
    try:
        embed = discord.Embed(
            title = "Enter the course ID of the course you would like to edit",
            description = "\n".join(courses),
            color = discord.Color.fuchsia()
        )
        await ctx.send(embed=embed)
        course_id = await bot.wait_for("message", check=lambda m:course_id_check(m) and user_check(m), timeout=30)
        
        embed = discord.Embed(
            title = "Which column would you like to update",
            description = "\n".join(schedule_columns),
            color = discord.Color.fuchsia()
        )
        await ctx.send(embed = embed)
        column_name = await bot.wait_for("message", check=lambda m:column_check(m) and user_check(m), timeout=30)

        embed = discord.Embed(
            title = "What is the new column value",
            description = f"Old column value: {db.get_all_courses_info(ctx.author.id)[courses.index(course_id.content)][column_name.content]}",
            color = discord.Color.fuchsia()
        )
        if column_name.content == "course_id":
            embed.description += "\n\nXXXXNNN (i.e. CMSC202)"
        elif column_name.content == "days_of_week":
            embed.description += "\n\nSelect from [MON,TUE,WED,THU,FRI] (i.e. MONWEDFRI)"
        elif column_name.content == "time":
            embed.description += "\n\nHH:MM(AM/PM)-HH:MM(AM/PM)"
        await ctx.send(embed=embed)
        column_value = await bot.wait_for("message", check=lambda m:column_value_check(m, column_name.content) and user_check(m), timeout=30)

        db.update_course(ctx.author.id, course_id.content, column_name.content, column_value.content)
        await ctx.send(f"Successfully updated the '{column_name.content}' column with the new value")
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you did not reply in time")

bot.run(token)