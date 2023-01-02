import discord
from discord.ext import commands
from pathlib import Path
import assets.userinfodb as db

class Extra(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    Command
    help

    Overrided help function
    """
    @commands.command()
    async def help(self, ctx):
        file = discord.File(Path("assets") / "thumbnail2.png")
        embed = discord.Embed(
            title="ScheduleBot Commands",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url="attachment://thumbnail2.png")
        embed.add_field(name="All Users", value="boop\nboob\nshow_courses\nview_user_courses\nadd_course\nremove_course\nupdate_course\n", inline=False)
        embed.add_field(name="Admin", value="show_all_members\nadd_all_users\nupdate_max_courses\nwipe_user_messages_from\n", inline=False)
        await ctx.send(file=file, embed=embed)

    """
    Command
    boop

    Boop!
    """
    @commands.command()
    async def boop(self, ctx):
        db.increment_boops(ctx.author.id)
        await ctx.send(f"Boop!\nYou have booped a total of {db.get_boops(ctx.author.id)} boops")

    """
    Command
    boob

    Boob!
    """
    @commands.command()
    async def boob(self, ctx):
        await ctx.send(f"{ctx.author.name} touched some boobs")

async def setup(bot):
    await bot.add_cog(Extra(bot))