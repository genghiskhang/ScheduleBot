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

@bot.command()
async def add_class(ctx):
    class_info = []

    def user_check(m):
        return ctx.author == m.author

    def course_id_check(m):
        return re.search("^[A-Z]{0,4}\d{3}$", m.content) is not None

    def days_of_week_check(m):
        return re.search("^(MON)?(TUE)?(WED)?(THU)?(FRI)?$", m.content) is not None

    def time_check(m):
        return re.search("^(0?[1-9]|1[0-2]):[0-5][0-9][A|P]M$", m.content) is not None

    try:
        # # course_id
        await ctx.send("What is the course ID?")
        await ctx.send("XXXXNNN Up to 4 capital characters and exactly 3 numbers (i.e. CMSC202)")
        msg = await bot.wait_for("message", check=lambda m:course_id_check(m) and user_check(m), timeout=30)
        class_info.append(msg)

        # course_name
        await ctx.send("What is the name of the course?")
        msg = await bot.wait_for("message", check=user_check, timeout=30)
        class_info.append(msg)

        # days_of_week
        await ctx.send("What days of the week do you have the class?")
        await ctx.send("Enter from [MON,TUE,WED,THU,FRI] no duplicates or spaces, in-order (i.e. MONWEDFRI)")
        msg = await bot.wait_for("message", check=lambda m:days_of_week_check(m) and user_check(m), timeout=30)
        class_info.append(msg)

        # time
        await ctx.send("What is the start time of the class?")
        await ctx.send("HH:MM and AM/PM (i.e. 11:30AM)")
        msg = await bot.wait_for("message", check=lambda m:time_check(m) and user_check(m), timeout=30)
        class_info.append(msg)
        await ctx.send("What is the end time of the class?")
        await ctx.send("HH:MM and AM/PM (i.e. 12:45PM)")
        msg = await bot.wait_for("message", check=lambda m:time_check(m) and user_check(m), timeout=30)
        class_info.append(msg)

        # location
        await ctx.send("Where is the class located?")
        msg = await bot.wait_for("message", check=user_check, timeout=30)
        class_info.append(msg)

        # professor
        await ctx.send("What is the name of the professor?")
        msg = await bot.wait_for("message", check=user_check, timeout=30)
        class_info.append(msg)
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you did not reply in time")

    db.add_class(ctx.author.id, class_info)

bot.run(token)