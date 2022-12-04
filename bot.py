import discord
from discord.ext import commands
import re
import asyncio
from pathlib import Path
import userinfodb as db

prefix = "-"
token = open(Path("assets/") / "token.txt", "r").readline().strip()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=prefix, intents=intents)

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

@bot.command()
async def boop(ctx):
    await ctx.send("Boop!")

# (ADMIN) display all users
@bot.command()
async def all_members(ctx):
    if ctx.author.guild_permissions.administrator:
        embed = discord.Embed(
            color = discord.Color.fuchsia()
        )
        embed.title = "Members List"
        members = ""
        for member in ctx.channel.guild.members:
            members += f"{member.name}#{member.discriminator} - {member.id} - is_bot:{member.bot}\n"
        embed.description = members
        await ctx.send(embed=embed)

# (ADMIN) add all users info to db
@bot.command()
async def add_all_users(ctx):
    if ctx.author.guild_permissions.administrator:
        pass

# create entry for user info in db
@bot.event
async def on_member_join(member):
    user_info = {
        "name":member.name,
        "discriminator":member.discriminator,
        "discord_id":member.id
    }
    if db.add_user(user_info):
        print(f"Added {member.name}'s info to the database")
    else:
        print("User already exists")

# update user info in db
@bot.event
async def on_member_update(member):
    pass

# idfk yet, delete user info?
@bot.event
async def on_member_remove(member):
    pass

# display classes
@bot.command()
async def classes(ctx):
    class_list = []
    for entry in db.get_all_classes(ctx.author.id):
        class_info = {
            "course_id":entry[1],
            "course_name":entry[2],
            "days_of_week":entry[3],
            "time":entry[4],
            "location":entry[5],
            "professor":entry[6]
        }
        class_list.append(class_info)
    for each_class in class_list:
        embed = discord.Embed(
            color = discord.Color.fuchsia()
        )
        embed.title = each_class["course_name"]
        # embed.set_thumbnail(url = Path("assets/") / "thumbnail.png")
        embed.add_field(name = "Course ID", value = each_class["course_id"])
        embed.add_field(name = "Days", value = each_class["days_of_week"])
        embed.add_field(name = "Time", value = each_class["time"])
        embed.add_field(name = "Location", value = each_class["location"])
        await ctx.send(embed = embed)

# add a class
@bot.command()
async def add_class(ctx):
    class_info = {
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
        return re.search("^[A-Z]{0,4}\d{3}$", m.content) is not None

    def days_of_week_check(m):
        return re.search("^(MON)?(TUE)?(WED)?(THU)?(FRI)?$", m.content) is not None

    def time_check(m):
        return re.search("^(0?[1-9]|1[0-2]):[0-5][0-9][A|P]M$", m.content) is not None

    try:
        # course_id
        await ctx.send("What is the course ID?")
        await ctx.send("XXXXNNN Up to 4 capital characters and exactly 3 numbers (i.e. CMSC202)")
        msg = await bot.wait_for("message", check=lambda m:course_id_check(m) and user_check(m), timeout=30)
        class_info["course_id"] = msg.content

        # course_name
        await ctx.send("What is the name of the course?")
        msg = await bot.wait_for("message", check=user_check, timeout=30)
        class_info["course_name"] = msg.content

        # days_of_week
        await ctx.send("What days of the week do you have the class?")
        await ctx.send("Enter from [MON,TUE,WED,THU,FRI] no duplicates or spaces, in-order (i.e. MONWEDFRI)")
        msg = await bot.wait_for("message", check=lambda m:days_of_week_check(m) and user_check(m), timeout=30)
        class_info["days_of_week"] = " ".join([j.title() for j in [msg.content[i:i + 3] for i in range(0, len(msg.content), 3)]])

        # time
        time = ""
        await ctx.send("What is the start time of the class?")
        await ctx.send("HH:MM and AM/PM (i.e. 11:30AM)")
        msg = await bot.wait_for("message", check=lambda m:time_check(m) and user_check(m), timeout=30)
        time += msg.content + "-"
        await ctx.send("What is the end time of the class?")
        await ctx.send("HH:MM and AM/PM (i.e. 12:45PM)")
        msg = await bot.wait_for("message", check=lambda m:time_check(m) and user_check(m), timeout=30)
        time += msg.content
        class_info["time"] = time

        # location
        await ctx.send("Where is the class located?")
        msg = await bot.wait_for("message", check=user_check, timeout=30)
        class_info["location"] = msg.content

        # professor
        await ctx.send("What is the name of the professor?")
        msg = await bot.wait_for("message", check=user_check, timeout=30)
        class_info["professor"] = msg.content
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you did not reply in time")

    if db.add_class(ctx.author.id, class_info):
        await ctx.send("Class added successfully")
    else:
        await ctx.send("Failed to add class")

# remove a class
@bot.command()
async def remove_class(ctx):
    pass

# update a class
@bot.command()
async def update_class(ctx):
    pass

bot.run(token)