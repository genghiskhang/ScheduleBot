import discord
from discord.ext import commands
import asyncio
from pathlib import Path

token = open(Path("assets/") / "token.txt", "r").readline().strip()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="-", intents=intents)
bot.remove_command("help")

"""
Event
on_ready

Bot initialization
"""
@bot.event
async def on_ready():
    print(" ____                        __                \n"+
          "/\  _`\                     /\ \               \n"+
          "\ \ \L\ \     __     __     \_\ \  __  __      \n"+
          " \ \ ,  /   /\"__`\ /\"__`\   /\"_` \/\ \/\ \  \n"+
          "  \ \ \ \  /\  __//\ \L\.\_/\ \L\ \ \ \_\ \    \n"+
          "   \ \_\ \_\ \____\ \__/.\_\ \___,_\/`____ \   \n"+
          "    \/_/\/ /\/____/\/__/\/_/\/__,_ /`/___/> \\ \n"+
          "                                       /\___/  \n"+
          "                                       \/__/   \n")

async def main():
    await bot.load_extension("cogs.admin")
    await bot.load_extension("cogs.courses")
    await bot.load_extension("cogs.extra")
    await bot.start(token)

asyncio.run(main())